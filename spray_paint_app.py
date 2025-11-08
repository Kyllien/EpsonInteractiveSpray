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
        self.background_image = None
        self.canvas_image = None
        self.drawing = False
        self.spray_sound = None
        self.sound_channel = None
        
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
                            bg='#4a4a4a', fg='white', font=('Arial', 12, 'bold'),
                            padx=15, pady=10, cursor='hand2')
        btn_load.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Bouton choix couleur
        self.color_btn = tk.Button(toolbar, text="🎨 Couleur", 
                                   command=self.choose_color,
                                   bg=self.spray_color, fg='white', 
                                   font=('Arial', 12, 'bold'),
                                   padx=15, pady=10, cursor='hand2',
                                   width=10)
        self.color_btn.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Label et slider pour la taille
        tk.Label(toolbar, text="Taille:", bg='#1e1e1e', fg='white', 
                font=('Arial', 11)).pack(side=tk.LEFT, padx=(20, 5))
        
        self.size_var = tk.IntVar(value=self.spray_size)
        size_slider = tk.Scale(toolbar, from_=5, to=100, orient=tk.HORIZONTAL,
                              variable=self.size_var, command=self.update_spray_size,
                              bg='#4a4a4a', fg='white', highlightthickness=0,
                              length=200, width=20)
        size_slider.pack(side=tk.LEFT, padx=5, pady=10)
        
        self.size_label = tk.Label(toolbar, text=f"{self.spray_size}px", 
                                   bg='#1e1e1e', fg='white', font=('Arial', 11),
                                   width=6)
        self.size_label.pack(side=tk.LEFT, padx=5)
        
        # Bouton charger son
        btn_load_sound = tk.Button(toolbar, text="🔊 Charger Son", 
                                   command=self.load_sound,
                                   bg='#4a4a4a', fg='white', font=('Arial', 12, 'bold'),
                                   padx=15, pady=10, cursor='hand2')
        btn_load_sound.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Bouton effacer
        btn_clear = tk.Button(toolbar, text="🗑️ Effacer", 
                             command=self.clear_canvas,
                             bg='#ff4444', fg='white', font=('Arial', 12, 'bold'),
                             padx=15, pady=10, cursor='hand2')
        btn_clear.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Bouton sauvegarder
        btn_save = tk.Button(toolbar, text="💾 Sauvegarder", 
                            command=self.save_image,
                            bg='#44ff44', fg='black', font=('Arial', 12, 'bold'),
                            padx=15, pady=10, cursor='hand2')
        btn_save.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Bouton quitter
        btn_quit = tk.Button(toolbar, text="❌ Quitter", 
                            command=self.quit_app,
                            bg='#ff8844', fg='white', font=('Arial', 12, 'bold'),
                            padx=15, pady=10, cursor='hand2')
        btn_quit.pack(side=tk.RIGHT, padx=10, pady=10)
        
        # Canvas pour dessiner
        self.canvas = tk.Canvas(main_frame, bg='white', cursor='crosshair')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Événements de dessin
        self.canvas.bind('<Button-1>', self.start_spray)
        self.canvas.bind('<B1-Motion>', self.spray_paint)
        self.canvas.bind('<ButtonRelease-1>', self.stop_spray)
        
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
                
                self.draw = ImageDraw.Draw(self.pil_image)
                
                # Afficher sur le canvas
                self.update_canvas()
                
                messagebox.showinfo("Succès", "Image chargée avec succès !")
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de charger l'image:\n{e}")
    
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
        self.spray_paint(event)
        
        # Jouer le son en boucle
        if self.spray_sound:
            self.sound_channel = self.spray_sound.play(loops=-1)
    
    def spray_paint(self, event):
        """Dessiner avec effet spray"""
        if not self.drawing:
            return
        
        x, y = event.x, event.y
        
        # Créer l'effet spray avec des particules aléatoires
        num_particles = int(self.spray_size / 2)  # Nombre de particules
        
        for _ in range(num_particles):
            # Position aléatoire autour du curseur
            offset_x = random.randint(-self.spray_size, self.spray_size)
            offset_y = random.randint(-self.spray_size, self.spray_size)
            
            # Distance du centre (pour effet circulaire)
            distance = (offset_x**2 + offset_y**2) ** 0.5
            
            if distance <= self.spray_size:
                px = x + offset_x
                py = y + offset_y
                
                # Taille aléatoire des particules
                particle_size = random.randint(1, 3)
                
                # Opacité variable (plus faible sur les bords)
                opacity = int(255 * (1 - distance / self.spray_size))
                color_with_opacity = self.hex_to_rgb(self.spray_color) + (opacity,)
                
                # Dessiner la particule
                if 0 <= px < self.pil_image.width and 0 <= py < self.pil_image.height:
                    self.draw.ellipse(
                        [px-particle_size, py-particle_size, 
                         px+particle_size, py+particle_size],
                        fill=color_with_opacity
                    )
        
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
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
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
