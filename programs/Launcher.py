from programs.BaseProgram import BaseProgram
import machine
import program_manager

def color(r, g, b):
    r,g,b = int(r/4),int(g/4),int(b/4)
    return (r << 12) + (g << 6) + b

class Program(BaseProgram):
    program_list = [("Calculator", "SimpleCalculator"), ("Pong", "Pong")] # ("LABEL", "PROGRAM")
    def run(self):
        self.register_keymap([{
                "a": "1", "b": "2", "c": "3",
                "d": "4", "e": "5", "f": "6",
                "g": None, "h": None, "i": None,
                "j": None, "k": "PREV", "l": "NEXT",
            }])
        self.draw()
    def draw(self):
        self.curr_program_list = self.program_list[:6]
        for i, program in enumerate(self.program_list):
            self.fb.text(program[0], 0, 5+10*i, color(255, 255, 255))
        self.update()
    def on_keypress(self, key, _press_type, _p_id):
        if key in "123456":
            program_index = int(key)-1
            if program_index >= len(self.program_list):
                return
            program = program_manager.load_program(self.program_list[program_index][1])
            self.jacc_os.run_program(program)
        