"""
gui.py
Interface graphique tkinter : permet de choisir une application cible,
définir des raccourcis clavier personnalisés et les déclencher via des boutons.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from keycombo import config_manager, keysender


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("KeyCombo — Raccourcis vers une seule application")
        self.geometry("480x520")
        self.resizable(False, False)

        self.config_data = config_manager.load_config()

        self._build_target_section()
        self._build_mode_section()
        self._build_shortcuts_section()

        self.refresh_target_label()
        self.refresh_shortcuts_list()

    # ---------- Section : application cible ----------
    def _build_target_section(self):
        frame = ttk.LabelFrame(self, text="Application cible")
        frame.pack(fill="x", padx=10, pady=10)

        self.target_label = ttk.Label(frame, text="Aucune application choisie")
        self.target_label.pack(side="left", padx=10, pady=10)

        ttk.Button(
            frame, text="Choisir l'application...", command=self.choose_target
        ).pack(side="right", padx=10, pady=10)

    def refresh_target_label(self):
        exe = self.config_data.get("target_exe")
        title = self.config_data.get("target_title")
        if exe:
            self.target_label.config(text=f"{title}  ({exe})")
        else:
            self.target_label.config(text="Aucune application choisie")

    def choose_target(self):
        windows = keysender.list_windows()
        if not windows:
            messagebox.showerror("Erreur", "Aucune fenêtre détectée.")
            return

        picker = tk.Toplevel(self)
        picker.title("Choisir une application")
        picker.geometry("420x400")

        listbox = tk.Listbox(picker, width=60, height=20)
        listbox.pack(padx=10, pady=10, fill="both", expand=True)

        for hwnd, title, exe in windows:
            listbox.insert("end", f"{title}   —   {exe}")

        def confirm():
            sel = listbox.curselection()
            if not sel:
                return
            hwnd, title, exe = windows[sel[0]]
            self.config_data["target_exe"] = exe
            self.config_data["target_title"] = title
            config_manager.save_config(self.config_data)
            self.refresh_target_label()
            picker.destroy()

        ttk.Button(picker, text="Sélectionner", command=confirm).pack(pady=5)

    # ---------- Section : mode d'envoi ----------
    def _build_mode_section(self):
        frame = ttk.LabelFrame(self, text="Mode d'envoi des touches")
        frame.pack(fill="x", padx=10, pady=(0, 10))

        self.mode_var = tk.StringVar(value=self.config_data.get("mode", "focus"))

        ttk.Radiobutton(
            frame, text="Focus automatique (recommandé, fonctionne partout)",
            variable=self.mode_var, value="focus", command=self.save_mode
        ).pack(anchor="w", padx=10, pady=2)

        ttk.Radiobutton(
            frame, text="Sans changer le focus (PostMessage, apps compatibles seulement)",
            variable=self.mode_var, value="postmessage", command=self.save_mode
        ).pack(anchor="w", padx=10, pady=2)

    def save_mode(self):
        self.config_data["mode"] = self.mode_var.get()
        config_manager.save_config(self.config_data)

    # ---------- Section : raccourcis ----------
    def _build_shortcuts_section(self):
        frame = ttk.LabelFrame(self, text="Raccourcis")
        frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.shortcuts_frame = ttk.Frame(frame)
        self.shortcuts_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Button(
            frame, text="+ Ajouter un raccourci", command=self.add_shortcut
        ).pack(pady=(0, 10))

    def refresh_shortcuts_list(self):
        for widget in self.shortcuts_frame.winfo_children():
            widget.destroy()

        shortcuts = self.config_data.get("shortcuts", [])
        if not shortcuts:
            ttk.Label(self.shortcuts_frame, text="Aucun raccourci défini.").pack()
            return

        for i, sc in enumerate(shortcuts):
            row = ttk.Frame(self.shortcuts_frame)
            row.pack(fill="x", pady=3)

            combo_text = " + ".join(sc["keys"])
            btn = ttk.Button(
                row, text=f"{sc['name']}  ({combo_text})",
                command=lambda s=sc: self.trigger_shortcut(s)
            )
            btn.pack(side="left", fill="x", expand=True)

            ttk.Button(
                row, text="Suppr.", width=7,
                command=lambda idx=i: self.delete_shortcut(idx)
            ).pack(side="right", padx=(5, 0))

    def add_shortcut(self):
        name = simpledialog.askstring("Nom du raccourci", "Nom (ex: Sauvegarder) :")
        if not name:
            return
        combo = simpledialog.askstring(
            "Combinaison de touches",
            "Touches séparées par des '+' (ex: ctrl+shift+s) :"
        )
        if not combo:
            return

        keys = [k.strip() for k in combo.split("+") if k.strip()]
        try:
            for k in keys:
                keysender.key_to_vk(k)  # valide que chaque touche est reconnue
        except ValueError as e:
            messagebox.showerror("Touche invalide", str(e))
            return

        self.config_data.setdefault("shortcuts", []).append({"name": name, "keys": keys})
        config_manager.save_config(self.config_data)
        self.refresh_shortcuts_list()

    def delete_shortcut(self, idx):
        del self.config_data["shortcuts"][idx]
        config_manager.save_config(self.config_data)
        self.refresh_shortcuts_list()

    def trigger_shortcut(self, shortcut):
        exe = self.config_data.get("target_exe")
        if not exe:
            messagebox.showwarning("Aucune cible", "Choisissez d'abord une application cible.")
            return

        hwnd = keysender.find_hwnd_by_exe(exe)
        if not hwnd:
            messagebox.showerror(
                "Introuvable", f"L'application '{exe}' ne semble pas ouverte actuellement."
            )
            return

        try:
            if self.config_data.get("mode", "focus") == "postmessage":
                keysender.send_combo_via_postmessage(hwnd, shortcut["keys"])
            else:
                keysender.send_combo_via_focus(hwnd, shortcut["keys"])
        except Exception as e:
            messagebox.showerror("Erreur d'envoi", str(e))
