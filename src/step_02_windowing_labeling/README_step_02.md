# Étape 02 – Fenêtrage et étiquetage

## Entrées
- `data/02_merged/PI-donnee-saine/PI-donnee-saine_output.csv`
- `data/02_merged/PI-donnee-balourd/PI-donnee-balourd_output.csv`

Ces fichiers sont générés par l'étape 01 (fusion + alignement)

## Ce que fait l'étape 02
- découpe les signaux en fenêtres de 2 secondes avec 50% de recouvrement
- crée un label pour chaque fenêtre :
  - 0 = sain
  - 1 = balourd
- produit un jeu de données prêt pour l'étape 03 (STFT / spectrogrammes)

## En détail 
Pour l’étape 2 je me suis occupée du fenêtrage, de l’échantillonnage et de l’étiquetage des données

On part des fichiers fusionnés de l’étape 1 :
data/02_merged/PI-donnee-saine/PI-donnee-saine_output.csv 
et data/02_merged/PI-donnee-balourd/PI-donnee-balourd_output.csv

Chaque fichier contient une colonne date et 6 signaux : ax_vibration_ms2, ay_vibration_ms2, az_vibration_ms2, gx_vibration_gx, gy_vibration_gy, gz_vibration_gz + le hall switch

Dans mon code je convertis date en un temps relatif en secondes (time_s) et je trie les mesures dans l’ordre chronologique

Ensuite j’applique un fenêtrage de 2 secondes avec 50 % de recouvrement sur les 6 signaux de vibration

Les fenêtres générées à partir des données saines reçoivent le label 0, celles générées à partir des données balourd (déséquilibrées) reçoivent le label 1

Au final on obtient 551 fenêtres saines et 246 fenêtres balourd, soit 797 fenêtres de taille (400 échantillons, 6 canaux)

Je sauvegarde les résultats dans data/03_windowed/ :
- X_windows.npy : tableau des fenêtres (shape = 797 × 400 × 6)
- y_labels.npy : labels associés (0 = sain, 1 = balourd)
- windows_summary.csv : résumé des labels
Ces fichiers servent d’entrée à l’étape suivante qui va transformer chaque fenêtre en image (spectrogramme) pour entraîner le CNN