"""
config_manager.py
Charge et sauvegarde la configuration (application cible + liste des raccourcis)
dans un fichier JSON, stocké dans le dossier de données utilisateur.
"""

import json
import os

APP_DIR_NAME = "KeyCombo"


def _config_dir() -> str:
    base = os.environ.get("APPDATA") or os.path.expanduser("~")
    path = os.path.join(base, APP_DIR_NAME)
    os.makedirs(path, exist_ok=True)
    return path


CONFIG_FILE = os.path.join(_config_dir(), "config.json")

DEFAULT_CONFIG = {
    "target_exe": None,
    "target_title": None,
    "mode": "focus",  # "focus" ou "postmessage"
    "shortcuts": []   # [{"name": "Sauvegarder", "keys": ["ctrl", "s"]}, ...]
}


def load_config() -> dict:
    if not os.path.exists(CONFIG_FILE):
        return dict(DEFAULT_CONFIG)
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        merged = dict(DEFAULT_CONFIG)
        merged.update(data)
        return merged
    except Exception:
        return dict(DEFAULT_CONFIG)


def save_config(config: dict) -> None:
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
