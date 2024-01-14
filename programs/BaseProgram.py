import machine

class BaseProgram:
    def __init__(self, jacc_os, fb):
        self.jacc_os = jacc_os
        self.fb = fb
        self.fb.fill(0) # clear window display
        self.update() # update display with cleared image
        self.timer = machine.Timer() # main timer for periodic application activities (automatically deinit'd)
    def update(self):
        self.jacc_os._draw_buffer(self.fb)
    def _exit(self):
        self.timer.deinit() # deinit timer
        self.fb.fill(0)
        self.update()
        del self.fb
        try:
            self.exit() # attempt graceful exit if supported
        except NotImplementedError:
            pass # graceful exit not implemented
    def register_keymap(self, keymap):
        self.jacc_os.register_keymap(keymap)
    def exit(self):
        raise NotImplementedError
    def on_keypress(self, key, press_type, p_id):
        raise NotImplementedError
    def pause(self):
        raise NotImplementedError
    def resume(self):
        raise NotImplementedError

