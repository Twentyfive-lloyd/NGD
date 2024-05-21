import os
import subprocess

# Définissez votre répertoire local du dépôt Git
repo_dir = "/root/NGD"

# Changez de répertoire pour le répertoire Git
os.chdir(repo_dir)

# Ajoutez les fichiers
subprocess.run(["git", "add", "."])

# Créez un commit avec un message
commit_message = "Mise à jour automatique"
subprocess.run(["git", "commit", "-m", commit_message])

# Poussez les changements vers le dépôt GitHub
subprocess.run(["git", "push", "origin", "master"])
