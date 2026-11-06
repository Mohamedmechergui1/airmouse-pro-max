# AIRMOUSE PRO MAX PRESENTATION

Application de contrôle par gestes de la main, avec une webcam, pour piloter le curseur et les présentations PowerPoint.

## Fonctionnalités

- **Déplacer le curseur** : présenter une main ouverte devant la caméra et la déplacer.
- **Cliquer** : rapprocher le pouce et l'index.
- **Zoomer dans PowerPoint** : écarter les deux mains pour zoomer, les rapprocher pour dézoomer. PowerPoint doit être la fenêtre active.
- **Changer de diapositive** : pendant un diaporama, replier le pouce et garder les quatre autres doigts tendus :
  - balayer de droite à gauche avec la main droite pour afficher la diapositive suivante ;
  - balayer de gauche à droite avec la main gauche pour revenir à la diapositive précédente.

Le suivi de la caméra est effectué localement par MediaPipe. Une webcam est nécessaire. Les gestes de navigation PowerPoint envoient des touches au système ; gardez la fenêtre voulue au premier plan.

## Prérequis

- Windows
- Python 3.11
- Une webcam
- PowerPoint pour les gestes de zoom et de navigation

Le fichier `hand_landmarker.task`, nécessaire au suivi des mains, est fourni avec le projet.

## Installation et lancement

Ouvrir PowerShell dans le dossier du projet, puis exécuter :

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

Dans l'application, choisir la caméra puis cliquer sur **Start tracking**. Autoriser l'accès à la caméra si Windows le demande.

## Tests

```powershell
.\.venv\Scripts\python.exe -m unittest -v test_app
```

## Publication et licence

Le fichier `hand_landmarker.task` est un modèle tiers : vérifier ses conditions de redistribution avant de publier le projet. Aucune licence logicielle n'a encore été choisie pour ce projet ; en ajouter une avant d'autoriser explicitement la réutilisation ou la redistribution du code.
