class RotateEncoderHandler:
    def __init__(self, hardware, сw_rotate_callback, cсw_rotate_callback):
        self.hardware = hardware
        self.сw_rotate_callback = сw_rotate_callback
        self.сww_rotate_callback = cсw_rotate_callback

        self.last_position = self.hardware.get_encoder().position

    def update(self):
        position = self.hardware.get_encoder().position


        if position != self.last_position:
            print(self.hardware.get_encoder().position)
            if position > self.last_position:
                self.сw_rotate_callback()
            else:
                self.сww_rotate_callback()

            self.last_position = position
