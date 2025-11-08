# 🎨 Epson Spray Paint - Application de Graffiti Virtuel

Application Python pour transformer votre stylo interactif Epson Easy Interactive Pen en bombe de peinture virtuelle sur votre projecteur Epson EB-475Wi.

## 📋 Prérequis

### 1. Python
- Python 3.7 ou supérieur

### 2. Pilotes Epson
**IMPORTANT** : Vous devez installer les pilotes Epson Easy Interactive Driver pour que le stylo soit reconnu par Windows.

Téléchargement : [Site officiel Epson](https://epson.com)
- Recherchez "Epson EB-475Wi drivers"
- Téléchargez et installez "Easy Interactive Driver"

### 3. Bibliothèques Python
Installez les bibliothèques nécessaires avec pip :

```bash
pip install pillow pygame
```

**Détail des bibliothèques :**
- `Pillow` : Pour la manipulation d'images
- `pygame` : Pour la lecture audio
- `tkinter` : Inclus avec Python (interface graphique)

## 🚀 Installation

1. **Téléchargez le fichier** `spray_paint_app.py`

2. **Installez les dépendances** :
```bash
pip install pillow pygame
```

3. **Installez les pilotes Epson** (si ce n'est pas déjà fait)

## 💻 Utilisation

### Lancement de l'application
```bash
python spray_paint_app.py
```

L'application se lance automatiquement en plein écran.

### Interface

**Barre d'outils (en haut) :**
- 📁 **Charger Image** : Charge une image de fond (.png, .jpg, .jpeg, .bmp, .gif)
- 🔄 **Reload** : Recharge l'image originale et efface tous les dessins
- 🎨 **Couleur** : Ouvre une palette pour choisir la couleur du spray
- 🧹 **Gomme** : Active/désactive le mode gomme (efface uniquement la peinture, pas l'image de fond)
- **Slider Taille** : Ajuste la taille du spray/gomme (5-100 pixels)
- **Slider Opacité** : Ajuste l'opacité de la peinture (10-100%)
- 🔊 **Son** : Charge un fichier audio de spray (.wav, .mp3, .ogg)
- ↶ **Annuler** : Annule la dernière action (jusqu'à 50 actions)
- 🗑️ **Effacer** : Efface tout le dessin (avec confirmation)
- 💾 **Sauvegarder** : Sauvegarde votre création
- ❌ **Quitter** : Ferme l'application

### Dessin

1. **Choisissez votre couleur** avec le bouton "Couleur"
2. **Ajustez la taille** du spray avec le slider "Taille"
3. **Ajustez l'opacité** avec le slider "Opacité" (100% = opaque, 10% = transparent)
4. **Une cible apparaît** autour de votre curseur pour prévisualiser la taille et le mode
   - **Mode peinture** : Cercle avec la couleur sélectionnée + cercle central montrant l'opacité
   - **Mode gomme** : Cercle rouge pointillé avec une croix
5. **Cliquez et maintenez** avec le stylo Epson (ou la souris) pour dessiner
6. Le son joue automatiquement quand vous dessinez (si chargé)
7. Le son s'arrête quand vous relâchez

### Mode Gomme

1. **Cliquez sur "Gomme"** pour activer le mode gomme (le bouton devient enfoncé)
2. La gomme efface **uniquement la peinture**, pas l'image de fond
3. **Recliquez sur "Gomme"** pour revenir au mode peinture

### Annuler / Reload

- **Annuler** : Annule le dernier coup de spray/gomme (historique de 50 actions)
- **Reload** : Repart de l'image originale, efface tous les dessins

### Raccourcis clavier
- **Échap** : Quitter/entrer en mode plein écran

## 🎵 Fichiers audio

Vous devez fournir vos propres fichiers audio de spray. Formats supportés :
- `.wav` (recommandé pour la qualité)
- `.mp3`
- `.ogg`

**Conseil** : Utilisez un son court (~1-2 secondes) qui sera lu en boucle pendant le dessin.

## 🎯 Utilisation avec le projecteur Epson

1. **Connectez votre PC au projecteur** Epson EB-475Wi
2. **Configurez l'affichage** :
   - Mode miroir (duplication) : l'interface sera visible sur le projecteur
   - Mode étendu : déplacez l'application sur l'écran du projecteur
3. **Calibrez le stylo** avec les pilotes Epson si nécessaire
4. **Lancez l'application**
5. Le stylo fonctionnera comme un outil de dessin tactile

## 🔧 Configuration du projecteur

Le projecteur doit être en mode "Interactive" pour que le stylo fonctionne correctement. Consultez le manuel du EB-475Wi pour plus de détails.

## ⚙️ Fonctionnalités

✅ Interface plein écran optimisée pour projection
✅ Effet spray réaliste avec particules dispersées
✅ Cible de prévisualisation dynamique (affiche la taille et le mode)
✅ Opacité/transparence ajustable (10-100%)
✅ Superposition de couleurs avec transparence réelle
✅ Mode gomme intelligent (efface uniquement la peinture)
✅ Historique d'annulation (jusqu'à 50 actions)
✅ Bouton Reload pour repartir de l'image originale
✅ Chargement d'images de fond
✅ Sélection de couleurs illimitée
✅ Taille de spray ajustable (5-100px)
✅ Son de spray personnalisable
✅ Sauvegarde des créations en PNG/JPEG
✅ Compatible avec le stylo Epson Easy Interactive Pen

## 🐛 Dépannage

### Le stylo ne fonctionne pas
- Vérifiez que les pilotes Easy Interactive Driver sont installés
- Calibrez le stylo via le logiciel Epson
- Vérifiez que le projecteur est en mode interactif

### Pas de son
- Vérifiez que vous avez chargé un fichier audio
- Testez avec un fichier .wav
- Vérifiez le volume de votre système

### L'application est lente
- Réduisez la taille du spray
- Utilisez une image de fond plus petite
- Fermez les autres applications

### L'image de fond ne s'affiche pas correctement
- Utilisez des images en résolution standard (1920x1080 ou moins)
- Formats recommandés : PNG ou JPEG

## 📝 Notes techniques

- L'effet spray utilise un algorithme de dispersion aléatoire
- L'opacité diminue vers les bords pour un effet naturel
- Le son joue en boucle pendant le dessin
- Les images sont sauvegardées en pleine résolution

## 🎨 Astuces créatives

- Commencez avec une grande taille pour les fonds
- Utilisez une petite taille pour les détails
- **Jouez avec l'opacité** : Réglez à 30-50% pour créer des effets de superposition et dégradés
- **Superposez les couleurs** : Peignez une couleur, puis une autre avec faible opacité par-dessus
- Chargez une photo de mur pour plus de réalisme
- La cible vous montre exactement ce qui va être dessiné

## 📄 Licence

Application créée pour usage personnel avec projecteur Epson EB-475Wi.

## 👨‍💻 Support

Pour tout problème lié aux pilotes Epson, consultez le support officiel Epson.

Bon graffiti ! 🎨🚀
