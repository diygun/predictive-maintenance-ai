# Étape 04 – Normalisation et Génération des Images RGB pour CNN

## Entrées

  - `data/03_windowed/X_windows.npy`
  - `data/03_windowed/y_labels.npy`

> **Note :** Cette étape repart des données brutes de l'étape 02. Les images générées à l'étape 03 servaient uniquement à la validation visuelle humaine.

-----

## Ce que fait l’étape 04

  - **Nettoie le signal :** Suppression de la gravité (composante DC) et filtrage des fenêtres "mortes".
  - **Fusionne les axes :** Empile les spectrogrammes des axes vibration (Ax, Ay, Az) en une seule **image RGB** (3 canaux).
  - **Améliore la résolution temporelle :** Utilise un fort chevauchement (overlap) pour obtenir des images larges malgré la courte durée des fenêtres.
  - **Normalise :** Applique une normalisation robuste (percentiles) pour garantir un bon contraste.
  - **Structure :** Organise les images pour l'entraînement du modèle (dossier `05_cnn_input`).

-----

## En détail

Cette étape est critique pour transformer des séries temporelles brutes en "tenseurs" d'images optimisés pour un Réseau de Neurones Convolutif (CNN).

Contrairement à l'étape 03 (visualisation), l'objectif ici est de créer des données dense et normalisées pour la machine.

### 1\. Stratégie RGB (Ax, Ay, Az)

Au lieu de traiter chaque axe séparément, je crée une image composite où chaque couleur correspond à une direction physique :

  - **Canal Rouge (R)** 🔴 : Spectrogramme de l'axe **Ax**
  - **Canal Vert (G)** 🟢 : Spectrogramme de l'axe **Ay**
  - **Canal Bleu (B)** 🔵 : Spectrogramme de l'axe **Az**

Cela permet au CNN d'apprendre les corrélations spatiales entre les axes (ex: une vibration forte sur X mais faible sur Y crée une couleur spécifique).

### 2\. Corrections Techniques Appliquées

Pour résoudre les problèmes d'images noires ou trop étroites rencontrés précédemment, le pipeline applique les transformations suivantes :

#### A. Suppression de la Gravité (`signal.detrend`)

Les accéléromètres captent la gravité (9.81 m/s²), ce qui crée une composante continue énorme à 0Hz. Cela "écrasait" les vibrations utiles lors de la normalisation (rendant l'image noire).

  - **Solution :** Application d'un `detrend` avant la STFT pour centrer le signal sur 0 et ne garder que les vibrations.

#### B. Étirement Temporel (High Overlap)

Les fenêtres de 2 secondes (400 points) sont courtes par rapport à la taille de la FFT (256 points). Sans chevauchement, l'image ne ferait que 2 ou 3 pixels de large.

  - **Solution :** `noverlap = 252` (sur 256). On fait glisser la fenêtre d'analyse très doucement pour générer artificiellement une résolution temporelle (largeur d'image \~100px).

#### C. Normalisation Robuste

Au lieu d'une normalisation Min-Max classique (sensible aux pics de bruits isolés), j'utilise une normalisation par **Percentiles (2% - 99%)**.

  - **Résultat :** Le contraste est maximisé sur la partie utile du signal, rendant les harmoniques de balourd bien visibles.

#### D. Filtrage des Données Mortes

Certaines fenêtres issues de la fusion (étape 01) contenaient des signaux plats ou nuls.

  - **Action :** Le script rejette automatiquement toute fenêtre dont l'écart-type est `< 0.005`.

-----

## ⚙️ Paramètres de la STFT

```python
FS = 200.0 Hz        # Fréquence d'échantillonnage
N_FFT = 256          # Résolution fréquentielle (Hauteur image = 129px)
NOVERLAP = 252       # Chevauchement (Largeur image ~ 101px)
WINDOW = 'hann'      # Fenêtrage pour limiter les fuites spectrales
MODE = 'magnitude'   # Amplitude (convertie en dB)
```

-----

## 📊 Résultats

Les images finales sont des PNG couleur de taille **101 x 129 pixels**.

  - **Sain** : \~551 images (Texture bruitée, verticale, peu de lignes horizontales).
  - **Balourd** : \~246 images (Lignes horizontales distinctes correspondant à la fréquence de rotation et ses harmoniques).

-----

## 📁 Structure de sortie

Les données sont prêtes à être chargées par un `ImageDataGenerator` (Keras) ou `ImageFolder` (PyTorch).

```text
data/05_cnn_input/
├── sain/
│   ├── spec_rgb_0000.png
│   ├── spec_rgb_0001.png
│   └── ...
└── balourd/
    ├── spec_rgb_0554.png
    ├── spec_rgb_0555.png
    └── ...
```

## le script ```image_quality_check.ipynb```

### 1. Vérification de la Quantité et de l'Équilibre (`CHECK QUANTITY & BALANCE`)
* **Ce qu'il fait :** Il compte combien d'images vous avez dans le dossier `sain` et dans le dossier `balourd`.
* **Pourquoi c'est important :**
    * **Volume :** Le Deep Learning a besoin de beaucoup de données. Avec ~800 images au total, vous avez un dataset "petit mais suffisant" pour commencer.
    * **Équilibre (Balance) :** Si vous avez 1000 images "saines" et seulement 10 images "balourd", le modèle va tricher : il va toujours prédire "sain" et aura 99% de réussite, mais il sera inutile.
    * **Votre Résultat :** Vous avez un ratio de **1 Balourd pour 2.24 Sain**. C'est un déséquilibre modéré. Le script vous avertit que c'est "acceptable", mais cela signifie que lors de l'entraînement (Étape 05), nous devrons dire au modèle : *"Attention, les exemples de Balourd sont rares, donc si tu en vois un, accorde-lui plus d'importance (poids)"*.

### 2. Vérification des Dimensions et du Format (`CHECK DIMENSIONS & FORMAT`)
* **Ce qu'il fait :** Il ouvre une image au hasard et regarde sa taille (Largeur x Hauteur) et son mode de couleur (RGB).
* **Pourquoi c'est important :**
    * **L'Input du CNN :** Un réseau de neurones attend une entrée de taille fixe. Si vous lui donnez une image de taille (3, 129) alors qu'il attend du (101, 129), il plantera.
    * **Le bug de l'overlap :** C'est ce test qui nous aurait permis de détecter automatiquement le problème des "bandes verticales" que vous aviez tout à l'heure. Le script vérifie `width > 30` pour s'assurer que l'image contient bien de l'information temporelle.

### 3. Vérification du Contenu (`CHECK PIXEL VALUES`)
* **Ce qu'il fait :** Il prend 100 images au hasard, les transforme en tableau de nombres, et calcule la moyenne de leur luminosité. Si la moyenne est proche de 0 (tout noir), il sonne l'alarme.
* **Pourquoi c'est important :**
    * **Détecter les signaux morts :** Comme nous l'avons vu, une fenêtre temporelle où le capteur ne captait rien (ou juste la gravité constante) produisait une image noire après normalisation.
    * **Éviter la pollution :** Si on entraîne un modèle sur des images noires étiquetées "balourd", il va apprendre n'importe quoi.
    * **Votre Résultat :** "Aucune image noire détectée". Cela valide que votre correction avec `signal.detrend` et le filtre `std_val < 0.005` ont bien fonctionné.

### 4. Visualisation Comparative (`VISUALISATION COMPARATIVE`)
* **Ce qu'il fait :** Il affiche une grille d'exemples réels pour vos yeux.
* **Pourquoi c'est important :**
    * **L'intuition humaine :** L'algorithme ne "voit" pas comme nous. Cette étape permet de vérifier si *vous* (l'humain) arrivez à voir une différence.
    * **Les Motifs :** Dans vos résultats, on voit clairement que les images "Balourd" ont des lignes horizontales bien marquées (les fréquences de vibration du défaut), alors que les images "Sain" sont plus "bruitées" ou verticales. C'est la preuve visuelle que l'information pertinente est bien présente dans l'image.

En résumé, ce script vous donne le **feu vert officiel**. Vous savez maintenant que vos données sont **propres, lisibles, et différenciables**.