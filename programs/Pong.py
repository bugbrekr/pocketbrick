from programs.BaseProgram import BaseProgram
import machine

def color(r, g, b):
    return ((b//8 & 0xF8) << 8) | ((r//8 & 0xFC) << 3) | (g//4 >> 3)

class Program(BaseProgram):
    WINNING_SCORE = 1
    def real_run(self, _=None):
        self.timer.init(mode=1, freq=20, callback=self.mainloop)
    def run(self):
        self.paddle_1 = 43
        self.paddle_2 = 43
        self.reset_ball()
        self.score = [0, 0]
        self.register_keymap([{
            "l": "PAUSE"
            }])
        self.is_paused = False
        self.timer.init(mode=0, period=500, callback=self.real_run)
    def draw_screen(self, paddle_1, paddle_2, ball_pos):
        self.fb.fill(0)
        self.fb.rect(2, paddle_1, 5, 30, color(255, 255, 255), True)
        self.fb.rect(120, paddle_2, 5, 30, color(255, 255, 255), True)
        self.fb.ellipse(ball_pos[0], ball_pos[1], 2, 2, color(255, 255, 255), True)
        self.fb.text(f"{self.score[0]}:{self.score[1]}", 50, 5, color(0, 255, 127))
        self.update()
    def reset_ball(self):
        self.ball_pos = [63, 58]
        self.ball_vel = [2, 0]
    def pause(self):
        self.is_paused = True
        self.timer.deinit()
    def resume(self):
        self.is_paused = False
        self.real_run()
    def reset_game(self, _=None):
        self.paddle_1 = 43
        self.paddle_2 = 43
        self.reset_ball()
        self.score = [0, 0]
        self.timer.init(mode=0, period=500, callback=self.real_run)
    def do_ai(self):
        if self.ball_pos[0] < 100:
            if self.ball_pos[1] > self.paddle_1+20:
                self.paddle_1 += 2
            elif self.ball_pos[1] < self.paddle_1+10:
                self.paddle_1 -= 2
    def award_point(self, player):
        self.paddle_1 = 43
        self.paddle_2 = 43
        self.score[player] += 1
    def draw_game_over_screen(self, player):
        self.fb.rect(14, 28, 100, 60, color(0, 0, 0), True)
        self.fb.rect(14, 28, 100, 60, color(0, 255, 0))
        self.fb.text("GAME OVER", 28, 40, color(0, 255, 0))
        self.fb.text(f"{player} WINS!", 18, 60, color(0, 255, 0))
        self.update()
    def mainloop(self, _):
        up, down = self.jacc_os.get_button_status("c"), self.jacc_os.get_button_status("f")
        if up == 1 and down == 1:
            pass
        elif up == 1:
            if self.paddle_2 <= 0:
                self.paddle_2 = 0
            else:
                self.paddle_2 -= 3
        elif down == 1:
            if self.paddle_2 >= 87:
                self.paddle_2 = 87
            else:
                self.paddle_2 += 3
        self.ball_pos[0] = int(self.ball_pos[0]+self.ball_vel[0])
        self.ball_pos[1] = int(self.ball_pos[1]+self.ball_vel[1])
        if self.ball_pos[0] >= 118:
            if self.ball_pos[1] > self.paddle_2-4 and self.ball_pos[1] < self.paddle_2+34:
                self.ball_vel[0] *= -1
                ball_offset = (self.ball_pos[1]-self.paddle_2-15)/23
                self.ball_vel[1] = ball_offset*6
            else:
                self.reset_ball()
                self.award_point(0) # award CPU
        elif self.ball_pos[0] <= 8:
            if self.ball_pos[1] > self.paddle_1-4 and self.ball_pos[1] < self.paddle_1+34:
                self.ball_vel[0] *= -1
                ball_offset = (self.ball_pos[1]-self.paddle_1-15)/23
                self.ball_vel[1] = ball_offset*6
            else:
                self.reset_ball()
                self.award_point(1) # award player
        if self.ball_pos[1] <= 0 or self.ball_pos[1] >= 117:
            self.ball_vel[1] *= -1
        self.do_ai()
        if self.paddle_1 <= 0:
            self.paddle_1 = 0
        if self.paddle_1 >= 87:
            self.paddle_1 = 87
        self.draw_screen(self.paddle_1, self.paddle_2, self.ball_pos)
        if self.score[0] == self.WINNING_SCORE or self.score[1] == self.WINNING_SCORE:
            self.timer.deinit()
            if self.score[0] == self.WINNING_SCORE:
                player = " CPU"
            else:
                player = "PLAYER"
            self.draw_game_over_screen(player)
            self.timer.init(mode=0, period=5000, callback=self.reset_game)
    def on_keypress(self, key, _press_type, _p_id):
        if key == "PAUSE":
            if self.is_paused:
                self.resume()
            else:
                self.pause()
