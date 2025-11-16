import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QFileDialog,
                             QMessageBox, QCheckBox, QDialog, QGridLayout)
from PyQt5.QtCore import Qt, QPoint, QTimer
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
        self.setFixedSize(400, 250)

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

        title = QLabel("Options de sauvegarde")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; margin: 10px;")
        layout.addWidget(title)

        self.include_background = QCheckBox("Inclure l'image de fond")
        self.include_background.setChecked(True)
        layout.addWidget(self.include_background)

        self.include_template = QCheckBox("Inclure l'image modèle")
        self.include_template.setChecked(True)
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
            self.image.fill(Qt.white)
        except Exception as e:
            print(f"Erreur lors de la création de l'image: {e}")
            # Fallback avec une taille plus petite
            self.image = QImage(800, 600, QImage.Format_ARGB32)
            self.image.fill(Qt.white)

    def paintEvent(self, event):
        """Dessiner le canvas"""
        if self.image is None:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Dessiner l'image
        painter.drawImage(0, 0, self.image)

        # Dessiner le curseur personnalisé (cercle de prévisualisation)
        if not self.drawing and self.cursor_pos and self.parent:
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
            self.drawing = True
            self.last_point = event.pos()
            self.parent.start_spray(event.pos())

    def mouseMoveEvent(self, event):
        """Continuer le dessin ou mettre à jour le curseur"""
        self.cursor_pos = event.pos()

        if self.drawing:
            self.parent.spray_paint(event.pos())

        self.update()

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

        # Audio
        self.spray_sound = None
        self.sound_channel = None

        # Mode gomme
        self.eraser_mode = False

        # Historique
        self.history = []
        self.max_history = 50

        # Détection position
        self.last_valid_position = None

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

        # Widget avec fond métallique
        bar = QWidget()
        bar.setStyleSheet("""
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
        bar.setLayout(bar_layout)

        # Forcer une largeur minimum pour que tous les boutons s'affichent
        # 4 boutons * 40px + 3 espacements * 10px + marges 2*12px = 214px
        bar.setMinimumWidth(220)

        layout.addWidget(bar)
        container.setLayout(layout)

        return container

    def create_right_bar(self):
        """Créer la barre latérale droite avec style métallique"""
        # Container principal
        container = QWidget()
        container.setStyleSheet("background: transparent;")

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Widget avec fond métallique (les contrôles)
        bar = QWidget()
        bar.setStyleSheet("""
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

        bar.setLayout(controls_layout)

        # Forcer la même largeur que la barre du haut
        bar.setMinimumWidth(220)

        layout.addWidget(bar)
        container.setLayout(layout)

        return container

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

            # Définir une taille fixe pour démarrer
            self.setGeometry(100, 100, 1600, 900)
            print(f"Géométrie définie: {self.geometry()}")

            # Si plusieurs écrans, utiliser le second
            if len(screens) > 1:
                print("Plusieurs écrans détectés, utilisation du second")
                screen = screens[1]
                self.setGeometry(screen.geometry())

            # Plein écran (commenté pour le débogage)
            # self.showFullScreen()
            # self.setWindowFlag(Qt.FramelessWindowHint)

            print("Configuration de l'écran terminée")
        except Exception as e:
            print(f"ERREUR dans setup_screen: {e}")
            import traceback
            traceback.print_exc()

    def load_background(self):
        """Charger une image de fond"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Choisir une image de fond",
            "", "Images (*.png *.jpg *.jpeg *.bmp)"
        )

        if file_path:
            try:
                img = Image.open(file_path).convert('RGBA')
                img = img.resize((1920, 1080), Image.Resampling.LANCZOS)
                self.background_image = img
                self.reload_background_layers()
                self.show_message("Succès", "Image de fond chargée !")
            except Exception as e:
                self.show_message("Erreur", f"Impossible de charger l'image:\n{e}", QMessageBox.Critical)

    def load_template(self):
        """Charger une image modèle"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Choisir une image modèle",
            "", "Images (*.png *.jpg *.jpeg *.bmp)"
        )

        if file_path:
            try:
                img = Image.open(file_path).convert('RGBA')
                img = img.resize((1000, 1000), Image.Resampling.LANCZOS)

                # Appliquer 30% d'opacité
                alpha = img.split()[3]
                alpha = ImageEnhance.Brightness(alpha).enhance(0.3)
                img.putalpha(alpha)

                self.template_image = img
                self.reload_background_layers()
                self.show_message("Succès", "Image modèle chargée (opacité 30%) !")
            except Exception as e:
                self.show_message("Erreur", f"Impossible de charger l'image modèle:\n{e}", QMessageBox.Critical)

    def reload_background_layers(self):
        """Recharger toutes les couches"""
        base = Image.new('RGBA', (1920, 1080), (255, 255, 255, 255))

        if self.background_image:
            base = Image.alpha_composite(base, self.background_image)

        if self.template_image:
            x = self.template_position[0] - 500
            y = self.template_position[1] - 500
            base.paste(self.template_image, (x, y), self.template_image)

        # Convertir en QImage
        img_data = base.tobytes("raw", "RGBA")
        qimage = QImage(img_data, 1920, 1080, QImage.Format_RGBA8888)
        self.canvas.image = qimage.copy()

        self.save_state()
        self.canvas.update()

    def load_sound(self):
        """Charger un son"""
        if not self.pygame_available:
            self.show_message("Audio non disponible",
                              "Le système audio n'est pas disponible.",
                              QMessageBox.Warning)
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self, "Choisir un son de spray",
            "", "Audio (*.wav *.mp3 *.ogg)"
        )

        if file_path:
            try:
                self.spray_sound = pygame.mixer.Sound(file_path)
                self.show_message("Succès", "Son chargé avec succès !")
            except Exception as e:
                self.show_message("Erreur", f"Impossible de charger le son:\n{e}", QMessageBox.Critical)

    def save_image(self):
        """Sauvegarder l'image"""
        dialog = SaveDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            # Créer l'image finale
            final_image = Image.new('RGBA', (1920, 1080), (255, 255, 255, 255))

            if dialog.include_background.isChecked() and self.background_image:
                final_image = Image.alpha_composite(final_image, self.background_image)

            if dialog.include_template.isChecked() and self.template_image:
                x = self.template_position[0] - 500
                y = self.template_position[1] - 500
                final_image.paste(self.template_image, (x, y), self.template_image)

            # Convertir QImage en PIL Image
            ptr = self.canvas.image.bits()
            ptr.setsize(1920 * 1080 * 4)
            arr = np.frombuffer(ptr, np.uint8).reshape((1080, 1920, 4))
            current_pil = Image.fromarray(arr, 'RGBA')

            final_image = Image.alpha_composite(final_image, current_pil)
            final_image = final_image.convert('RGB')

            file_path, _ = QFileDialog.getSaveFileName(
                self, "Sauvegarder l'image",
                "", "PNG (*.png);;JPEG (*.jpg)"
            )

            if file_path:
                try:
                    final_image.save(file_path)
                    self.show_message("Succès", f"Image sauvegardée :\n{file_path}")
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
            self.history.pop()
            self.canvas.image = self.history[-1].copy()
            self.canvas.update()

    def restart_with_background(self):
        """Recommencer"""
        if self.show_question("Confirmation",
                              "Recommencer le dessin en gardant le fond et le modèle ?"):
            self.reload_background_layers()

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
        """Sauvegarder l'état"""
        if len(self.history) >= self.max_history:
            self.history.pop(0)
        self.history.append(self.canvas.image.copy())

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
                # Position non détectée, son seulement
                if self.pygame_available and self.spray_sound and not self.eraser_mode and not self.sound_channel:
                    try:
                        self.sound_channel = self.spray_sound.play(loops=-1)
                    except Exception as e:
                        print(f"Erreur lors de la lecture du son: {e}")
                return

        self.last_valid_position = pos

        # Convertir QImage en PIL
        ptr = self.canvas.image.bits()
        ptr.setsize(1920 * 1080 * 4)
        arr = np.frombuffer(ptr, np.uint8).reshape((1080, 1920, 4))
        pil_image = Image.fromarray(arr, 'RGBA')

        x, y = pos.x(), pos.y()

        if self.eraser_mode:
            # Gomme: restaurer le fond
            base = Image.new('RGBA', (1920, 1080), (255, 255, 255, 255))

            if self.background_image:
                base = Image.alpha_composite(base, self.background_image)

            if self.template_image:
                tx = self.template_position[0] - 500
                ty = self.template_position[1] - 500
                base.paste(self.template_image, (tx, ty), self.template_image)

            # Effacer en cercle
            draw = ImageDraw.Draw(pil_image)
            mask = Image.new('L', (1920, 1080), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse([x - self.spray_size, y - self.spray_size,
                               x + self.spray_size, y + self.spray_size], fill=255)

            pil_image = Image.composite(base, pil_image, mask)
        else:
            # Spray réaliste
            spray_layer = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
            spray_draw = ImageDraw.Draw(spray_layer)

            rgb_color = tuple(int(self.spray_color.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))
            num_particles = int(self.spray_size * 3)

            for _ in range(num_particles):
                offset_x = int(random.gauss(0, self.spray_size / 2.5))
                offset_y = int(random.gauss(0, self.spray_size / 2.5))

                distance = (offset_x ** 2 + offset_y ** 2) ** 0.5

                if distance <= self.spray_size:
                    px = x + offset_x
                    py = y + offset_y

                    particle_size = random.choice([1, 1, 1, 2])

                    distance_factor = 1 - (distance / self.spray_size)
                    distance_opacity = int(255 * distance_factor ** 2)
                    final_opacity = int(distance_opacity * (self.spray_opacity / 100.0))
                    final_opacity = int(final_opacity * random.uniform(0.3, 1.0))

                    color_with_opacity = rgb_color + (final_opacity,)

                    if 0 <= px < 1920 and 0 <= py < 1080:
                        spray_draw.ellipse(
                            [px - particle_size, py - particle_size,
                             px + particle_size, py + particle_size],
                            fill=color_with_opacity
                        )

            pil_image = Image.alpha_composite(pil_image, spray_layer)

        # Reconvertir en QImage
        img_data = pil_image.tobytes("raw", "RGBA")
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