import time
from menu import Menu

class ButtonHandler:
    def __init__(self, hardware, hold_callback, hold_threshold=0.3):
        self.hardware = hardware
        self.hold_callback = hold_callback
        self.hold_threshold = hold_threshold  # Hold time threshold in seconds (default 300 ms)
        self.button_hold_start_time = None  # Tracks the start time of the button press

    def long_button_pressed(self):
        """
        Checks if the button has been held down longer than the threshold and triggers the hold callback.
        """
        # Read the button state (active-low)
        button_pressed = not self.hardware.get_encoder_button().value
        current_time = time.monotonic()

        if button_pressed:
            # Start timer if button is newly pressed
            if self.button_hold_start_time is None:
                self.button_hold_start_time = current_time
            elif (current_time - self.button_hold_start_time) >= self.hold_threshold:
                # If held longer than the threshold, trigger the hold callback
                print("Button held for more than 300 ms")
                self.hold_callback()
                self.button_hold_start_time = None  # Reset timer to prevent repeated calls
        else:
            # Button released, reset hold timer
            self.button_hold_start_time = None

class AppState:
    def __init__(self, hardware, synth_engines):
        self.hardware = hardware;

        self.synth_engines = synth_engines
        self.active_engine = None
        self.active_engine_index = 0            
        self.global_settings = {                   
            "volume": 0.8,
            "output_mode": "stereo",
        }

        self.is_modal_active = False              
        self.modal_text = ""   

        self.button_handler = ButtonHandler(self.hardware, self.button_long_press_callback)

        self.init_menu()

    def init_menu(self):
        menu_items = []
        for synth in self.synth_engines:
            menu_items.append(synth.title)

        self.menu = Menu(self.hardware, menu_items, self.set_active_engine)
        self.is_menu_active = True
    
    def destruct_menu(self):
        del self.menu
        self.menu = None
        self.is_menu_active = False
    
    def destruct_active_engine(self):
        del self.active_engine
        self.active_engine = None
        self.active_engine_index = 0

    def button_long_press_callback(self):
        if self.is_menu_active is False:
            self.destruct_active_engine()
            self.init_menu()

    def get_active_engine(self):
        return self.synth_engines[self.active_engine_index]

    def set_active_engine(self, index):
        if 0 <= index < len(self.synth_engines):
            self.active_engine_index = index
            self.is_menu_active = False
            del self.menu
            
            self.init_active_set_active_engine()

    def init_active_set_active_engine(self):
        if not self.active_engine:
            engine = self.get_active_engine()
            self.active_engine = engine(self.hardware)

    def update_ui(self):
        if(self.is_menu_active):
            return self.menu.update_ui()

        self.active_engine.update_ui()
        # self.display.refresh()
    
    def update_input(self):
        if(self.is_menu_active):
            return self.menu.update_input()

        self.button_handler.long_button_pressed()

        if self.active_engine:
            return self.active_engine.update_input()