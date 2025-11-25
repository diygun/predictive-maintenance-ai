# Step 05 - Entraînement du CNN

Ce fichier décrit l'étape 05 du projet : l'entraînement d'un réseau de neurones convolutif (CNN).

## Contenu

- **Objectif** : Former un modèle CNN pour analyser les données et prédire les défaillances.
- **Fichiers principaux** :
    - `cnn_training.ipynb` : Notebook pour l'entraînement et sauvegarde du modèle CNN
    - `timestamp_validation_res_XX.XX_test_set_YY.YY.h5` : Modèles sauvegardés avec performances

- **Dépendances** :
    - TensorFlow / PyTorch
    - NumPy, Pandas
    - Matplotlib (pour la visualisation)

## Instructions

1. Pour lancer l'entrainement, on utilise un conteneur Docker afin d'utiliser une carte graphique pour accélérer l'entrainement.
```bash
docker run --gpus all -it --rm -v .:/tf -p 8888:8888 tensorflow/tensorflow:2.15.0-gpu-jupyter
```

- `--gpus all` permet d'utiliser toute la puissance de calcule du/des GPU.
- `-v .:/tf` avec . qui est la racine du projet monté au dossier tensorflow
- `tensorflow/tensorflow:2.15.0-gpu-jupyter` l'image avec l'environnement

Cette commande vous donnera en sortie (après quelques logs) une URL de ce type :

```bash
[I 2025-11-25 22:26:34.411 ServerApp]     http://127.0.0.1:8888/tree?token=fd8710e631861c5d49e1c54c625273b58ab80bdbe71dc023
```
- Vous pouvez utiliser cette url depuis un autre appareil du réseau à condition de remplacer l'IP.

Avec cette URL l'interface de Jupyter sera accessible via le navigateur et avec la puissance de calcul du GPU.

Nous avons opté pour cette solution conteneurisée car elle permet d'éviter tout problème de dépendance.


## Notes

Attention à ce que les données soient correctement préparées dans les étapes précédentes avant de lancer cet entraînement.

## Conclusion - Avis sur le modèle et les performances

Au début j'avais utilisé les spectrogrammes X, Y, Z en tant qu'entrées distinctes. J'ai eu des super performances avec peu d'itérations. 10 époques, 95% avec le test set.

Puis en utilisant les 3 axes en tant qu'entrée unique (fusionnés en une seule image avec trois canaux R, G, B), les performances sont inférieures (environ 75% sur le test set après 10 époques). Malgré des résultats moins bons, je pense que le modèle ne surprendra pas et donc il devrait mieux généraliser sur des données réelles.
