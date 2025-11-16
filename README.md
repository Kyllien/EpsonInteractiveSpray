# Epson Spray Paint - Graffiti Virtuel

Application de peinture spray virtuelle pour projecteur Epson avec stylo interactif.

## Installation

### Dépendances requises

```bash
pip install -r requirements.txt
```

### Lancement

```bash
python spray_paint_app.py
```

## Fonctionnalités

### Interface

L'application dispose de deux barres d'outils :

#### Barre supérieure (en haut à droite)
- 📁 **Charger fond** : Charge une image de fond plein écran
- 🖼️ **Charger modèle** : Charge une image modèle 1000x1000px à 30% d'opacité (centrée en x=725, y=540)
- 🔊 **Charger son** : Charge un fichier audio pour le son du spray
- 💾 **Sauvegarder** : Sauvegarde l'image avec options (fond/modèle)

#### Barre latérale droite (à 20% de la hauteur)

**Outils :**
- ↶ **Annuler** : Annule la dernière action (max 50 actions)
- 🧹 **Gomme** : Active/désactive le mode gomme (restaure le fond)
- 🔄 **Recommencer** : Efface le dessin en gardant le fond et le modèle

**Taille du spray (6 paliers) :**
- Bouton **−** : Diminue la taille
- Bouton **+** : Augmente la taille
- Paliers : 20px, 60px, 100px, 140px, 180px, 220px

**Opacité du spray (6 paliers) :**
- ☀ **Blanc** : Diminue l'opacité
- ☀ **Noir** : Augmente l'opacité  
- Paliers : 50%, 60%, 70%, 80%, 90%, 100%

**Palette de couleurs :**
- 16 couleurs disponibles en grille 4x4

### Spray réaliste

Le spray utilise un algorithme de particules pour simuler un vrai spray paint :
- Distribution en 3 zones (centre, intermédiaire, lointaine)
- Particules de tailles variées (0.5px à 2.5px)
- Opacité graduelle du centre vers l'extérieur
- Effet de diffusion naturel

### Sauvegarde

Lors de la sauvegarde, vous pouvez choisir :
- ✓ Inclure l'image de fond
- ✓ Inclure l'image modèle
- Sauvegarder uniquement le dessin

### Multi-écrans

L'application détecte automatiquement les écrans :
- **2+ écrans** : S'ouvre automatiquement sur l'écran secondaire (HDMI)
- **1 écran** : S'ouvre sur l'écran principal
- Mode plein écran automatique sans bordures

## Utilisation avec Epson Pen Interactive

L'application est optimisée pour le stylo interactif Epson :
- Son de spray pendant le dessin (pas avec la gomme)
- Détection de position pour déclencher le son même si la position n'est pas détectée par le projecteur

## Raccourcis clavier

- **ESC** : Quitter l'application (avec confirmation)

## Spécifications techniques

- Résolution : 1920 x 1080 pixels
- Format d'image de fond : PNG, JPG, JPEG, BMP
- Format d'image modèle : PNG, JPG, JPEG, BMP (redimensionné à 1000x1000px)
- Format audio : WAV, MP3, OGG
- Format de sauvegarde : PNG, JPG

## Historique

L'application conserve jusqu'à 50 états pour la fonction Annuler.

## Notes

- Le curseur affiche un cercle de prévisualisation avec la taille actuelle du spray
- La gomme restaure l'image de fond et le modèle (pas seulement du blanc)
- Le son se déclenche uniquement en mode peinture (pas avec la gomme)

## Développement

Créé avec :
- PyQt5 pour l'interface graphique
- Pillow (PIL) pour le traitement d'image
- Pygame pour l'audio
- NumPy pour les conversions d'image

---

**Version finale** - Prêt pour utilisation avec projecteur Epson