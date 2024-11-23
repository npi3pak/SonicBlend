from ..core.rotate_encoder import RotateEncoderHandler

# focus object
# {
#     'focus_handler': focused,
#     'blur_handler': hover,
#     'enc_a_handler': enc_a_handler,
#     'enc_b_handler': enc_b_handler,
# }

class FocusManager():
    def __init__(self, hardware):
        self.focus_index = 0
        self.focused = False
        self.focusable_objects = []

        self.encoder_handler = RotateEncoderHandler(
            hardware, self.enc_a, self.enc_b, self.enc_press
        )
        
    def update(self):
        self.encoder_handler.update()

    def add_focusable_object(self, object):
        self.focusable_objects.append(object)
        
        focus_handler = self.focusable_objects[0]['focus_handler']
        focus_handler()

    def enc_a(self):
        if self.focused:
            enc_a_handler = self.focusable_objects[self.focus_index]['enc_a_handler']
            enc_a_handler()

        if not self.focused:
            new_index = self.focus_index + 1
            if new_index > len(self.focusable_objects) - 1:
                return
            
            blur_handler = self.focusable_objects[self.focus_index]['blur_handler']
            blur_handler()

            focus_handler = self.focusable_objects[new_index]['focus_handler']
            focus_handler()
            
            self.focus_index = new_index
        
    def enc_b(self):
        if self.focused:
            enc_b_handler = self.focusable_objects[self.focus_index]['enc_b_handler']
            enc_b_handler()

        if not self.focused:
            new_index = self.focus_index - 1
            if new_index < 0:
                return
            
            blur_handler = self.focusable_objects[self.focus_index]['blur_handler']
            blur_handler()

            focus_handler = self.focusable_objects[new_index]['focus_handler']
            focus_handler()
            
            self.focus_index = new_index

    def enc_press(self):
            self.focused = not self.focused
