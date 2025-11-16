import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QFileDialog,
                             QMessageBox, QCheckBox, QDialog, QGridLayout)
from PyQt5.QtCore import Qt, QPoint, QTimer, QPropertyAnimation, QRect
from PyQt5.QtGui import (QPainter, QColor, QPen, QImage, QPixmap, QPainterPath,
                         QLinearGradient, QRadialGradient, QBrush, QCursor)
from PIL import Image, ImageEnhance, ImageDraw
import random
import pygame
import numpy as np


class SaveDialog(QDialog):
    """Dialogue personnalisé pour les options de sauvegarde"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Options de sauvegarde")
        self.setModal(True)
        self.setFixedSize(400, 280)

        # Style du dialogue
        self.setStyleSheet("""
            QDialog {
                background-color: #d0d0d0;
            }
            QLabel {
                color: black;
                font-size: 14px;
                font-weight: bold;
                background-color: transparent;
            }
            QCheckBox {
                color: black;
                font-size: 12px;
                spacing: 10px;
                background-color: transparent;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #666;
                border-radius: 4px;
                background: #f0f0f0;
            }
            QCheckBox::indicator:checked {
                background: #4a9eff;
                border: 2px solid #4a9eff;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f0f0f0, stop:1 #d0d0d0);
                color: black;
                border: 2px solid #808080;
                border-radius: 5px;
                padding: 10px 30px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #e0e0e0);
            }
        """)

        layout = QVBoxLayout()

        title = QLabel("Que souhaitez-vous sauvegarder ?")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; margin: 10px;")
        layout.addWidget(title)

        # Options de sauvegarde
        self.include_drawing = QCheckBox("Inclure le dessin")
        self.include_drawing.setChecked(True)
        self.include_drawing.setEnabled(False)  # Toujours activé
        layout.addWidget(self.include_drawing)

        self.include_background = QCheckBox("Inclure l'image de fond")
        self.include_background.setChecked(False)
        layout.addWidget(self.include_background)

        self.include_template = QCheckBox("Inclure l'image modèle")
        self.include_template.setChecked(False)
        layout.addWidget(self.include_template)

        # Boutons
        btn_layout = QHBoxLayout()

        save_btn = QPushButton("Sauvegarder")
        save_btn.clicked.connect(self.accept)

        cancel_btn = QPushButton("Annuler")
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)

        layout.addStretch()
        layout.addLayout(btn_layout)

        self.setLayout(layout)


class DrawingCanvas(QWidget):
    """Widget de dessin personnalisé"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setMouseTracking(True)
        self.setCursor(Qt.BlankCursor)

        # Image de dessin - initialisation simple
        self.image = None
        self.init_image()

        # Variables de dessin
        self.drawing = False
        self.last_point = QPoint()
        self.cursor_pos = QPoint()

    def init_image(self):
        """Initialiser l'image de dessin"""
        try:
            self.image = QImage(1920, 1080, QImage.Format_ARGB32)
            # Remplir avec du blanc
            self.image.fill(Qt.white)
            # Initialiser la couche de dessin du parent
            if self.parent:
                self.parent.drawing_layer = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
        except Exception as e:
            print(f"Erreur lors de la création de l'image: {e}")
            # Fallback avec une taille plus petite
            self.image = QImage(800, 600, QImage.Format_ARGB32)
            self.image.fill(Qt.white)
            if self.parent:
                self.parent.drawing_layer = Image.new('RGBA', (800, 600), (0, 0, 0, 0))

    def paintEvent(self, event):
        """Dessiner le canvas"""
        if self.image is None:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Dessiner l'image
        painter.drawImage(0, 0, self.image)

        # Dessiner le curseur personnalisé (cercle de prévisualisation)
        # Seulement si on n'est pas en train de dessiner et pas dans une zone protégée
        if not self.drawing and self.cursor_pos and self.parent:
            # Ne pas afficher le curseur dans les zones protégées
            if not self.is_in_protected_zone(self.cursor_pos):
                painter.setPen(QPen(QColor(self.parent.spray_color), 2))
                painter.setBrush(Qt.NoBrush)

                # Cercle
                radius = self.parent.spray_size
                painter.drawEllipse(self.cursor_pos, radius, radius)

                # Croix
                painter.drawLine(self.cursor_pos.x() - 5, self.cursor_pos.y(),
                                 self.cursor_pos.x() + 5, self.cursor_pos.y())
                painter.drawLine(self.cursor_pos.x(), self.cursor_pos.y() - 5,
                                 self.cursor_pos.x(), self.cursor_pos.y() + 5)

    def mousePressEvent(self, event):
        """Démarrer le dessin"""
        if event.button() == Qt.LeftButton:
            # Vérifier si le clic n'est pas dans la zone des menus ou boutons
            if not self.is_in_protected_zone(event.pos()):
                self.drawing = True
                self.last_point = event.pos()
                self.parent.start_spray(event.pos())

    def mouseMoveEvent(self, event):
        """Continuer le dessin ou mettre à jour le curseur"""
        self.cursor_pos = event.pos()

        if self.drawing:
            # Pendant le dessin, vérifier seulement les menus DÉPLOYÉS (pas les boutons)
            if self.is_in_deployed_menu(event.pos()):
                # Si on entre dans un menu déployé, arrêter le dessin
                self.drawing = False
                self.parent.stop_spray()
            else:
                # Sinon, continuer à dessiner normalement
                self.parent.spray_paint(event.pos())

        self.update()

    def is_in_deployed_menu(self, pos):
        """Vérifier si la position est dans un menu DÉPLOYÉ (pas les boutons)"""
        if not self.parent:
            return False

        # Convertir la position du canvas vers les coordonnées de la fenêtre parent
        parent_pos = self.mapTo(self.parent, pos)

        # Menu du haut déployé
        if hasattr(self.parent, 'top_bar_visible') and self.parent.top_bar_visible:
            if hasattr(self.parent, 'top_bar_content'):
                content_global_pos = self.parent.top_bar_content.mapTo(self.parent, QPoint(0, 0))
                content_rect = QRect(
                    content_global_pos.x(),
                    content_global_pos.y(),
                    self.parent.top_bar_content.width(),
                    self.parent.top_bar_content.height()
                )
                if content_rect.contains(parent_pos):
                    return True

        # Menu de droite déployé
        if hasattr(self.parent, 'right_bar_visible') and self.parent.right_bar_visible:
            if hasattr(self.parent, 'right_bar_content'):
                content_global_pos = self.parent.right_bar_content.mapTo(self.parent, QPoint(0, 0))
                content_rect = QRect(
                    content_global_pos.x(),
                    content_global_pos.y(),
                    self.parent.right_bar_content.width(),
                    self.parent.right_bar_content.height()
                )
                if content_rect.contains(parent_pos):
                    return True

        return False

    def is_in_protected_zone(self, pos):
        """Vérifier si la position est dans une zone protégée (pour les clics initiaux)"""
        if not self.parent:
            return False

        # Convertir la position du canvas vers les coordonnées de la fenêtre parent
        parent_pos = self.mapTo(self.parent, pos)

        # Protection du menu du haut
        if hasattr(self.parent, 'top_bar_visible') and hasattr(self.parent, 'top_bar'):
            if self.parent.top_bar_visible:
                # Menu déployé : protéger tout le contenu visible
                if hasattr(self.parent, 'top_bar_content'):
                    content_global_pos = self.parent.top_bar_content.mapTo(self.parent, QPoint(0, 0))
                    content_rect = QRect(
                        content_global_pos.x(),
                        content_global_pos.y(),
                        self.parent.top_bar_content.width(),
                        self.parent.top_bar_content.height()
                    )
                    if content_rect.contains(parent_pos):
                        return True

            # Toujours protéger le bouton toggle du haut
            if hasattr(self.parent, 'top_toggle_btn'):
                btn_global_pos = self.parent.top_toggle_btn.mapTo(self.parent, QPoint(0, 0))
                btn_rect = QRect(
                    btn_global_pos.x(),
                    btn_global_pos.y(),
                    self.parent.top_toggle_btn.width(),
                    self.parent.top_toggle_btn.height()
                )
                if btn_rect.contains(parent_pos):
                    return True

        # Protection du menu de droite
        if hasattr(self.parent, 'right_bar_visible') and hasattr(self.parent, 'right_bar'):
            if self.parent.right_bar_visible:
                # Menu déployé : protéger tout le contenu visible
                if hasattr(self.parent, 'right_bar_content'):
                    content_global_pos = self.parent.right_bar_content.mapTo(self.parent, QPoint(0, 0))
                    content_rect = QRect(
                        content_global_pos.x(),
                        content_global_pos.y(),
                        self.parent.right_bar_content.width(),
                        self.parent.right_bar_content.height()
                    )
                    if content_rect.contains(parent_pos):
                        return True

            # Toujours protéger le bouton toggle de droite - POSITION EXACTE
            if hasattr(self.parent, 'right_toggle_btn'):
                # Obtenir la position réelle du bouton dans la fenêtre
                btn_global_pos = self.parent.right_toggle_btn.mapTo(self.parent, QPoint(0, 0))
                btn_rect = QRect(
                    btn_global_pos.x(),
                    btn_global_pos.y(),
                    self.parent.right_toggle_btn.width(),
                    self.parent.right_toggle_btn.height()
                )
                if btn_rect.contains(parent_pos):
                    return True

        return False

    def mouseReleaseEvent(self, event):
        """Arrêter le dessin"""
        if event.button() == Qt.LeftButton:
            self.drawing = False
            self.parent.stop_spray()


class SprayPaintApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialiser pygame pour l'audio de manière plus sûre
        try:
            pygame.mixer.pre_init(44100, -16, 2, 512)
            pygame.init()
            pygame.mixer.init()
        except Exception as e:
            print(f"Avertissement: Impossible d'initialiser pygame audio: {e}")
            self.pygame_available = False
        else:
            self.pygame_available = True

        # Variables de dessin
        self.spray_color = "#E74C3C"
        self.spray_size = 100
        self.spray_opacity = 100

        # Paliers
        self.size_levels = [20, 60, 100, 140, 180, 220]
        self.current_size_index = 2

        self.opacity_levels = [50, 60, 70, 80, 90, 100]
        self.current_opacity_index = 5

        # Images
        self.background_image = None
        self.template_image = None
        self.template_position = (725, 540)

        # Couche de dessin séparée (pour isoler le dessin du fond/modèle)
        self.drawing_layer = None

        # Audio
        self.spray_sound = None
        self.sound_channel = None

        # Mode gomme
        self.eraser_mode = False

        # Historique
        self.history = []  # Contiendra des tuples (canvas_image, drawing_layer)
        self.max_history = 50

        # Détection position
        self.last_valid_position = None
        self.position_not_detected_count = 0  # Compteur pour détecter les problèmes de stylet

        # État des barres rétractables
        self.top_bar_visible = True
        self.right_bar_visible = True
        self.top_bar_animation = None
        self.right_bar_animation = None

        # Palette de couleurs
        self.color_palette = [
            "#E74C3C", "#E67E22", "#F1C40F", "#2ECC71",
            "#27AE60", "#16A085", "#3498DB", "#2980B9",
            "#9B59B6", "#8E44AD", "#E91E63", "#795548",
            "#95A5A6", "#34495E", "#F39C12", "#ECF0F1"
        ]

        self.init_ui()
        self.setup_screen()

    def init_ui(self):
        """Initialiser l'interface utilisateur"""
        print("Initialisation de l'interface...")
        self.setWindowTitle("Epson Spray Paint - Graffiti Virtuel")
        self.setStyleSheet("background-color: black;")

        # Widget central SIMPLE
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        print("Widget central créé")

        # Attendre que la fenêtre soit visible avant de créer les widgets complexes
        QTimer.singleShot(100, self.create_widgets)

        print("Interface initialisée")

    def create_widgets(self):
        """Créer les widgets après l'initialisation de la fenêtre"""
        print("Création des widgets...")
        central_widget = self.centralWidget()

        # Canvas de dessin en plein écran (en arrière-plan)
        print("Création du canvas...")
        self.canvas = DrawingCanvas(self)
        self.canvas.setParent(central_widget)
        self.canvas.setGeometry(0, 0, self.width(), self.height())
        self.canvas.show()
        print("Canvas créé")

        # Initialiser l'historique avec l'état de départ
        self.save_state()

        # Barre supérieure (overlay en haut à droite)
        print("Création de la barre supérieure...")
        self.top_bar = self.create_top_bar()
        self.top_bar.setParent(central_widget)
        self.top_bar.show()
        self.top_bar.raise_()
        print("Barre supérieure créée")

        # Barre latérale droite (overlay à droite)
        print("Création de la barre droite...")
        self.right_bar = self.create_right_bar()
        self.right_bar.setParent(central_widget)
        self.right_bar.show()
        self.right_bar.raise_()
        print("Barre droite créée")

        # Positionner les barres
        QTimer.singleShot(50, self.position_overlays)
        print("Widgets créés")

    def position_overlays(self):
        """Positionner les barres d'outils en overlay"""
        # Obtenir la taille de la barre droite
        right_bar_width = self.right_bar.sizeHint().width()

        # Positionner la barre du haut en haut à droite
        # Même largeur que la barre de droite, alignée à droite
        top_bar_height = self.top_bar.sizeHint().height()
        self.top_bar.setGeometry(
            self.width() - right_bar_width - 10,  # x: aligné à droite avec même largeur
            10,  # y: en haut
            right_bar_width,  # largeur: même que barre droite
            top_bar_height  # hauteur
        )

        # Positionner la barre de droite plus haut (à 20% de la hauteur au lieu du milieu)
        right_bar_height = self.right_bar.sizeHint().height()
        self.right_bar.setGeometry(
            self.width() - right_bar_width - 10,  # x: à droite
            int(self.height() * 0.2),  # y: à 20% de la hauteur (remonté)
            right_bar_width,  # largeur
            right_bar_height  # hauteur
        )

    def resizeEvent(self, event):
        """Repositionner les overlays quand la fenêtre change de taille"""
        super().resizeEvent(event)
        if hasattr(self, 'canvas'):
            self.canvas.setGeometry(0, 0, self.width(), self.height())
        if hasattr(self, 'top_bar') and hasattr(self, 'right_bar'):
            self.position_overlays()

    def create_top_bar(self):
        """Créer la barre d'outils supérieure avec style métallique"""
        # Container principal
        container = QWidget()
        container.setStyleSheet("background: transparent;")

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # Bouton de réduction/expansion en haut
        self.top_toggle_btn = QPushButton("▼")
        self.top_toggle_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e0e0e0, stop:0.5 #c0c0c0, stop:1 #a0a0a0);
                border: 2px solid #808080;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
                min-height: 25px;
                max-height: 25px;
                color: black;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f0f0f0, stop:0.5 #d0d0d0, stop:1 #b0b0b0);
            }
        """)
        self.top_toggle_btn.clicked.connect(self.toggle_top_bar)
        layout.addWidget(self.top_toggle_btn)

        # Widget avec fond métallique (la barre des outils)
        self.top_bar_content = QWidget()
        self.top_bar_content.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e0e0e0, stop:0.5 #c0c0c0, stop:1 #a0a0a0);
                border: none;
                border-radius: 8px;
            }
        """)

        bar_layout = QVBoxLayout()
        bar_layout.setContentsMargins(12, 12, 12, 12)
        bar_layout.setSpacing(8)

        # Style des boutons métalliques (petits pour la barre du haut)
        button_style = """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f0f0f0, stop:0.5 #d0d0d0, stop:1 #b0b0b0);
                border: 2px solid #808080;
                border-radius: 5px;
                font-size: 22px;
                min-width: 40px;
                min-height: 40px;
                max-width: 40px;
                max-height: 40px;
                margin: 0;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:0.5 #e0e0e0, stop:1 #c0c0c0);
                border: 2px solid #606060;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #b0b0b0, stop:0.5 #d0d0d0, stop:1 #f0f0f0);
            }
        """

        # Frame pour les boutons
        buttons_frame = QWidget()
        buttons_frame.setStyleSheet("background: transparent;")
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        buttons_layout.setContentsMargins(0, 0, 0, 0)

        # Boutons
        btn_background = QPushButton("📁")
        btn_background.setStyleSheet(button_style)
        btn_background.clicked.connect(self.load_background)
        btn_background.setToolTip("Charger image de fond")

        btn_template = QPushButton("🖼")
        btn_template.setStyleSheet(button_style)
        btn_template.clicked.connect(self.load_template)
        btn_template.setToolTip("Charger image modèle")

        btn_sound = QPushButton("🔊")
        btn_sound.setStyleSheet(button_style)
        btn_sound.clicked.connect(self.load_sound)
        btn_sound.setToolTip("Charger son")

        btn_save = QPushButton("💾")
        btn_save.setStyleSheet(button_style)
        btn_save.clicked.connect(self.save_image)
        btn_save.setToolTip("Sauvegarder")

        buttons_layout.addWidget(btn_background)
        buttons_layout.addWidget(btn_template)
        buttons_layout.addWidget(btn_sound)
        buttons_layout.addWidget(btn_save)

        buttons_frame.setLayout(buttons_layout)
        bar_layout.addWidget(buttons_frame)
        self.top_bar_content.setLayout(bar_layout)

        # Forcer une largeur minimum pour que tous les boutons s'affichent
        self.top_bar_content.setMinimumWidth(220)

        layout.addWidget(self.top_bar_content)
        container.setLayout(layout)

        return container

    def create_right_bar(self):
        """Créer la barre latérale droite avec style métallique"""
        # Container principal
        container = QWidget()
        container.setStyleSheet("background: transparent;")

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # Widget avec fond métallique (les contrôles) - AJOUTÉ EN PREMIER
        self.right_bar_content = QWidget()
        self.right_bar_content.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #e0e0e0, stop:0.5 #c0c0c0, stop:1 #a0a0a0);
                border: none;
                border-radius: 8px;
            }
        """)

        controls_layout = QVBoxLayout()
        controls_layout.setContentsMargins(12, 15, 12, 15)
        controls_layout.setSpacing(15)

        # Style des boutons moyens (outils)
        tool_button_style = """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f0f0f0, stop:0.5 #d0d0d0, stop:1 #b0b0b0);
                border: 2px solid #808080;
                border-radius: 6px;
                font-size: 24px;
                min-width: 50px;
                min-height: 50px;
                max-width: 50px;
                max-height: 50px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:0.5 #e0e0e0, stop:1 #c0c0c0);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #b0b0b0, stop:0.5 #d0d0d0, stop:1 #f0f0f0);
            }
        """

        # Style des gros boutons (taille et opacité)
        big_button_style = """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f0f0f0, stop:0.5 #d0d0d0, stop:1 #b0b0b0);
                border: 2px solid #808080;
                border-radius: 6px;
                font-size: 32px;
                min-width: 60px;
                min-height: 60px;
                max-width: 60px;
                max-height: 60px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:0.5 #e0e0e0, stop:1 #c0c0c0);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #b0b0b0, stop:0.5 #d0d0d0, stop:1 #f0f0f0);
            }
        """

        # === SECTION 1 : Outils ===
        tools_frame = QWidget()
        tools_frame.setStyleSheet("background: transparent;")
        tools_layout = QHBoxLayout()
        tools_layout.setSpacing(10)

        btn_undo = QPushButton("↶")
        btn_undo.setStyleSheet(tool_button_style)
        btn_undo.clicked.connect(self.undo)
        btn_undo.setToolTip("Annuler")

        self.btn_eraser = QPushButton("🧹")
        self.btn_eraser.setStyleSheet(tool_button_style)
        self.btn_eraser.clicked.connect(self.toggle_eraser)
        self.btn_eraser.setToolTip("Gomme")

        btn_restart = QPushButton("🔄")
        btn_restart.setStyleSheet(tool_button_style)
        btn_restart.clicked.connect(self.restart_with_background)
        btn_restart.setToolTip("Recommencer")

        tools_layout.addWidget(btn_undo)
        tools_layout.addWidget(self.btn_eraser)
        tools_layout.addWidget(btn_restart)
        tools_frame.setLayout(tools_layout)
        controls_layout.addWidget(tools_frame)

        # === SECTION 2 : Taille ===
        size_frame = QWidget()
        size_frame.setStyleSheet("background: transparent;")
        size_layout = QHBoxLayout()
        size_layout.setSpacing(10)

        btn_size_minus = QPushButton("−")
        btn_size_minus.setStyleSheet(big_button_style + "font-weight: bold;")
        btn_size_minus.clicked.connect(self.decrease_size)

        btn_size_plus = QPushButton("+")
        btn_size_plus.setStyleSheet(big_button_style + "font-weight: bold;")
        btn_size_plus.clicked.connect(self.increase_size)

        size_layout.addWidget(btn_size_minus)
        size_layout.addWidget(btn_size_plus)
        size_frame.setLayout(size_layout)
        controls_layout.addWidget(size_frame)

        # === SECTION 3 : Opacité ===
        opacity_frame = QWidget()
        opacity_frame.setStyleSheet("background: transparent;")
        opacity_layout = QHBoxLayout()
        opacity_layout.setSpacing(10)

        btn_opacity_minus = QPushButton("☀")
        btn_opacity_minus.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #e0e0e0);
                border: 2px solid #808080;
                border-radius: 6px;
                color: black;
                font-size: 32px;
                min-width: 60px;
                min-height: 60px;
                max-width: 60px;
                max-height: 60px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f0f0f0);
            }
        """)
        btn_opacity_minus.clicked.connect(self.decrease_opacity)

        btn_opacity_plus = QPushButton("☀")
        btn_opacity_plus.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #404040, stop:1 #202020);
                border: 2px solid #808080;
                border-radius: 6px;
                color: white;
                font-size: 32px;
                min-width: 60px;
                min-height: 60px;
                max-width: 60px;
                max-height: 60px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #505050, stop:1 #303030);
            }
        """)
        btn_opacity_plus.clicked.connect(self.increase_opacity)

        opacity_layout.addWidget(btn_opacity_minus)
        opacity_layout.addWidget(btn_opacity_plus)
        opacity_frame.setLayout(opacity_layout)
        controls_layout.addWidget(opacity_frame)

        self.opacity_label = QLabel(f"{self.spray_opacity}%")
        self.opacity_label.setAlignment(Qt.AlignCenter)
        self.opacity_label.setStyleSheet("color: black; font-size: 16px; font-weight: bold; background: transparent;")
        controls_layout.addWidget(self.opacity_label)

        # === SECTION 4 : Palette de couleurs (16 couleurs) ===
        colors_widget = QWidget()
        colors_widget.setStyleSheet("background: transparent;")
        colors_layout = QGridLayout()
        colors_layout.setSpacing(4)

        for i, color in enumerate(self.color_palette):
            row = i // 4
            col = i % 4

            btn = QPushButton()
            btn.setFixedSize(36, 36)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    border: 2px solid #404040;
                    border-radius: 18px;
                }}
                QPushButton:hover {{
                    border: 3px solid #ffffff;
                }}
            """)
            btn.clicked.connect(lambda checked, c=color: self.select_color(c))

            colors_layout.addWidget(btn, row, col)

        colors_widget.setLayout(colors_layout)
        controls_layout.addWidget(colors_widget)

        self.right_bar_content.setLayout(controls_layout)

        # Forcer la même largeur que la barre du haut
        self.right_bar_content.setMinimumWidth(220)

        # Ajouter le contenu d'abord
        layout.addWidget(self.right_bar_content)

        # Puis le bouton de réduction/expansion à droite
        self.right_toggle_btn = QPushButton("▶")
        self.right_toggle_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #e0e0e0, stop:0.5 #c0c0c0, stop:1 #a0a0a0);
                border: 2px solid #808080;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
                min-width: 25px;
                max-width: 25px;
                color: black;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f0f0f0, stop:0.5 #d0d0d0, stop:1 #b0b0b0);
            }
        """)
        self.right_toggle_btn.clicked.connect(self.toggle_right_bar)
        layout.addWidget(self.right_toggle_btn)

        container.setLayout(layout)

        return container

    def toggle_top_bar(self):
        """Afficher/masquer la barre du haut avec animation"""
        if self.top_bar_visible:
            # Masquer
            target_height = 0
            self.top_toggle_btn.setText("▼")
            # Permettre de réduire à 0
            self.top_bar_content.setMinimumHeight(0)
        else:
            # Afficher
            target_height = 80  # Hauteur approximative du contenu
            self.top_toggle_btn.setText("▲")
            # Restaurer la hauteur minimum
            self.top_bar_content.setMinimumHeight(0)

        # Créer l'animation
        self.top_bar_animation = QPropertyAnimation(self.top_bar_content, b"maximumHeight")
        self.top_bar_animation.setDuration(300)  # 300ms
        self.top_bar_animation.setStartValue(self.top_bar_content.height())
        self.top_bar_animation.setEndValue(target_height)
        self.top_bar_animation.start()

        self.top_bar_visible = not self.top_bar_visible

    def toggle_right_bar(self):
        """Afficher/masquer la barre de droite avec animation"""
        if self.right_bar_visible:
            # Masquer le contenu (se rétracte vers la gauche)
            target_width = 0
            self.right_toggle_btn.setText("◀")  # Flèche vers la gauche quand masqué
            self.right_bar_content.setMinimumWidth(0)
        else:
            # Afficher le contenu (se déploie vers la gauche)
            target_width = 220
            self.right_toggle_btn.setText("▶")  # Flèche vers la droite quand visible
            self.right_bar_content.setMinimumWidth(220)

        # Animation uniquement de la largeur du contenu
        # Le bouton reste fixe à sa position, le contenu glisse vers la gauche
        self.right_bar_animation = QPropertyAnimation(self.right_bar_content, b"maximumWidth")
        self.right_bar_animation.setDuration(300)
        self.right_bar_animation.setStartValue(self.right_bar_content.width())
        self.right_bar_animation.setEndValue(target_width)
        self.right_bar_animation.start()

        self.right_bar_visible = not self.right_bar_visible

    def show_message(self, title, message, icon=QMessageBox.Information):
        """Afficher un message avec le bon style"""
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(icon)

        # Appliquer le style
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #d0d0d0;
            }
            QLabel {
                color: black;
                font-size: 13px;
                background-color: transparent;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f0f0f0, stop:1 #d0d0d0);
                color: black;
                border: 2px solid #808080;
                border-radius: 5px;
                padding: 8px 20px;
                min-width: 80px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #e0e0e0);
            }
        """)

        msg.exec_()

    def show_question(self, title, message):
        """Afficher une question Oui/Non avec le bon style"""
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(QMessageBox.Question)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

        # Forcer la palette de couleurs
        from PyQt5.QtGui import QPalette
        palette = msg.palette()
        palette.setColor(QPalette.Window, QColor("#d0d0d0"))
        palette.setColor(QPalette.WindowText, QColor("black"))
        palette.setColor(QPalette.Base, QColor("#f0f0f0"))
        palette.setColor(QPalette.Text, QColor("black"))
        palette.setColor(QPalette.Button, QColor("#e0e0e0"))
        palette.setColor(QPalette.ButtonText, QColor("black"))
        msg.setPalette(palette)

        # Appliquer le style
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #d0d0d0;
            }
            QLabel {
                color: black;
                font-size: 13px;
                background-color: transparent;
            }
            QPushButton {
                background-color: #e0e0e0;
                color: black;
                border: 2px solid #808080;
                border-radius: 5px;
                padding: 8px 20px;
                min-width: 80px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)

        # Accéder directement aux boutons et forcer leur style
        for button in msg.buttons():
            button.setStyleSheet("""
                QPushButton {
                    background-color: #e0e0e0;
                    color: black;
                    border: 2px solid #808080;
                    border-radius: 5px;
                    padding: 8px 20px;
                    min-width: 80px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #f0f0f0;
                }
                QPushButton:pressed {
                    background-color: #d0d0d0;
                }
            """)

        return msg.exec_() == QMessageBox.Yes

    def setup_screen(self):
        """Configurer l'écran et le plein écran"""
        print("Configuration de l'écran...")
        try:
            # Obtenir les écrans disponibles
            app = QApplication.instance()
            screens = app.screens()
            print(f"Nombre d'écrans détectés: {len(screens)}")

            # Si plusieurs écrans, utiliser le second (écran HDMI)
            if len(screens) > 1:
                print("Plusieurs écrans détectés, utilisation de l'écran secondaire")
                screen = screens[1]

                # Obtenir la géométrie de l'écran secondaire
                screen_geometry = screen.geometry()
                print(f"Géométrie écran secondaire: {screen_geometry}")

                # Positionner la fenêtre sur l'écran secondaire
                self.move(screen_geometry.x(), screen_geometry.y())

                # Définir la taille en plein écran
                self.resize(screen_geometry.width(), screen_geometry.height())

                # Activer le plein écran sans bordures
                self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
                self.showFullScreen()

                print(f"Application en plein écran sur écran 2: {screen_geometry.width()}x{screen_geometry.height()}")
                print("RAPPEL: Appuyez sur ESC pour quitter l'application")
            else:
                print("Un seul écran détecté, utilisation de l'écran principal")
                screen = screens[0]
                screen_geometry = screen.geometry()

                # Plein écran sur l'écran principal
                self.setWindowFlags(Qt.FramelessWindowHint)
                self.showFullScreen()

                print(
                    f"Application en plein écran sur écran principal: {screen_geometry.width()}x{screen_geometry.height()}")
                print("RAPPEL: Appuyez sur ESC pour quitter l'application")

            print("Configuration de l'écran terminée")
            print("\n" + "=" * 60)
            print("ℹ️  INFORMATION IMPORTANTE - Epson Pen Interactive")
            print("=" * 60)
            print("Si le stylet n'est pas détecté correctement par l'écran :")
            print("• Le son du spray se jouera")
            print("• Mais AUCUN dessin n'apparaîtra")
            print("\nCela indique que le stylet est détecté mais pas sa position.")
            print("Solution : Vérifiez la connexion du stylet à l'écran interactif.")
            print("=" * 60 + "\n")
        except Exception as e:
            print(f"ERREUR dans setup_screen: {e}")
            import traceback
            traceback.print_exc()

    def load_background(self):
        """Charger une image de fond"""
        # Créer le dossier /fonds s'il n'existe pas
        fonds_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonds")
        os.makedirs(fonds_dir, exist_ok=True)

        # Désactiver les sons Windows temporairement
        try:
            import ctypes
            # SPI_SETBEEP = 0x0002, False = désactiver
            ctypes.windll.user32.SystemParametersInfoW(0x0002, 0, 0, 0)
        except:
            pass

        file_path, _ = QFileDialog.getOpenFileName(
            self, "Choisir une image de fond",
            fonds_dir, "Images (*.png *.jpg *.jpeg *.bmp)"
        )

        # Réactiver les sons Windows
        try:
            import ctypes
            ctypes.windll.user32.SystemParametersInfoW(0x0002, 1, 0, 0)
        except:
            pass

        if file_path:
            try:
                img = Image.open(file_path).convert('RGBA')
                img = img.resize((1920, 1080), Image.Resampling.LANCZOS)
                self.background_image = img

                self.reload_background_layers()
                self.save_state()  # Sauvegarder après le chargement
                # Pas de message de succès pour éviter le bruit Windows
            except Exception as e:
                self.show_message("Erreur", f"Impossible de charger l'image:\n{e}", QMessageBox.Critical)

    def load_template(self):
        """Charger une image modèle"""
        # Créer le dossier /modeles s'il n'existe pas
        modeles_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "modeles")
        os.makedirs(modeles_dir, exist_ok=True)

        try:
            import ctypes
            ctypes.windll.user32.SystemParametersInfoW(0x0002, 0, 0, 0)
        except:
            pass

        file_path, _ = QFileDialog.getOpenFileName(
            self, "Choisir une image modèle",
            modeles_dir, "Images (*.png *.jpg *.jpeg *.bmp)"
        )

        try:
            import ctypes
            ctypes.windll.user32.SystemParametersInfoW(0x0002, 1, 0, 0)
        except:
            pass

        if file_path:
            try:
                img = Image.open(file_path).convert('RGBA')
                img = img.resize((1000, 1000), Image.Resampling.LANCZOS)

                # Extraire automatiquement le contenu en supprimant le fond
                img_array = np.array(img)

                # Détecter le fond (couleur dominante dans les coins)
                corners = [
                    img_array[0:10, 0:10],  # Haut gauche
                    img_array[0:10, -10:],  # Haut droit
                    img_array[-10:, 0:10],  # Bas gauche
                    img_array[-10:, -10:]  # Bas droit
                ]

                # Calculer la couleur moyenne des coins (c'est généralement le fond)
                corner_pixels = np.concatenate([c.reshape(-1, 4) for c in corners])
                bg_color = np.median(corner_pixels, axis=0).astype(int)

                # Créer un masque pour isoler le contenu
                # Pixels similaires au fond deviennent transparents
                diff = np.abs(img_array.astype(int) - bg_color)
                # Seuil de différence (ajustable)
                threshold = 50
                is_background = np.all(diff[:, :, :3] < threshold, axis=2)

                # Appliquer le masque
                img_array[:, :, 3] = np.where(is_background, 0, img_array[:, :, 3])

                # Recréer l'image
                img = Image.fromarray(img_array, 'RGBA')

                # Appliquer 60% d'opacité au contenu restant (au lieu de 30%)
                alpha = img.split()[3]
                alpha = ImageEnhance.Brightness(alpha).enhance(0.6)
                img.putalpha(alpha)

                self.template_image = img
                self.reload_background_layers()
                self.save_state()  # Sauvegarder après le chargement
                # Pas de message de succès pour éviter le bruit Windows
            except Exception as e:
                self.show_message("Erreur", f"Impossible de charger l'image modèle:\n{e}", QMessageBox.Critical)

    def reload_background_layers(self):
        """Recharger toutes les couches en préservant le dessin"""
        # Toujours créer un fond blanc
        base = Image.new('RGBA', (1920, 1080), (255, 255, 255, 255))

        if self.background_image:
            base = Image.alpha_composite(base, self.background_image)

        # Le modèle est collé avec alpha compositing pour gérer la transparence
        if self.template_image:
            x = self.template_position[0] - 500
            y = self.template_position[1] - 500
            # Créer une image temporaire pour placer le modèle
            temp_layer = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
            temp_layer.paste(self.template_image, (x, y), self.template_image)
            base = Image.alpha_composite(base, temp_layer)

        # Ajouter le dessin par-dessus si il existe
        if self.drawing_layer is not None:
            base = Image.alpha_composite(base, self.drawing_layer)

        # Convertir en QImage
        img_data = base.tobytes("raw", "RGBA")
        qimage = QImage(img_data, 1920, 1080, QImage.Format_RGBA8888)
        self.canvas.image = qimage.copy()

        # NE PAS sauvegarder l'état ici - cela cause des problèmes avec l'historique
        self.canvas.update()

    def load_sound(self):
        """Charger un son"""
        if not self.pygame_available:
            self.show_message("Audio non disponible",
                              "Le système audio n'est pas disponible.",
                              QMessageBox.Warning)
            return

        # Créer le dossier /sons s'il n'existe pas
        sons_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sons")
        os.makedirs(sons_dir, exist_ok=True)

        try:
            import ctypes
            ctypes.windll.user32.SystemParametersInfoW(0x0002, 0, 0, 0)
        except:
            pass

        file_path, _ = QFileDialog.getOpenFileName(
            self, "Choisir un son de spray",
            sons_dir, "Audio (*.wav *.mp3 *.ogg)"
        )

        try:
            import ctypes
            ctypes.windll.user32.SystemParametersInfoW(0x0002, 1, 0, 0)
        except:
            pass

        if file_path:
            try:
                self.spray_sound = pygame.mixer.Sound(file_path)
                # Pas de message de succès pour éviter le bruit Windows
            except Exception as e:
                self.show_message("Erreur", f"Impossible de charger le son:\n{e}", QMessageBox.Critical)

    def save_image(self):
        """Sauvegarder l'image avec options sélectives"""
        dialog = SaveDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            # Créer le dossier /save s'il n'existe pas
            save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "save")
            os.makedirs(save_dir, exist_ok=True)

            # Récupérer les options
            include_bg = dialog.include_background.isChecked()
            include_tpl = dialog.include_template.isChecked()

            # Composer l'image finale selon les options
            # Si on n'inclut pas le fond, créer un fond transparent pour avoir juste le dessin
            if not include_bg:
                final_image = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
            else:
                final_image = Image.new('RGBA', (1920, 1080), (255, 255, 255, 255))

            # Ajouter le fond si demandé
            if include_bg and self.background_image:
                final_image = Image.alpha_composite(final_image, self.background_image)

            # Ajouter le modèle si demandé
            if include_tpl and self.template_image:
                tx = self.template_position[0] - 500
                ty = self.template_position[1] - 500
                # Créer une image temporaire pour placer le modèle
                temp_layer = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
                temp_layer.paste(self.template_image, (tx, ty), self.template_image)
                final_image = Image.alpha_composite(final_image, temp_layer)

            # Toujours ajouter le dessin (qui est déjà isolé dans drawing_layer)
            if self.drawing_layer:
                final_image = Image.alpha_composite(final_image, self.drawing_layer)

            # Convertir en RGB pour la sauvegarde (sauf si fond transparent)
            if not include_bg:
                # Garder le PNG avec transparence
                pass
            else:
                final_image = final_image.convert('RGB')

            # Désactiver les sons Windows
            try:
                import ctypes
                ctypes.windll.user32.SystemParametersInfoW(0x0002, 0, 0, 0)
            except:
                pass

            # Adapter les formats disponibles selon si on a de la transparence
            if not include_bg:
                file_formats = "PNG (*.png)"
            else:
                file_formats = "PNG (*.png);;JPEG (*.jpg)"

            file_path, _ = QFileDialog.getSaveFileName(
                self, "Sauvegarder l'image",
                save_dir, file_formats
            )

            # Réactiver les sons Windows
            try:
                import ctypes
                ctypes.windll.user32.SystemParametersInfoW(0x0002, 1, 0, 0)
            except:
                pass

            if file_path:
                try:
                    final_image.save(file_path)
                    # Pas de message de succès pour éviter le bruit Windows
                except Exception as e:
                    self.show_message("Erreur", f"Impossible de sauvegarder:\n{e}", QMessageBox.Critical)

    def toggle_eraser(self):
        """Activer/désactiver la gomme"""
        self.eraser_mode = not self.eraser_mode

        if self.eraser_mode:
            self.btn_eraser.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #ff9999, stop:0.5 #ff6b6b, stop:1 #ff4444);
                    border: 2px solid #cc0000;
                    border-radius: 6px;
                    font-size: 24px;
                    min-width: 50px;
                    min-height: 50px;
                    max-width: 50px;
                    max-height: 50px;
                }
            """)
        else:
            self.btn_eraser.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #f0f0f0, stop:0.5 #d0d0d0, stop:1 #b0b0b0);
                    border: 2px solid #808080;
                    border-radius: 6px;
                    font-size: 24px;
                    min-width: 50px;
                    min-height: 50px;
                    max-width: 50px;
                    max-height: 50px;
                }
            """)

    def undo(self):
        """Annuler"""
        if len(self.history) > 1:
            # Retirer l'état actuel
            self.history.pop()
            # Récupérer l'état précédent
            canvas_image, drawing_layer = self.history[-1]
            self.canvas.image = canvas_image.copy()
            if drawing_layer:
                self.drawing_layer = drawing_layer.copy()
            self.canvas.update()

    def restart_with_background(self):
        """Recommencer"""
        if self.show_question("Confirmation",
                              "Recommencer le dessin en gardant le fond et le modèle ?"):
            # Réinitialiser uniquement la couche de dessin
            self.drawing_layer = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
            self.reload_background_layers()
            self.save_state()  # Sauvegarder après le restart

    def decrease_size(self):
        """Diminuer la taille"""
        if self.current_size_index > 0:
            self.current_size_index -= 1
            self.spray_size = self.size_levels[self.current_size_index]

    def increase_size(self):
        """Augmenter la taille"""
        if self.current_size_index < len(self.size_levels) - 1:
            self.current_size_index += 1
            self.spray_size = self.size_levels[self.current_size_index]

    def decrease_opacity(self):
        """Diminuer l'opacité"""
        if self.current_opacity_index > 0:
            self.current_opacity_index -= 1
            self.spray_opacity = self.opacity_levels[self.current_opacity_index]
            self.opacity_label.setText(f"{self.spray_opacity}%")

    def increase_opacity(self):
        """Augmenter l'opacité"""
        if self.current_opacity_index < len(self.opacity_levels) - 1:
            self.current_opacity_index += 1
            self.spray_opacity = self.opacity_levels[self.current_opacity_index]
            self.opacity_label.setText(f"{self.spray_opacity}%")

    def select_color(self, color):
        """Sélectionner une couleur"""
        self.spray_color = color

    def save_state(self):
        """Sauvegarder l'état (canvas + couche de dessin)"""
        if len(self.history) >= self.max_history:
            self.history.pop(0)
        # Sauvegarder à la fois l'image canvas et la couche de dessin
        drawing_copy = self.drawing_layer.copy() if self.drawing_layer else None
        self.history.append((self.canvas.image.copy(), drawing_copy))

    def start_spray(self, pos):
        """Démarrer le spray"""
        self.last_valid_position = pos
        self.save_state()

        if self.pygame_available and self.spray_sound and not self.eraser_mode:
            try:
                self.sound_channel = self.spray_sound.play(loops=-1)
            except Exception as e:
                print(f"Erreur lors de la lecture du son: {e}")

    def spray_paint(self, pos):
        """Appliquer le spray"""
        # Détection de position valide
        if self.last_valid_position:
            dx = abs(pos.x() - self.last_valid_position.x())
            dy = abs(pos.y() - self.last_valid_position.y())

            if dx < 2 and dy < 2:
                # Position non détectée, son seulement (problème de stylet Epson)
                self.position_not_detected_count += 1

                # Afficher un avertissement après 10 tentatives
                if self.position_not_detected_count == 10:
                    print("\n⚠️  ATTENTION: Le stylet Epson est détecté mais sa position ne l'est pas!")
                    print("   Le son se joue mais aucun dessin n'apparaît.")
                    print("   Vérifiez la connexion du stylet à l'écran interactif.\n")

                if self.pygame_available and self.spray_sound and not self.eraser_mode and not self.sound_channel:
                    try:
                        self.sound_channel = self.spray_sound.play(loops=-1)
                    except Exception as e:
                        print(f"Erreur lors de la lecture du son: {e}")
                return
            else:
                # Position détectée correctement, réinitialiser le compteur
                if self.position_not_detected_count > 0:
                    print("✓ Position du stylet détectée correctement!")
                    self.position_not_detected_count = 0

        self.last_valid_position = pos

        x, y = pos.x(), pos.y()

        if self.eraser_mode:
            # Gomme: effacer sur la couche de dessin
            mask = Image.new('L', (1920, 1080), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse([x - self.spray_size, y - self.spray_size,
                               x + self.spray_size, y + self.spray_size], fill=255)

            # Créer une image transparente
            transparent = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))

            # Appliquer le masque pour effacer la zone sur la couche de dessin
            self.drawing_layer = Image.composite(transparent, self.drawing_layer, mask)
        else:
            # Spray réaliste ultra amélioré
            spray_layer = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
            spray_draw = ImageDraw.Draw(spray_layer)

            rgb_color = tuple(int(self.spray_color.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))

            # Nombre de particules ajusté pour éviter un centre trop dense
            num_particles = int(self.spray_size * 6)

            for _ in range(num_particles):
                # Distribution ajustée :
                # 50% des particules au centre (au lieu de 60%)
                # 35% des particules en zone intermédiaire (au lieu de 30%)
                # 15% des particules très éloignées (au lieu de 10%)
                rand = random.random()

                if rand < 0.5:
                    # Zone centrale - distribution légèrement plus large
                    offset_x = int(random.gauss(0, self.spray_size / 3.5))
                    offset_y = int(random.gauss(0, self.spray_size / 3.5))
                elif rand < 0.85:
                    # Zone intermédiaire
                    offset_x = int(random.gauss(0, self.spray_size / 1.8))
                    offset_y = int(random.gauss(0, self.spray_size / 1.8))
                else:
                    # Particules très éloignées (projections)
                    offset_x = int(random.gauss(0, self.spray_size * 1.5))
                    offset_y = int(random.gauss(0, self.spray_size * 1.5))

                distance = (offset_x ** 2 + offset_y ** 2) ** 0.5

                # Limite plus souple pour permettre aux particules d'aller plus loin
                if distance <= self.spray_size * 2:
                    px = x + offset_x
                    py = y + offset_y

                    # Tailles de particules très variées
                    particle_rand = random.random()
                    if particle_rand < 0.75:
                        # 75% de très petites particules (1 pixel)
                        particle_size = 0.5
                    elif particle_rand < 0.92:
                        # 17% de petites particules (2 pixels)
                        particle_size = 1
                    else:
                        # 8% de particules moyennes (3-4 pixels)
                        particle_size = random.uniform(1.5, 2.5)

                    # Opacité basée sur la distance avec courbe plus douce
                    if distance < self.spray_size * 0.3:
                        # Centre - opacité réduite pour moins de densité
                        base_opacity = random.uniform(0.6, 0.9)
                    elif distance < self.spray_size:
                        # Zone intermédiaire
                        distance_factor = 1 - (distance / self.spray_size)
                        base_opacity = distance_factor ** 1.5 * random.uniform(0.4, 0.9)
                    else:
                        # Zone éloignée, très transparent
                        distance_factor = 1 - (distance / (self.spray_size * 2))
                        base_opacity = distance_factor ** 3 * random.uniform(0.1, 0.4)

                    final_opacity = int(255 * base_opacity * (self.spray_opacity / 100.0))

                    # Limiter l'opacité pour éviter les pixels complètement opaques
                    final_opacity = min(final_opacity, 200)

                    color_with_opacity = rgb_color + (final_opacity,)

                    if 0 <= px < 1920 and 0 <= py < 1080:
                        spray_draw.ellipse(
                            [px - particle_size, py - particle_size,
                             px + particle_size, py + particle_size],
                            fill=color_with_opacity
                        )

            # Ajouter le spray à la couche de dessin
            self.drawing_layer = Image.alpha_composite(self.drawing_layer, spray_layer)

        # Recomposer l'image complète : fond + modèle + dessin
        final_image = Image.new('RGBA', (1920, 1080), (255, 255, 255, 255))

        if self.background_image:
            final_image = Image.alpha_composite(final_image, self.background_image)

        # Le modèle est collé avec alpha compositing pour gérer la transparence
        if self.template_image:
            tx = self.template_position[0] - 500
            ty = self.template_position[1] - 500
            # Créer une image temporaire pour placer le modèle
            temp_layer = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
            temp_layer.paste(self.template_image, (tx, ty), self.template_image)
            final_image = Image.alpha_composite(final_image, temp_layer)

        # Ajouter le dessin par-dessus
        final_image = Image.alpha_composite(final_image, self.drawing_layer)

        # Reconvertir en QImage
        img_data = final_image.tobytes("raw", "RGBA")
        self.canvas.image = QImage(img_data, 1920, 1080, QImage.Format_RGBA8888).copy()
        self.canvas.update()

    def stop_spray(self):
        """Arrêter le spray"""
        if self.sound_channel:
            try:
                self.sound_channel.stop()
            except Exception as e:
                print(f"Erreur lors de l'arrêt du son: {e}")
            finally:
                self.sound_channel = None

    def keyPressEvent(self, event):
        """Gérer les touches"""
        if event.key() == Qt.Key_Escape:
            if self.show_question("Quitter", "Voulez-vous vraiment quitter ?"):
                if self.pygame_available:
                    try:
                        pygame.mixer.quit()
                        pygame.quit()
                    except:
                        pass
                self.close()

    def closeEvent(self, event):
        """Gérer la fermeture de la fenêtre"""
        if self.pygame_available:
            try:
                pygame.mixer.quit()
                pygame.quit()
            except:
                pass
        event.accept()


def main():
    print("Démarrage de l'application...")
    app = QApplication(sys.argv)
    print("QApplication créée")

    try:
        window = SprayPaintApp()
        print("Fenêtre créée")
        window.show()
        print("Fenêtre affichée")
        print(f"Fenêtre visible: {window.isVisible()}")
        print(f"Géométrie: {window.geometry()}")
    except Exception as e:
        print(f"ERREUR lors de la création de la fenêtre: {e}")
        import traceback
        traceback.print_exc()
        return

    print("Lancement de la boucle d'événements...")
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()