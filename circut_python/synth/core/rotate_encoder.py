def void_handler():
    pass

class RotateEncoderHandler:
    def __init__(self, hardware, сw_rotate_callback, cсw_rotate_callback, button_press_callback = void_handler) :
        self.hardware = hardware
        self.сw_rotate_callback = сw_rotate_callback
        self.сww_rotate_callback = cсw_rotate_callback
        self.button_press_callback = button_press_callback

        self.last_position = self.hardware.get_encoder().position

        self.prev_button_value = False

    def update(self):
        position = self.hardware.get_encoder().position
        button_value = not self.hardware.get_encoder_button().value
        # print(button_value)

        if self.prev_button_value != button_value and button_value == True:
            self.button_press_callback()
            self.prev_button_value = button_value
        if self.prev_button_value != button_value and button_value == False:
            self.prev_button_value = button_value

        if position != self.last_position:
            if position > self.last_position:
                self.сw_rotate_callback()
            else:
                self.сww_rotate_callback()

            self.last_position = position
