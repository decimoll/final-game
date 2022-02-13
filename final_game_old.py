import pyxel
import math
import random

score = 0
is_ingame = True
class Ball:
  def __init__(self):
     self.x = random.randint(0, 159)
     self.y = random.randint(-100, 0)
     #angle = math.radians(random.randint(30, 150))
     angle = math.radians(90)
     self.vx = math.cos(angle)
     self.vy = math.sin(angle)
     self.direction = 1

  def move(self):
     global score, is_ingame
     self.x += self.vx * self.direction * 3 * is_ingame
     self.y += self.vy * self.direction * 3 * is_ingame
     if self.x >= 160 or self.x <= 0:
       self.direction = self.direction * (-1)
     if self.y >= 100:
       self.x = random.randint(0, 159)
       self.y = random.randint(-100, 0)
       score += 1

class App:
    def __init__(self):
        pyxel.init(160, 100, caption="ぶろっくくずしではありません")
        pyxel.image(0).load(0, 0, "assets/cat_16x16.png")
        #pyxel.image(1).load(0, 0, "assets/cat_16x16.png")

        # Starting Point
        self.player_x = 64
        self.player_y = 80

        self.balls = []
        for i in range(0, 12):
            self.balls.append(Ball())

        pyxel.run(self.update, self.draw)

    def update(self):
        global score, is_ingame
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        if pyxel.btnp(pyxel.KEY_ENTER):
            is_ingame = True
            score = 0
        self.update_player()
        self.update_balls()

    def update_player(self):
        if is_ingame:
            if pyxel.btn(pyxel.KEY_LEFT):
                self.player_x = max(self.player_x - 2, 0)

            if pyxel.btn(pyxel.KEY_RIGHT):
                self.player_x = min(self.player_x + 2, pyxel.width - 16)

    def update_balls(self):
        global is_ingame
        for b in self.balls:
            b.move()
            if abs(b.x - (self.player_x + 8)) < 11 and abs(b.y - (self.player_y + 8)) < 10:
                is_ingame = False

    def draw(self):
        global score

        pyxel.cls(0)

        # プレイヤー(猫)を描画
        pyxel.blt(
            self.player_x,
            self.player_y,
            0,
            0,
            0,
            16,
            16,
            13, # ここを13にすると透過色が13の色になって消える
        )

        for b in self.balls:
            pyxel.circ(b.x, b.y, 4, 2)

        pyxel.text(25, 20, str(score), 10)
        if not is_ingame:
            pyxel.text(34, 30, 'GAME OVER\n\nPRESS ENTER TO TRY AGAIN\n\nPRESS ESC TO QUIT', 8)

App()
