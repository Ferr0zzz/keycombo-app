# KeyCombo

Application Windows avec interface graphique permettant de :
- choisir **une seule application** cible sur le PC,
- définir des combinaisons de touches personnalisées,
- les déclencher via des boutons, même si l'application cible n'est pas au
  premier plan.

## Structure du projet

```
keycombo-app/
├── src/
│   └── keycombo/
│       ├── __init__.py
│       ├── __main__.py       # point d'entrée (python -m keycombo)
│       ├── gui.py            # interface tkinter
│       ├── keysender.py      # détection de fenêtres + envoi des touches
│       └── config_manager.py # sauvegarde/chargement de la config
├── pyproject.toml
├── requirements.txt
├── .gitignore
├── LICENSE
└── README.md
```

## Prérequis

- Windows (utilise l'API Win32 via `pywin32`)
- Python 3.9+

## Installation (environnement virtuel)

```bash
# Cloner le dépôt
git clone https://github.com/<votre-user>/keycombo-app.git
cd keycombo-app

# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement virtuel
# PowerShell :
venv\Scripts\Activate.ps1
# Invite de commandes (cmd.exe) :
venv\Scripts\activate.bat

# Installer les dépendances
pip install -r requirements.txt

# Installer le projet en mode développement (optionnel mais recommandé)
pip install -e .
```

## Lancer l'application

```bash
# Si installé avec pip install -e .
keycombo

# Sinon, directement :
python -m keycombo
```

## Utilisation

1. **Choisir l'application** : cliquez sur "Choisir l'application...", une
   liste des fenêtres actuellement ouvertes s'affiche, sélectionnez la vôtre.
2. **Ajouter un raccourci** : cliquez sur "+ Ajouter un raccourci", donnez-lui
   un nom (ex : "Sauvegarder") et la combinaison de touches, séparée par des
   `+` (ex : `ctrl+shift+s`, `alt+f4`, `f5`).
3. **Déclencher** : cliquez sur le bouton du raccourci créé. KeyCombo retrouve
   la fenêtre de l'application cible et lui envoie la combinaison.

La configuration (application cible + raccourcis) est sauvegardée
automatiquement dans `%APPDATA%\KeyCombo\config.json`.

## Les deux modes d'envoi

- **Focus automatique (recommandé)** : KeyCombo active brièvement la fenêtre
  cible, envoie les vraies touches, puis remet immédiatement le focus sur
  votre fenêtre précédente. Quasi instantané, fonctionne avec la grande
  majorité des applications (y compris les jeux).
- **Sans changer le focus (PostMessage)** : KeyCombo envoie les messages de
  touches directement à la fenêtre cible sans jamais l'activer. Plus discret,
  mais ne fonctionne que sur certaines applications Win32 classiques (beaucoup
  d'applications modernes, jeux ou apps DirectX ignorent ces messages
  simulés).

Si un raccourci ne fonctionne pas en mode "Sans changer le focus", basculez
sur "Focus automatique" dans l'interface.

## Touches reconnues

Lettres et chiffres (`a`-`z`, `0`-`9`), modificateurs (`ctrl`, `shift`, `alt`,
`win`), touches spéciales (`enter`, `tab`, `esc`, `space`, `backspace`,
`delete`, `up`, `down`, `left`, `right`, `home`, `end`, `pageup`, `pagedown`,
`f1` à `f12`).

## Limites connues

- Windows uniquement.
- Certains jeux protégés (anti-triche) ou applications élevées ("exécuter en
  administrateur") peuvent bloquer l'envoi de touches simulées si KeyCombo
  n'est pas lui-même lancé en administrateur.
- Si l'application cible se ferme et se rouvre, KeyCombo la retrouve
  automatiquement via son nom d'exécutable (`.exe`), pas besoin de la
  re-sélectionner.

## Licence

MIT — voir [LICENSE](LICENSE).
