from programs.BaseProgram import BaseProgram

class Program(BaseProgram):
    def run(self):
        keymap = [
            {
                "a": ("1", "POWER"), "b": ("2", "*"), "c": ("3", "BK"),
                "d": ("4", "ROOT"), "e": ("5", "/"), "f": ("6", "+"),
                "g": ("7", "CLR"), "h": ("8", "UP"), "i": ("9", "-"),
                "j": None, "k": ("0", "DOWN"), "l": (".", "="),
            },
            {
                "a": "POWER", "b": "*", "c": ("BK", "CA"),
                "d": "ROOT", "e": "/", "f": "+",
                "g": "CLR", "h": "UP", "i": "-",
                "j": None, "k": "DOWN", "l": "=",
            }
        ]
        self.jacc_os.register_keymap(keymap)
        self.selector = -1
        self.number_1 = ""
        self.operation = ""
        self.number_2 = ""
        self.solution = ""
    def _evaluate(self, number_1, operation, number_2):
        if operation == "+":
            return number_1+number_2
        elif operation == "-":
            return number_1-number_2
        elif operation == "*":
            return number_1*number_2
        elif operation == "/":
            return number_1/number_2
        elif operation == "POWER":
            return number_1**number_2
        elif operation == "ROOT":
            return number_1**(1/number_2)
    def on_keypress(self, key, _press_type, _p_id):
        if key in "0123456789.":
            self.solution = ""
            if self.selector == -1 or self.selector == 0:
                if len(self.number_1) <= 14:
                    if key == ".":
                        if "." not in self.number_1:
                            self.number_1 += key
                    else:
                        self.number_1 += key
            elif self.selector == 1:
                if len(self.number_2) <= 14:
                    if key == ".":
                        if "." not in self.number_2:
                            self.number_2 += key
                    else:
                        self.number_2 += key
            elif self.operation == "":
                if len(self.number_1) <= 14:
                    if key == ".":
                        if "." not in self.number_1:
                            self.number_1 += key
                    else:
                        self.number_1 += key
            else:
                if len(self.number_2) <= 14:
                    if key == ".":
                        if "." not in self.number_2:
                            self.number_2 += key
                    else:
                        self.number_2 += key
        elif key in ["+", "-", "*", "/", "POWER", "ROOT"]:
            self.solution = ""
            if self.operation != "" and self.number_1 != "" and self.number_2 != "":
                sol = self._evaluate(float(self.number_1), self.operation, float(self.number_2))
                if int(sol) == sol:
                    sol = int(sol)
                self.solution = str(sol)
                self.number_1 = self.solution
                self.number_2 = ""
            self.operation = key
            if self.selector == -1:
                self.selector = 1
        elif key == "UP":
            self.selector = 0
        elif key == "DOWN":
            self.selector = 1
        elif key == "BK":
            self.solution = ""
            if self.selector == -1 or self.selector == 0:
                self.number_1 = self.number_1[:-1]
            elif self.selector == 1:
                if self.number_2 == "":
                    if self.operation == "":
                        self.selector = 0
                        self.number_1 = self.number_1[:-1]
                    else:
                        self.operation = ""
                else:
                    self.number_2 = self.number_2[:-1]
            elif self.operation == "":
                self.number_1 = self.number_1[:-1]
            else:
                if self.number_2 == "":
                    if self.operation == "":
                        self.selector = 0
                        self.number_1 = ""
                    else:
                        self.operation = ""
                else:
                    self.number_2 = self.number_2[:-1]
        elif key == "CA":
            self.solution = ""
            if self.selector == -1 or self.selector == 0:
                self.number_1 = ""
            elif self.selector == 1:
                if self.number_2 == "":
                    self.operation = ""
                else:
                    self.number_2 = ""
            elif self.operation == "":
                self.number_1 = ""
            else:
                if self.number_2 == "":
                    self.operation = ""
                else:
                    self.number_2 = ""
        elif key == "=":
            if self.number_1 != "" and self.number_2 != "" and self.operation != "":
                sol = self._evaluate(float(self.number_1), self.operation, float(self.number_2))
                if int(sol) == sol:
                    sol = int(sol)
                self.solution = str(sol)
                self.number_1 = self.solution
                self.number_2 = ""
        elif key == "CLR":
            self.number_1 = ""
            self.operation = ""
            self.number_2 = ""
            self.solution = ""
            self.selector = -1
        self.fb.fill(0)
        self.fb.text("{: >16}".format(self.number_1), 0, 8, 65535)
        self.fb.text("{: >16}".format(self.operation), 0, 16, 65535)
        self.fb.text("{: >16}".format(self.number_2), 0, 24, 65535)
        self.fb.text("="+"{: >15}".format(self.solution), 0, 40, 65535)
        self.update()