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
- 🎨 **Couleur** : Ouvre une palette pour choisir la couleur du spray
- **Slider Taille** : Ajuste la taille du spray (5-100 pixels)
- 🔊 **Charger Son** : Charge un fichier audio de spray (.wav, .mp3, .ogg)
- 🗑️ **Effacer** : Efface tout le dessin (avec confirmation)
- 💾 **Sauvegarder** : Sauvegarde votre création
- ❌ **Quitter** : Ferme l'application

### Dessin

1. **Choisissez votre couleur** avec le bouton "Couleur"
2. **Ajustez la taille** du spray avec le slider
3. **Cliquez et maintenez** avec le stylo Epson (ou la souris) pour dessiner
4. Le son joue automatiquement quand vous dessinez (si chargé)
5. Le son s'arrête quand vous relâchez

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
✅ Opacité variable pour un rendu naturel
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
- Superposez les couleurs pour créer des dégradés
- Chargez une photo de mur pour plus de réalisme

## 📄 Licence

Application créée pour usage personnel avec projecteur Epson EB-475Wi.

## 👨‍💻 Support

Pour tout problème lié aux pilotes Epson, consultez le support officiel Epson.

Bon graffiti ! 🎨🚀
