import tkinter as tk
from tkinter import filedialog, colorchooser, messagebox
from PIL import Image, ImageDraw, ImageTk
import random
import pygame
import os


class SprayPaintApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Epson Spray Paint - Graffiti Virtuel")

        # Initialiser pygame pour l'audio
        pygame.mixer.init()

        # Variables de dessin
        self.spray_color = "#FF0000"  # Rouge par défaut
        self.spray_size = 20
        self.spray_opacity = 100  # Opacité en pourcentage (0-100)
        self.background_image = None
        self.canvas_image = None
        self.drawing = False
        self.spray_sound = None
        self.sound_channel = None
        self.eraser_mode = False  # Mode gomme

        # Cible de prévisualisation
        self.preview_circle = None
        self.preview_enabled = True

        # Historique pour annulation
        self.history = []  # Liste des états de l'image
        self.max_history = 50  # Nombre maximum d'états sauvegardés

        # Configuration de la fenêtre en plein écran
        self.root.attributes('-fullscreen', True)
        self.root.bind('<Escape>', lambda e: self.toggle_fullscreen())

        # Obtenir les dimensions de l'écran
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        self.setup_ui()

    def setup_ui(self):
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#2b2b2b')
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Barre d'outils en haut
        toolbar = tk.Frame(main_frame, bg='#1e1e1e', height=80)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        # Bouton charger image
        btn_load = tk.Button(toolbar, text="📁 Charger Image",
                             command=self.load_image,
                             bg='#4a4a4a', fg='white', font=('Arial', 11, 'bold'),
                             padx=10, pady=8, cursor='hand2')
        btn_load.pack(side=tk.LEFT, padx=5, pady=10)

        # Bouton reload (repartir de l'image originale)
        btn_reload = tk.Button(toolbar, text="🔄 Reload",
                               command=self.reload_image,
                               bg='#4a9eff', fg='white', font=('Arial', 11, 'bold'),
                               padx=10, pady=8, cursor='hand2')
        btn_reload.pack(side=tk.LEFT, padx=5, pady=10)

        # Bouton choix couleur
        self.color_btn = tk.Button(toolbar, text="🎨 Couleur",
                                   command=self.choose_color,
                                   bg=self.spray_color, fg='white',
                                   font=('Arial', 11, 'bold'),
                                   padx=10, pady=8, cursor='hand2',
                                   width=8)
        self.color_btn.pack(side=tk.LEFT, padx=5, pady=10)

        # Bouton gomme
        self.eraser_btn = tk.Button(toolbar, text="🧹 Gomme",
                                    command=self.toggle_eraser,
                                    bg='#4a4a4a', fg='white',
                                    font=('Arial', 11, 'bold'),
                                    padx=10, pady=8, cursor='hand2',
                                    relief=tk.RAISED)
        self.eraser_btn.pack(side=tk.LEFT, padx=5, pady=10)

        # Label et slider pour la taille
        tk.Label(toolbar, text="Taille:", bg='#1e1e1e', fg='white',
                 font=('Arial', 10)).pack(side=tk.LEFT, padx=(10, 5))

        self.size_var = tk.IntVar(value=self.spray_size)
        size_slider = tk.Scale(toolbar, from_=5, to=100, orient=tk.HORIZONTAL,
                               variable=self.size_var, command=self.update_spray_size,
                               bg='#4a4a4a', fg='white', highlightthickness=0,
                               length=150, width=15)
        size_slider.pack(side=tk.LEFT, padx=5, pady=10)

        self.size_label = tk.Label(toolbar, text=f"{self.spray_size}px",
                                   bg='#1e1e1e', fg='white', font=('Arial', 10),
                                   width=5)
        self.size_label.pack(side=tk.LEFT, padx=5)

        # Label et slider pour l'opacité
        tk.Label(toolbar, text="Opacité:", bg='#1e1e1e', fg='white',
                 font=('Arial', 10)).pack(side=tk.LEFT, padx=(10, 5))

        self.opacity_var = tk.IntVar(value=self.spray_opacity)
        opacity_slider = tk.Scale(toolbar, from_=10, to=100, orient=tk.HORIZONTAL,
                                  variable=self.opacity_var, command=self.update_opacity,
                                  bg='#4a4a4a', fg='white', highlightthickness=0,
                                  length=150, width=15)
        opacity_slider.pack(side=tk.LEFT, padx=5, pady=10)

        self.opacity_label = tk.Label(toolbar, text=f"{self.spray_opacity}%",
                                      bg='#1e1e1e', fg='white', font=('Arial', 10),
                                      width=5)
        self.opacity_label.pack(side=tk.LEFT, padx=5)

        # Bouton charger son
        btn_load_sound = tk.Button(toolbar, text="🔊 Son",
                                   command=self.load_sound,
                                   bg='#4a4a4a', fg='white', font=('Arial', 11, 'bold'),
                                   padx=10, pady=8, cursor='hand2')
        btn_load_sound.pack(side=tk.LEFT, padx=5, pady=10)

        # Bouton annuler
        btn_undo = tk.Button(toolbar, text="↶ Annuler",
                             command=self.undo,
                             bg='#ff9944', fg='white', font=('Arial', 11, 'bold'),
                             padx=10, pady=8, cursor='hand2')
        btn_undo.pack(side=tk.LEFT, padx=5, pady=10)

        # Bouton effacer
        btn_clear = tk.Button(toolbar, text="🗑️ Effacer",
                              command=self.clear_canvas,
                              bg='#ff4444', fg='white', font=('Arial', 11, 'bold'),
                              padx=10, pady=8, cursor='hand2')
        btn_clear.pack(side=tk.LEFT, padx=5, pady=10)

        # Bouton sauvegarder
        btn_save = tk.Button(toolbar, text="💾 Sauvegarder",
                             command=self.save_image,
                             bg='#44ff44', fg='black', font=('Arial', 11, 'bold'),
                             padx=10, pady=8, cursor='hand2')
        btn_save.pack(side=tk.LEFT, padx=5, pady=10)

        # Bouton quitter
        btn_quit = tk.Button(toolbar, text="❌ Quitter",
                             command=self.quit_app,
                             bg='#ff8844', fg='white', font=('Arial', 11, 'bold'),
                             padx=10, pady=8, cursor='hand2')
        btn_quit.pack(side=tk.RIGHT, padx=5, pady=10)

        # Canvas pour dessiner
        self.canvas = tk.Canvas(main_frame, bg='white', cursor='none')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Événements de dessin
        self.canvas.bind('<Button-1>', self.start_spray)
        self.canvas.bind('<B1-Motion>', self.spray_paint)
        self.canvas.bind('<ButtonRelease-1>', self.stop_spray)

        # Événements pour la cible de prévisualisation
        self.canvas.bind('<Motion>', self.update_preview)
        self.canvas.bind('<Leave>', self.hide_preview)
        self.canvas.bind('<Enter>', self.show_preview)

        # Créer une image PIL pour le dessin
        canvas_width = self.screen_width
        canvas_height = self.screen_height - 80  # Moins la barre d'outils
        self.pil_image = Image.new('RGB', (canvas_width, canvas_height), 'white')
        self.draw = ImageDraw.Draw(self.pil_image)

    def load_image(self):
        """Charger une image de fond"""
        file_path = filedialog.askopenfilename(
            title="Choisir une image de fond",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )

        if file_path:
            try:
                # Charger et redimensionner l'image
                img = Image.open(file_path)
                canvas_width = self.canvas.winfo_width() or self.screen_width
                canvas_height = self.canvas.winfo_height() or (self.screen_height - 80)

                # Redimensionner en gardant les proportions
                img.thumbnail((canvas_width, canvas_height), Image.Resampling.LANCZOS)

                # Créer une nouvelle image avec fond blanc
                self.pil_image = Image.new('RGB', (canvas_width, canvas_height), 'white')

                # Coller l'image au centre
                x = (canvas_width - img.width) // 2
                y = (canvas_height - img.height) // 2
                self.pil_image.paste(img, (x, y))

                # Sauvegarder l'image de fond originale
                self.background_image = self.pil_image.copy()

                self.draw = ImageDraw.Draw(self.pil_image)

                # Réinitialiser l'historique
                self.history = []
                self.save_state()

                # Afficher sur le canvas
                self.update_canvas()

                messagebox.showinfo("Succès", "Image chargée avec succès !")
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de charger l'image:\n{e}")

    def reload_image(self):
        """Recharger l'image de fond originale"""
        if self.background_image:
            if messagebox.askyesno("Confirmation",
                                   "Voulez-vous repartir de l'image originale ?\nTout le dessin sera effacé."):
                self.pil_image = self.background_image.copy()
                self.draw = ImageDraw.Draw(self.pil_image)

                # Réinitialiser l'historique
                self.history = []
                self.save_state()

                self.update_canvas()
                messagebox.showinfo("Succès", "Image rechargée !")
        else:
            messagebox.showwarning("Attention", "Aucune image de fond n'a été chargée.")

    def toggle_eraser(self):
        """Basculer entre le mode gomme et le mode peinture"""
        self.eraser_mode = not self.eraser_mode

        if self.eraser_mode:
            self.eraser_btn.config(relief=tk.SUNKEN, bg='#ff6666')
        else:
            self.eraser_btn.config(relief=tk.RAISED, bg='#4a4a4a')

    def save_state(self):
        """Sauvegarder l'état actuel de l'image dans l'historique"""
        # Sauvegarder une copie de l'image actuelle
        self.history.append(self.pil_image.copy())

        # Limiter la taille de l'historique
        if len(self.history) > self.max_history:
            self.history.pop(0)

    def undo(self):
        """Annuler la dernière action"""
        if len(self.history) > 1:
            # Retirer l'état actuel
            self.history.pop()

            # Restaurer l'état précédent
            self.pil_image = self.history[-1].copy()
            self.draw = ImageDraw.Draw(self.pil_image)

            self.update_canvas()
        else:
            messagebox.showinfo("Info", "Aucune action à annuler.")

    def update_preview(self, event):
        """Mettre à jour la position de la cible de prévisualisation"""
        # Ne pas afficher la cible pendant le dessin
        if self.drawing:
            return

        if self.preview_enabled:
            # Supprimer l'ancienne cible
            if self.preview_circle:
                self.canvas.delete(self.preview_circle)
                self.canvas.delete('preview_cross')

            x, y = event.x, event.y
            size = self.spray_size

            # Choisir la couleur de la cible selon le mode
            if self.eraser_mode:
                # Mode gomme : cible avec croix
                outline_color = '#ff0000'
                fill_color = ''

                # Dessiner le cercle
                self.preview_circle = self.canvas.create_oval(
                    x - size, y - size, x + size, y + size,
                    outline=outline_color, width=2, dash=(4, 4)
                )

                # Ajouter une croix au centre
                cross_size = 10
                self.canvas.create_line(
                    x - cross_size, y, x + cross_size, y,
                    fill=outline_color, width=2, tags='preview_cross'
                )
                self.canvas.create_line(
                    x, y - cross_size, x, y + cross_size,
                    fill=outline_color, width=2, tags='preview_cross'
                )
            else:
                # Mode peinture : cible avec la couleur sélectionnée
                # Calculer la transparence pour l'affichage
                rgb = self.hex_to_rgb(self.spray_color)
                opacity_alpha = int(self.spray_opacity * 2.55)  # Convertir 0-100 en 0-255

                # Créer une couleur semi-transparente pour la prévisualisation
                outline_color = self.spray_color

                # Dessiner le cercle extérieur
                self.preview_circle = self.canvas.create_oval(
                    x - size, y - size, x + size, y + size,
                    outline=outline_color, width=2
                )

                # Dessiner une croix au centre
                cross_size = 8
                self.canvas.create_line(
                    x - cross_size, y, x + cross_size, y,
                    fill=outline_color, width=1, tags='preview_cross'
                )
                self.canvas.create_line(
                    x, y - cross_size, x, y + cross_size,
                    fill=outline_color, width=1, tags='preview_cross'
                )

    def hide_preview(self, event):
        """Cacher la cible quand le curseur sort du canvas"""
        if self.preview_circle:
            self.canvas.delete(self.preview_circle)
            self.canvas.delete('preview_cross')
            self.preview_circle = None

    def show_preview(self, event):
        """Afficher la cible quand le curseur entre dans le canvas"""
        self.preview_enabled = True

    def update_opacity(self, value):
        """Mettre à jour l'opacité du spray"""
        self.spray_opacity = int(value)
        self.opacity_label.config(text=f"{self.spray_opacity}%")

    def choose_color(self):
        """Choisir une couleur"""
        color = colorchooser.askcolor(title="Choisir une couleur de spray")[1]
        if color:
            self.spray_color = color
            self.color_btn.config(bg=self.spray_color)

    def update_spray_size(self, value):
        """Mettre à jour la taille du spray"""
        self.spray_size = int(value)
        self.size_label.config(text=f"{self.spray_size}px")

    def load_sound(self):
        """Charger un fichier son pour le spray"""
        file_path = filedialog.askopenfilename(
            title="Choisir un son de spray",
            filetypes=[("Audio", "*.wav *.mp3 *.ogg")]
        )

        if file_path:
            try:
                self.spray_sound = pygame.mixer.Sound(file_path)
                messagebox.showinfo("Succès", "Son chargé avec succès !")
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de charger le son:\n{e}")

    def start_spray(self, event):
        """Commencer à dessiner"""
        self.drawing = True

        # Cacher la cible pendant le dessin
        if self.preview_circle:
            self.canvas.delete(self.preview_circle)
            self.canvas.delete('preview_cross')
            self.preview_circle = None

        # Sauvegarder l'état avant de dessiner
        self.save_state()

        self.spray_paint(event)

        # Jouer le son en boucle
        if self.spray_sound:
            self.sound_channel = self.spray_sound.play(loops=-1)

    def spray_paint(self, event):
        """Dessiner avec effet spray ou gomme"""
        if not self.drawing:
            return

        x, y = event.x, event.y

        # Mode gomme : effacer en restaurant l'image de fond
        if self.eraser_mode:
            if self.background_image:
                # Créer un masque circulaire pour la gomme
                eraser_size = self.spray_size

                # Copier la zone de l'image de fond
                for dx in range(-eraser_size, eraser_size):
                    for dy in range(-eraser_size, eraser_size):
                        distance = (dx ** 2 + dy ** 2) ** 0.5
                        if distance <= eraser_size:
                            px = x + dx
                            py = y + dy

                            if 0 <= px < self.pil_image.width and 0 <= py < self.pil_image.height:
                                # Récupérer le pixel de l'image de fond
                                bg_pixel = self.background_image.getpixel((px, py))
                                self.pil_image.putpixel((px, py), bg_pixel)
            else:
                # Si pas d'image de fond, effacer en blanc
                self.draw.ellipse(
                    [x - self.spray_size, y - self.spray_size,
                     x + self.spray_size, y + self.spray_size],
                    fill='white'
                )
        else:
            # Mode peinture : créer l'effet spray avec des particules aléatoires
            num_particles = int(self.spray_size / 2)  # Nombre de particules

            # Créer une image temporaire pour le spray avec canal alpha
            spray_layer = Image.new('RGBA', self.pil_image.size, (0, 0, 0, 0))
            spray_draw = ImageDraw.Draw(spray_layer)

            rgb_color = self.hex_to_rgb(self.spray_color)

            for _ in range(num_particles):
                # Position aléatoire autour du curseur
                offset_x = random.randint(-self.spray_size, self.spray_size)
                offset_y = random.randint(-self.spray_size, self.spray_size)

                # Distance du centre (pour effet circulaire)
                distance = (offset_x ** 2 + offset_y ** 2) ** 0.5

                if distance <= self.spray_size:
                    px = x + offset_x
                    py = y + offset_y

                    # Taille aléatoire des particules
                    particle_size = random.randint(1, 3)

                    # Opacité basée sur la distance (effet spray) multipliée par l'opacité globale
                    distance_opacity = int(255 * (1 - distance / self.spray_size))
                    final_opacity = int(distance_opacity * (self.spray_opacity / 100.0))

                    color_with_opacity = rgb_color + (final_opacity,)

                    # Dessiner la particule sur la couche spray
                    if 0 <= px < spray_layer.width and 0 <= py < spray_layer.height:
                        spray_draw.ellipse(
                            [px - particle_size, py - particle_size,
                             px + particle_size, py + particle_size],
                            fill=color_with_opacity
                        )

            # Convertir l'image PIL en RGBA si nécessaire
            if self.pil_image.mode != 'RGBA':
                self.pil_image = self.pil_image.convert('RGBA')

            # Composer la couche spray sur l'image principale
            self.pil_image = Image.alpha_composite(self.pil_image, spray_layer)

            # Convertir en RGB pour l'affichage
            self.pil_image = self.pil_image.convert('RGB')
            self.draw = ImageDraw.Draw(self.pil_image)

        # Mettre à jour l'affichage toutes les quelques particules pour la fluidité
        if random.random() < 0.3:  # 30% du temps
            self.update_canvas()

    def stop_spray(self, event):
        """Arrêter de dessiner"""
        self.drawing = False

        # Arrêter le son
        if self.sound_channel:
            self.sound_channel.stop()

        # Mise à jour finale
        self.update_canvas()

        # Réafficher la cible après le dessin
        self.update_preview(event)

    def update_canvas(self):
        """Mettre à jour l'affichage du canvas"""
        self.canvas_image = ImageTk.PhotoImage(self.pil_image)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.canvas_image)

    def clear_canvas(self):
        """Effacer le canvas"""
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment tout effacer ?"):
            canvas_width = self.pil_image.width
            canvas_height = self.pil_image.height
            self.pil_image = Image.new('RGB', (canvas_width, canvas_height), 'white')
            self.draw = ImageDraw.Draw(self.pil_image)

            # Réinitialiser l'historique
            self.history = []
            self.save_state()

            self.update_canvas()

    def save_image(self):
        """Sauvegarder l'image"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("All Files", "*.*")]
        )

        if file_path:
            try:
                self.pil_image.save(file_path)
                messagebox.showinfo("Succès", f"Image sauvegardée :\n{file_path}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de sauvegarder:\n{e}")

    def hex_to_rgb(self, hex_color):
        """Convertir couleur hexadécimale en RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

    def toggle_fullscreen(self):
        """Basculer le mode plein écran"""
        current = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not current)

    def quit_app(self):
        """Quitter l'application"""
        if messagebox.askyesno("Quitter", "Voulez-vous vraiment quitter ?"):
            pygame.mixer.quit()
            self.root.quit()


def main():
    root = tk.Tk()
    app = SprayPaintApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()