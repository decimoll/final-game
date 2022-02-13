import pyxel
import math
import random
from enum import IntEnum, auto


score = 0


class Gamemode(IntEnum):
    TITLE = auto()
    MAIN = auto()
    HIGHSCORE = auto()
    END = auto()



class Level():
    EASY = 0
    NORMAL = 1
    HARD = 2



class Ball:
    def __init__(self, level):
        self.init(level)


    # 初期化する
    def init(self, level):
        self.x = random.randint(0, 159)
        self.y = random.randint(-100, -1)
        if level == Level.EASY or level == Level.NORMAL:
            self.angle = math.radians(90)
            self.life = 1
        elif level == Level.HARD:
            self.angle = math.radians(random.randint(75, 105))
            self.life = 1
        self.vx = math.cos(self.angle)
        self.vy = math.sin(self.angle)


    # 動く
    def move(self, px, py, level):
        global score

        self.x += self.vx * 3
        self.y += self.vy * 3

        if self.x < 0 or self.x > 159:
            self.init(level)
        if self.y >= 100:
            self.init(level)
            score += 1

        # 猫に当たったらゲームオーバーでTrueを返す
        if abs(self.x - (px + 8)) <= 10 and abs(self.y - (py + 8)) <= 9:
            return True

        return False



class Bullet:
    def __init__(self, _x, _y):
        self.x = _x
        self.y = _y
        angle = math.radians(270)
        self.vx = math.cos(angle)
        self.vy = math.sin(angle)
        
        # 弾を撃ったときの効果音
        pyxel.play(3, 9, loop=False)


    # 戻り値  False: 何もなかった True: 画面外に出た or ボールに当たった(つまり消滅した)
    def move(self, balls, level):
        global score

        self.x += self.vx * 5
        self.y += self.vy * 5

        if self.y < 0:
            return True

        for b in balls:
            # ボールと衝突
            if abs(self.x - b.x) <= 5 and abs(self.y - b.y) <= 5:
                b.life -= 1
                # ボール消滅
                if b.life == 0:
                    pyxel.play(3, 8, loop=False)
                    b.init(level)
                    if level == Level.EASY:
                        score += 1
                    elif level == Level.HARD:
                        score -= 5
                return True

        return False
        


class Player:   # ねこ
    def __init__(self):        
        pyxel.image(0).load(0, 0, "./assets/cat_16x16.png")
        self.init()


    # 初期化する
    def init(self):
        self.x = 64
        self.y = 80
        self.direction = 1  # 右向が-1 左向が1


    # Shiftキーを押しながらだと低速に動く
    def move(self):
        if pyxel.btn(pyxel.KEY_LEFT):
            self.direction = 1
            if pyxel.btn(pyxel.KEY_LSHIFT):
                self.x = max(self.x - 1, 0)
            else:
                self.x = max(self.x - 2, 0)

        if pyxel.btn(pyxel.KEY_RIGHT):
            self.direction = -1
            if pyxel.btn(pyxel.KEY_LSHIFT):
                self.x = min(self.x + 1, pyxel.width - 16)
            else:
                self.x = min(self.x + 2, pyxel.width - 16)



class App:
    def __init__(self):
        pyxel.init(160, 100, title='final game')

        # ハイスコア記録ファイルの存在チェック 無ければ作る
        try:
            with open('./highscore.txt', 'x', encoding='utf-8') as f:
                for i in range(6):
                    if i % 2:
                        f.write('0\n')
                    else:
                        f.write('...\n')
        except FileExistsError:
            pass
        # ハイスコアを読み取り 奇数行目がeasy, normal, hardの難易度，偶数行目にそれぞれの難易度のスコアが記載されている
        with open('./highscore.txt', encoding='utf-8') as f:
            self.highscores = [s.strip() for s in f.readlines()]

        self.gamemode = Gamemode.TITLE
        self.level = Level.EASY
        self.player = Player()
        self.balls = []
        self.bullets = []

        # 音楽を読み込み
        pyxel.load('./assets/resource.pyxres', False, False, True, True)
        # 基本BGMを再生
        pyxel.playm(0, loop=True)

        pyxel.run(self.update, self.draw)


    # タイトル画面へ遷移する
    def to_title(self):
        global score
        if self.gamemode == Gamemode.MAIN or self.gamemode == Gamemode.HIGHSCORE or self.gamemode == Gamemode.END:
            for b in self.balls:
                del b
            self.balls = []
            for bu in self.bullets:
                del bu
            self.bullets = []
            score = 0
            if self.gamemode != Gamemode.MAIN:
                pyxel.playm(0, loop=True)

            with open('./highscore.txt', encoding='utf-8') as f:
                self.highscores = [s.strip() for s in f.readlines()]
            self.gamemode = Gamemode.TITLE


    # ゲームメイン画面へ遷移する
    def to_main(self):
        global score
        if self.gamemode == Gamemode.TITLE:
            self.balls = []
            if self.level == Level.EASY:
                qty = 6
            elif self.level == Level.NORMAL or self.level == Level.HARD:
                qty = 12
            # ボールをqty個生成
            for i in range(qty):
                self.balls.append(Ball(self.level))            
            
            # ゲームの状態の遷移
            self.gamemode = Gamemode.MAIN

        elif self.gamemode == Gamemode.MAIN or self.gamemode == Gamemode.HIGHSCORE or self.gamemode == Gamemode.END:
            self.player.init()
            for b in self.balls:
                b.init(self.level)
            for bu in self.bullets:
                del bu
            self.bullets = []
            score = 0
            if self.gamemode != Gamemode.MAIN:
                pyxel.playm(0, loop=True)
            with open('./highscore.txt', encoding='utf-8') as f:
                self.highscores = [s.strip() for s in f.readlines()]
            self.gamemode = Gamemode.MAIN

    
    # ハイスコア画面へ遷移する
    def to_highscore(self):
        global score
        if self.gamemode == Gamemode.MAIN:
            # ゲームオーバー音楽を再生
            pyxel.stop()
            pyxel.playm(3, loop=False)
            self.gamemode = Gamemode.END

            self.highscores[self.level * 2] =''
            self.highscores[self.level * 2 + 1] = str(score)            
            self.gamemode = Gamemode.HIGHSCORE
            

    # ゲームオーバー画面へ遷移する
    def to_end(self):
        global score        
        if self.gamemode == Gamemode.MAIN or self.gamemode == Gamemode.HIGHSCORE:
            if self.gamemode != Gamemode.HIGHSCORE:            
                # ゲームオーバー音楽を再生
                pyxel.stop()
                pyxel.playm(3, loop=False)
            self.gamemode = Gamemode.END


    # ゲームの状態(Gamemode)によってupdate関数を分離
    def update(self):
        if self.gamemode == Gamemode.TITLE:
            self.update_title()
        elif self.gamemode == Gamemode.MAIN:
            self.update_main()
        elif self.gamemode == Gamemode.HIGHSCORE:
            self.update_highscore()
        elif self.gamemode == Gamemode.END:
            self.update_end()


    # タイトル画面の処理
    def update_title(self):
        # 難易度選択
        if self.level > 0 and pyxel.btnp(pyxel.KEY_UP):
            self.level -= 1
        if self.level < 2 and pyxel.btnp(pyxel.KEY_DOWN):
            self.level += 1

        # 開始するキー(SpaceまたはEnter)が押された
        if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_RETURN):
            self.to_main()


    # ゲーム画面の処理
    def update_main(self):
        global score

        # 弾を撃つ 難易度により一度に画面に表示できる弾数を制限
        if pyxel.btnp(pyxel.KEY_Z):
            if self.level == Level.EASY:
                qty = 3
            elif self.level == Level.NORMAL:
                qty = 2
            elif self.level == Level.HARD:
                qty = 1
            if len(self.bullets) < qty:
                # 猫の両耳の間から弾が出るようにする
                if self.player.direction == 1:
                    self.bullets.append(Bullet(self.player.x + 6, self.player.y + 1))
                else:
                    self.bullets.append(Bullet(self.player.x + 9, self.player.y + 1))
        
        # プレイヤーを動かす
        self.player.move()

        # ボールを動かす Ball.move()の戻り値によってゲームオーバーか判断
        for b in self.balls:
            if b.move(self.player.x, self.player.y, self.level):
                if score > int(self.highscores[self.level * 2 + 1]):
                    self.to_highscore()
                else:
                    self.to_end()
        
        # 弾を動かす Bullet.move()の戻り値によっては弾を消滅させる
        i = 0
        while (i < len(self.bullets)):
            if self.bullets[i].move(self.balls, self.level):
                del self.bullets[i]
            else:
                i += 1

        # Enterキーはタイトル画面へ戻る
        if pyxel.btnp(pyxel.KEY_RETURN):
            self.to_title()

        # Spaceキーは同じ難易度で再挑戦
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.to_main()


    # ハイスコアであるときに名前入力のための関数
    def input_highscore_name(self):
        if len(self.highscores[self.level * 2]) < 3:
            # AからZまで入力可
            for i in range(18, 44):
                if pyxel.btnp(i):
                    self.highscores[self.level * 2] += chr(i + 47)

        # Backspaceで1文字削除
        if pyxel.btnp(pyxel.KEY_BACKSPACE):
            self.highscores[self.level * 2] = self.highscores[self.level * 2][:-1]


    # ハイスコア時の処理
    def update_highscore(self):
        self.input_highscore_name()
        # 入力された文字数が3文字で，なおかつEnterキーが押されたら書き込み
        if len(self.highscores[self.level * 2]) == 3 and pyxel.btnp(pyxel.KEY_RETURN):
            with open('./highscore.txt', 'w', encoding='utf-8') as f:
                for s in self.highscores:
                    f.write(s + '\n')
            self.to_end()

        # Spaceキーは同じ難易度で再挑戦
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.to_main()


    # ゲームオーバー時の処理
    def update_end(self):
        global score
        # Enterキーはタイトル画面へ戻る
        if pyxel.btnp(pyxel.KEY_RETURN):
            self.to_title()

        # Spaceキーは同じ難易度で再挑戦
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.to_main()


    # update()と同様，ゲームの状態によって分離
    def draw(self):
        if self.gamemode == Gamemode.TITLE:            
            self.draw_title()
        elif self.gamemode == Gamemode.MAIN:
            self.draw_main()
        elif self.gamemode == Gamemode.HIGHSCORE:
            self.draw_highscore()
        elif self.gamemode == Gamemode.END:
            self.draw_end()


    # タイトル画面の描画
    def draw_title(self):
        pyxel.cls(0)

        pyxel.text(50, 20, 'THE FINAL GAME', 7)

        pyxel.text(38, 45, 'EASY', 3)
        pyxel.text(38, 55, 'NORMAL', 9)
        pyxel.text(38, 65, 'HARD', 8)

        # 難易度選択のカーソル
        if self.level == Level.EASY:
            pyxel.circ(33, 47, 2, 7)
        elif self.level == Level.NORMAL:
            pyxel.circ(33, 57, 2, 7)
        elif self.level == Level.HARD:
            pyxel.circ(33, 67, 2, 7)

        pyxel.text(86, 35, 'HIGHSCORE', 10)
        pyxel.text(90, 45, self.highscores[0] + ' ' + self.highscores[1], 10)
        pyxel.text(90, 55, self.highscores[2] + ' ' + self.highscores[3], 10)
        pyxel.text(90, 65, self.highscores[4] + ' ' + self.highscores[5], 10)


    # ゲーム画面の描画
    def draw_main(self):
        global score

        pyxel.cls(0)

        # プレイヤー(猫)を描画
        pyxel.blt(
            self.player.x,
            self.player.y,
            0,
            0,
            0,
            16 * self.player.direction,    # 負の数だと水平反転
            16,
            13, # ここを13にすると13の色が透過色になって消える
        )

        # ボールを描画
        for b in self.balls:
            pyxel.circ(b.x, b.y, 4, 2)
            pyxel.circb(b.x, b.y, 4, 1)

        # 弾を描画
        for bu in self.bullets:
            pyxel.circ(bu.x, bu.y, 1, 9)

        # スコアの表示
        pyxel.text(25, 20, str(score), 10)


    # ハイスコア時の画面描画
    def draw_highscore(self):
        pyxel.rect(0, 40, 160, 25, 0)
        pyxel.text(34, 30, 'GAME OVER', 8)
        pyxel.text(34, 40, 'YOUR SCORE IS THE HIGHSCORE', 8)
        pyxel.text(34, 50, 'ENTER YOUR NAME 3 MOJI DE', 8)
        pyxel.text(34, 60, self.highscores[self.level * 2], 8)
        

    # ゲームオーバ時の画面描画
    def draw_end(self):
        pyxel.rect(0, 40, 160, 25, 0)
        pyxel.text(34, 30, 'GAME OVER', 8)
        pyxel.text(34, 40, 'PRESS SPACE TO TRY AGAIN', 8)
        pyxel.text(34, 50, 'PRESS ENTER TO BACK TO TITLE', 8)
        pyxel.text(34, 60, 'PRESS ESC TO QUIT', 8)



App()
