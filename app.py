import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
import customtkinter as ctk
from PIL import Image, ImageTk
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

from src.engine_a.segmentation import segment_damage
from src.engine_a.measurement import estimate_from_reference
from src.engine_a.pricing import estimate_cost, init_db
from src.engine_b.pattern_analysis import analyze_burn_patterns
from src.engine_b.inconsistency import detect_inconsistencies
from src.engine_b.red_flag import RedFlagSystem


class InsuranceAdjusterApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AI Insurance Adjuster")
        self.geometry("1100x720")
        self.minsize(900, 600)

        init_db()

        self.image_path = None
        self.photo = None
        self.result = None

        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        main = ctk.CTkFrame(self)
        main.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main.grid_columnconfigure(1, weight=1)
        main.grid_rowconfigure(0, weight=1)

        # ─── Left: Image + Controls ───
        left = ctk.CTkFrame(main, width=400)
        left.grid(row=0, column=0, sticky="nswe", padx=(0, 8))
        left.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(left, text="Damage Image", font=("Segoe UI", 14, "bold")).grid(
            row=0, column=0, pady=(8, 4)
        )

        self.img_label = ctk.CTkLabel(left, text="No image selected", width=380, height=300)
        self.img_label.grid(row=1, column=0, padx=8, pady=4, sticky="nsew")

        ctk.CTkButton(left, text="Browse Image", command=self._browse_image).grid(
            row=2, column=0, pady=(8, 4), padx=20, sticky="ew"
        )

        ctk.CTkLabel(left, text="Incident description (optional):", anchor="w").grid(
            row=3, column=0, padx=8, pady=(8, 0), sticky="ew"
        )
        self.desc_entry = ctk.CTkTextbox(left, height=60)
        self.desc_entry.grid(row=4, column=0, padx=8, pady=4, sticky="ew")

        ctk.CTkLabel(left, text="Damage type for cost estimate:", anchor="w").grid(
            row=5, column=0, padx=8, pady=(8, 0), sticky="ew"
        )
        self.material_var = ctk.StringVar(value="fire_damage_repair")
        material_combo = ctk.CTkComboBox(
            left,
            values=[
                "fire_damage_repair",
                "drywall",
                "flooring_wood",
                "roofing_shingle",
                "smoke_cleanup",
                "paint_interior",
            ],
            variable=self.material_var,
        )
        material_combo.grid(row=6, column=0, padx=8, pady=4, sticky="ew")

        self.analyze_btn = ctk.CTkButton(
            left, text="Analyze Damage", command=self._analyze, state="disabled"
        )
        self.analyze_btn.grid(row=7, column=0, pady=12, padx=20, sticky="ew")

        # ─── Right: Results ───
        right = ctk.CTkFrame(main)
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_rowconfigure(0, weight=1)
        right.grid_columnconfigure(0, weight=1)

        self.tabview = ctk.CTkTabview(right)
        self.tabview.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)

        self.tab_assessment = self.tabview.add("Damage Assessment")
        self.tab_fraud = self.tabview.add("Fraud Analysis")
        self.tab_cost = self.tabview.add("Cost Estimate")

        for t in [self.tab_assessment, self.tab_fraud, self.tab_cost]:
            t.grid_columnconfigure(0, weight=1)
            t.grid_rowconfigure(1, weight=1)

        # Assessment tab
        self.assessment_text = ctk.CTkTextbox(self.tab_assessment, wrap="word", state="disabled")
        self.assessment_text.grid(row=1, column=0, sticky="nsew", padx=8, pady=8)

        # Fraud tab
        self.fraud_text = ctk.CTkTextbox(self.tab_fraud, wrap="word", state="disabled")
        self.fraud_text.grid(row=1, column=0, sticky="nsew", padx=8, pady=8)

        # Cost tab
        self.cost_text = ctk.CTkTextbox(self.tab_cost, wrap="word", state="disabled")
        self.cost_text.grid(row=1, column=0, sticky="nsew", padx=8, pady=8)

        # ─── Status bar ───
        self.status_var = ctk.StringVar(value="Ready")
        self.status_bar = ctk.CTkLabel(
            self, textvariable=self.status_var, anchor="w", font=("Segoe UI", 10)
        )
        self.status_bar.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 6))

        self._progress = ctk.CTkProgressBar(self, height=4)
        self._progress.grid(row=2, column=0, sticky="ew", padx=10)
        self._progress.set(0)

    def _browse_image(self):
        path = filedialog.askopenfilename(
            title="Select damage image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")],
        )
        if not path:
            return
        self.image_path = path
        self.analyze_btn.configure(state="normal")
        self._show_thumbnail(path)
        self.status_var.set(f"Loaded: {Path(path).name}")

    def _show_thumbnail(self, path):
        img = Image.open(path)
        img.thumbnail((380, 300), Image.LANCZOS)
        self.photo = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
        self.img_label.configure(image=self.photo, text="")

    def _analyze(self):
        if not self.image_path:
            return
        self.analyze_btn.configure(state="disabled", text="Analyzing...")
        self._progress.set(0.2)
        self.status_var.set("Running analysis...")

        thread = threading.Thread(target=self._run_analysis, daemon=True)
        thread.start()

    def _run_analysis(self):
        try:
            seg = segment_damage(self.image_path)
            self.after(0, self._progress.set, 0.5)

            area = estimate_from_reference(seg["mask"], seg["objects"])
            self.after(0, self._progress.set, 0.7)

            description = self.desc_entry.get("1.0", "end-1l").strip()
            material = self.material_var.get()

            patterns = analyze_burn_patterns(seg["mask"])
            inconsistencies = detect_inconsistencies(description, seg["objects"])

            rf = RedFlagSystem()
            for p in patterns:
                rf.add_flag(p["type"], p["severity"], p["message"], p.get("confidence", 50))
            for inc in inconsistencies:
                rf.add_flag(inc["type"], inc["severity"], inc["message"], inc.get("confidence", 50))
            if not seg["fire_detections"] and not seg["smoke_detections"]:
                rf.add_flag("no_damage_detected", "low", "No fire/smoke damage detected in image.", 30)

            cost = estimate_cost(material, area) if area > 0 else None

            self.after(0, self._display_results, seg, area, rf, cost, patterns, inconsistencies)
        except Exception as e:
            self.after(0, self._show_error, str(e))

    def _display_results(self, seg, area, rf, cost, patterns, inconsistencies):
        self._progress.set(1.0)

        # Assessment
        self.assessment_text.configure(state="normal")
        self.assessment_text.delete("1.0", "end")
        self.assessment_text.insert("1.0", f"Fire detections: {len(seg['fire_detections'])}\n")
        self.assessment_text.insert("end", f"Smoke detections: {len(seg['smoke_detections'])}\n")
        self.assessment_text.insert("end", f"Damaged area: {area:.2f} m²\n")
        self.assessment_text.insert("end", f"Image size: {seg['original_shape']}\n\n")
        for i, f in enumerate(seg['fire_detections'], 1):
            self.assessment_text.insert("end", f"Fire #{i}: confidence {f['confidence']:.0%}\n")
        for i, s in enumerate(seg['smoke_detections'], 1):
            self.assessment_text.insert("end", f"Smoke #{i}: confidence {s['confidence']:.0%}\n")
        if seg["objects"]:
            self.assessment_text.insert("end", "\nOther objects:\n")
            for obj in seg["objects"][:10]:
                self.assessment_text.insert("end", f"  {obj['label']} ({obj['confidence']:.0%})\n")
        self.assessment_text.configure(state="disabled")

        # Fraud
        self.fraud_text.configure(state="normal")
        self.fraud_text.delete("1.0", "end")
        score = rf.compute_risk_score()
        self.fraud_text.insert("1.0", f"Risk Score: {score:.1%}\n")
        self.fraud_text.insert("end", f"Total flags: {rf.get_report()['total_flags']}\n")
        self.fraud_text.insert("end", f"High severity: {rf.get_report()['high_severity_count']}\n\n")
        for flag in rf.flags:
            icon = {"high": "[HIGH]", "medium": "[MED]", "low": "[LOW]"}
            self.fraud_text.insert(
                "end", f"{icon.get(flag['severity'], '[INFO]')} {flag['type']}\n"
            )
            self.fraud_text.insert("end", f"  {flag['message']}\n")
            self.fraud_text.insert("end", f"  Confidence: {flag['confidence']:.0f}%\n\n")
        self.fraud_text.configure(state="disabled")

        # Cost
        self.cost_text.configure(state="normal")
        self.cost_text.delete("1.0", "end")
        if cost:
            self.cost_text.insert("1.0", f"Category: {cost['category']}\n")
            self.cost_text.insert("end", f"Material: {cost['material']}\n")
            self.cost_text.insert("end", f"Area: {cost['area_m2']:.2f} m²\n")
            self.cost_text.insert("end", f"Material cost: €{cost['material_cost']:.2f}\n")
            self.cost_text.insert("end", f"Labor cost: €{cost['labor_cost']:.2f}\n")
            self.cost_text.insert("end", f"\nTotal estimate: €{cost['total_estimated']:.2f}\n")
        else:
            self.cost_text.insert("1.0", "No damage detected — cost estimate unavailable.\n")
        self.cost_text.configure(state="disabled")

        self.tabview.set("Damage Assessment")
        self.analyze_btn.configure(state="normal", text="Analyze Damage")
        self.status_var.set("Analysis complete")

    def _show_error(self, msg):
        self.analyze_btn.configure(state="normal", text="Analyze Damage")
        self._progress.set(0)
        self.status_var.set("Error")
        messagebox.showerror("Analysis Error", msg)


if __name__ == "__main__":
    app = InsuranceAdjusterApp()
    app.mainloop()
