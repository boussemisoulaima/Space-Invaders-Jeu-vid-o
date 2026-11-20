'''
@author: Soulaima boussemi Lisa brahmi
''' 
import tkinter as tk
from tkinter import messagebox
import os


# ===================== Classe Bullet =====================
class Bullet:
    def __init__(self, shooter):
        self.radius = 4
        self.color = "red"
        self.speed = 10
        self.id = None
        self.shooter = shooter

    def install_in(self, canvas):
        self.canvas = canvas
        x1, y1, x2, y2 = canvas.coords(self.shooter.id)
        cx = (x1 + x2) / 2
        cy = y1
        self.id = canvas.create_oval(
            cx - self.radius, cy - 2 * self.radius,
            cx + self.radius, cy,
            fill=self.color, outline=self.color
        )

    def move_in(self):
        self.canvas.move(self.id, 0, -self.speed)
        x1, y1, x2, y2 = self.canvas.coords(self.id)

        if y2 <= 0:
            self.canvas.delete(self.id)
            self.id = None
            self.shooter.remove_bullet(self)


# ===================== Classe Alien =====================
class Alien:
    def __init__(self, image):
        self.image = image
        self.id = None
        self.alive = True

    def install_in(self, canvas, x, y):
        self.canvas = canvas
        self.id = canvas.create_image(x, y, image=self.image)

    def move_in(self, dx, dy):
        if self.alive:
            self.canvas.move(self.id, dx, dy)

    def get_coords(self):
        return self.canvas.bbox(self.id)

    def destroy(self):
        self.canvas.delete(self.id)
        self.alive = False


# ===================== Classe Fleet =====================
class Fleet:
    def __init__(self, canvas_width):
        self.aliens = []
        self.direction = 1
        self.speed_x = 5
        self.step_down = 20
        self.canvas_width = canvas_width
        self.alien_image = None
        self.canvas = None

    def install_in(self, canvas):
        self.canvas = canvas
        self.alien_image = tk.PhotoImage(file="alien.gif")

        img_w = self.alien_image.width()
        img_h = self.alien_image.height()

        rows = 3
        cols = 8
        gap_x = 10
        gap_y = 20

        total_width = cols * img_w + (cols - 1) * gap_x
        start_x = max(0, (self.canvas_width - total_width) // 2)
        start_y = 60

        for i in range(rows):
            for j in range(cols):
                alien = Alien(self.alien_image)
                x = start_x + j * (img_w + gap_x)
                y = start_y + i * (img_h + gap_y)
                alien.install_in(canvas, x, y)
                self.aliens.append(alien)

    def move_in(self):
        dx = self.direction * self.speed_x

        need_to_go_down = False
        for alien in self.aliens:
            coords = alien.get_coords()
            if coords is None:
                continue
            x1, y1, x2, y2 = coords
            if x2 + dx >= self.canvas_width or x1 + dx <= 0:
                need_to_go_down = True
                break

        if need_to_go_down:
            self.direction *= -1
            for alien in self.aliens:
                if alien.alive:
                    alien.move_in(0, self.step_down)

        dx = self.direction * self.speed_x
        for alien in self.aliens:
            if alien.alive:
                alien.move_in(dx, 0)

    def get_bottom_y(self):
        max_y = 0
        for alien in self.aliens:
            if alien.alive:
                x1, y1, x2, y2 = alien.get_coords()
                if y2 > max_y:
                    max_y = y2
        return max_y

    def manage_collisions_with(self, bullet):
        if bullet.id is None:
            return False

        bx1, by1, bx2, by2 = self.canvas.coords(bullet.id)

        for alien in self.aliens:
            if not alien.alive:
                continue
            coords = alien.get_coords()
            if coords is None:
                continue

            x1, y1, x2, y2 = coords

            overlap = not (bx2 < x1 or bx1 > x2 or by2 < y1 or by1 > y2)

            if overlap:
                alien.destroy()

                explosion = self.canvas.create_oval(
                    bx1 - 5, by1 - 5, bx2 + 5, by2 + 5,
                    fill="yellow", outline="yellow"
                )
                self.canvas.after(100, lambda: self.canvas.delete(explosion))

                self.canvas.delete(bullet.id)
                bullet.id = None

                bullet.shooter.remove_bullet(bullet)

                return True

        return False


# ===================== Classe Defender =====================
class Defender:
    def __init__(self, canvas_width, canvas_height):
        self.width = 20
        self.height = 20
        self.move_delta = 20
        self.id = None
        self.canvas = None
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height

        self.max_bullets = 8
        self.bullets = []

    def install_in(self, canvas):
        self.canvas = canvas
        x = self.canvas_width // 2
        y = self.canvas_height - 50
        self.id = canvas.create_rectangle(
            x - self.width // 2, y - self.height // 2,
            x + self.width // 2, y + self.height // 2,
            fill="white"
        )

    def move_in(self, event):
        x1, y1, x2, y2 = self.canvas.coords(self.id)

        if event.keysym == "Left":
            if x1 - self.move_delta < 0:
                self.canvas.move(self.id, -x1, 0)
            else:
                self.canvas.move(self.id, -self.move_delta, 0)

        elif event.keysym == "Right":
            if x2 + self.move_delta > self.canvas_width:
                self.canvas.move(self.id, self.canvas_width - x2, 0)
            else:
                self.canvas.move(self.id, self.move_delta, 0)

        elif event.keysym == "space":
            self.fire()

    def fire(self):
        if len(self.bullets) >= self.max_bullets:
            return

        b = Bullet(self)
        b.install_in(self.canvas)
        self.bullets.append(b)

    def remove_bullet(self, bullet):
        if bullet in self.bullets:
            self.bullets.remove(bullet)

    def get_top_y(self):
        x1, y1, x2, y2 = self.canvas.coords(self.id)
        return y1


# ===================== Classe Game =====================
class Game:
    def __init__(self, frame, scores, player_name):
        self.frame = frame
        self.width = 800
        self.height = 600

        self.canvas = tk.Canvas(self.frame, width=self.width, height=self.height, bg="black")
        self.canvas.pack()

        self.scores = scores
        self.player_name = player_name
        self.score = 0

        self.score_text_id = self.canvas.create_text(
            40, 10,
            fill="white",
            text=f"Score : {self.score}"
        )

        self.defender = Defender(self.width, self.height)
        self.defender.install_in(self.canvas)

        self.fleet = Fleet(self.width)
        self.fleet.install_in(self.canvas)

        self.running = True

    def update_score_text(self):
        self.canvas.itemconfig(self.score_text_id, text=f"Score : {self.score}")

    def animation(self):
        if not self.running:
            return

        self.move_bullets()
        self.fleet.move_in()
        self.check_victory()
        self.check_game_over()

        self.canvas.after(30, self.animation)

    def move_bullets(self):
        for b in list(self.defender.bullets):
            b.move_in()
            touche = self.fleet.manage_collisions_with(b)
            if touche:
                self.score += 10
                self.update_score_text()

    def sauvegarder_scores(self):
        self.scores[self.player_name] = self.score

        with open("scores.txt", "w", encoding="utf-8") as f:
            for nom, sc in self.scores.items():
                f.write(f"{nom};{sc}\n")

    def check_game_over(self):
        bottom_fleet = self.fleet.get_bottom_y()
        defender_top = self.defender.get_top_y()

        if bottom_fleet >= defender_top:
            self.running = False
            self.sauvegarder_scores()
            messagebox.showinfo("Perdu", "Les aliens t'ont envahi !")

    def check_victory(self):
        for alien in self.fleet.aliens:
            if alien.alive:
                return

        self.running = False
        self.sauvegarder_scores()
        messagebox.showinfo("Gagné", "Bravo, tu as détruit tous les aliens !")


# ===================== Classe SpaceInvaders =====================
class SpaceInvaders:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Space Invaders")

        self.scores = {}
        if os.path.exists("scores.txt"):
            with open("scores.txt", "r") as f:
                for line in f:
                    name, score_str = line.strip().split(";")
                    self.scores[name] = int(score_str)

        self.intro_frame = tk.Frame(self.root)
        self.intro_frame.pack()

        titre = tk.Label(self.intro_frame, text="Space Invaders")
        titre.pack()

        label_scores = tk.Label(self.intro_frame, text="Scores sauvegardés :")
        label_scores.pack()

        for name, score in self.scores.items():
            tk.Label(self.intro_frame, text=f"{name} : {score}").pack()

        label_nom = tk.Label(self.intro_frame, text="Nom du joueur :")
        label_nom.pack()

        self.entree_nom = tk.Entry(self.intro_frame)
        self.entree_nom.pack()

        bouton_jouer = tk.Button(self.intro_frame, text="Commencer la partie", command=self.start_game)
        bouton_jouer.pack()

        self.frame = None
        self.game = None

    def start_game(self):
        nom = self.entree_nom.get()
        if nom == "":
            messagebox.showwarning("Nom manquant", "Veuillez entrer un nom de joueur.")
            return

        self.player_name = nom

        self.intro_frame.destroy()

        self.frame = tk.Frame(self.root)
        self.frame.pack()

        self.game = Game(self.frame, self.scores, self.player_name)

        self.root.bind("<Key>", self.game.defender.move_in)

        self.game.animation()

    def play(self):
        self.root.mainloop()


# ===================== Lancer le jeu =====================
SpaceInvaders().play()


