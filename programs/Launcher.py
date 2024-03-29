from programs.BaseProgram import BaseProgram
import machine
import program_manager

def color(r, g, b):
    return ((b//8 & 0xF8) << 8) | ((r//8 & 0xFC) << 3) | (g//4 >> 3)

class Program(BaseProgram):
    options_list = [("Calculator", "SimpleCalculator"), ("Pong", "Pong"), ("Home Control", "HomeControl"), ("Settings", "Settings")]
    # ("LABEL", "PROGRAM")
    ELEMENTS_PER_PAGE = 7
    def run(self):
        self.register_keymap([{
                "a": None, "b": "SELECT", "c": ("UP", "TOP"),
                "d": None, "e": None, "f": ("DOWN", "BOTTOM"),
                "g": None, "h": None, "i": None,
                "j": None, "k": None, "l": None,
            }])
        self.selector = 0
        self.show_options_index = 0
        self.draw()
    def draw(self):
        self.fb.fill(0)
        #offset = min(0, self.selector-ELEMENTS_PER_PAGE+1)
        for i, setting in enumerate(self.options_list[self.show_options_index:self.show_options_index+self.ELEMENTS_PER_PAGE]):
            self.fb.text(setting[0], 2, 8+16*i, color(255, 255, 255))
        relative_selected_option = self.selector-self.show_options_index
        self.fb.rect(0, 4+16*relative_selected_option, 127, 16, color(112, 128, 144))
        self.update()
    def on_keypress(self, key, _press_type, _p_id):
        if key in ["UP", "DOWN"]:
            if key == "UP":
                if self.selector == 0:
                    self.selector = 0
                else:
                    self.selector -= 1
            elif key == "DOWN":
                if self.selector+1 == len(self.options_list):
                    self.selector = len(self.options_list)-1
                else:
                    self.selector += 1
            if self.selector < self.show_options_index:
                self.show_options_index -= 1
            elif self.selector >= self.show_options_index+self.ELEMENTS_PER_PAGE:
                self.show_options_index += 1
            self.draw()
        elif key == "TOP":
            self.selector = 0
            self.show_options_index = 0
            self.draw()
        elif key == "BOTTOM":
            self.selector = len(self.options_list)-1
            self.show_options_index = max(0, len(self.options_list)-self.ELEMENTS_PER_PAGE)
            self.draw()
        elif key == "SELECT":
            selection = self.options_list[self.selector][1]
            program = program_manager.load_program(selection)
            self.jacc_os.run_program(program)
        