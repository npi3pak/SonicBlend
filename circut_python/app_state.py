import displayio
import terminalio
from adafruit_displayio_ssd1306 import SSD1306
from adafruit_display_text import label
from adafruit_display_shapes.rect import Rect
import time

TEXT_COLOR = 0xFFFFFF
BG_COLOR = 0x000000

class Menu:
    def __init__(self, hardware, menu_items, handle_select_callback):
        self.hardware = hardware
        self.handle_select_callback = handle_select_callback
        self.display = self.hardware.get_display()


        test_list = ["Option 1", "Option 2", "Option 3", "Option 4", "Option 5", "Option 6"]
        menu_items.extend(test_list)

        self.menu_items = menu_items
        self.current_selection = 0
        self.top_index = 0  # First item in the 3-line window
        self.last_position = self.hardware.get_encoder().position

        # Constants
        self.MAX_DISPLAY_LINES = 3

        # Display group for screen elements
        self.screen_group = displayio.Group()


        # Text labels for each line
        self.text_areas = []
        for i in range(self.MAX_DISPLAY_LINES):
            line_color = BG_COLOR if i is self.current_selection else TEXT_COLOR
            bg_color = TEXT_COLOR if i is self.current_selection else BG_COLOR
            
            text_area = label.Label(terminalio.FONT, text="", color=line_color, background_color=bg_color,x=5, y=5 + (i * 11))
            self.text_areas.append(text_area)
            self.screen_group.append(text_area)

        self.display.root_group = self.screen_group
        self.update_ui()  # Initial display update

    def update_ui(self):
        """
        Refresh the display based on current menu state.
        """
        # Update highlight position
        # self.highlight_rect.y = (self.current_selection - self.top_index) * 11

        # Display the current menu items in the window
        for i in range(self.MAX_DISPLAY_LINES):
            item_index = self.top_index + i
            if item_index < len(self.menu_items):
                self.text_areas[i].text = self.menu_items[item_index]

                line_color = BG_COLOR if item_index is self.current_selection else TEXT_COLOR
                bg_color = TEXT_COLOR if item_index is self.current_selection else BG_COLOR

                self.text_areas[i].color = line_color
                self.text_areas[i].background_color = bg_color
            else:
                self.text_areas[i].text = ""


        self.display.refresh()

    def update_input(self):
        """
        Update encoder position and button state, modify menu selection.
        """
        # Read encoder position and button
        position = self.hardware.get_encoder().position
        button_pressed = not self.hardware.get_encoder_button().value  # Button active-low

        if position != self.last_position:
            if position > self.last_position:
                self.current_selection += 1
            else:
                self.current_selection -= 1

            # Clamp within menu bounds
            self.current_selection = max(0, min(self.current_selection, len(self.menu_items) - 1))


            # Adjust top_index for scrolling
            if self.current_selection < self.top_index:
                self.top_index = self.current_selection
            elif self.current_selection >= self.top_index + self.MAX_DISPLAY_LINES:
                self.top_index = self.current_selection - self.MAX_DISPLAY_LINES + 1

            # Update display to reflect new selection
            self.update_ui()
            self.last_position = position

        # Handle button press
        if button_pressed:
            print("Selected:", self.menu_items[self.current_selection])
            self.handle_select_callback(self.current_selection)
            # time.sleep(0.3)  # Debounce delay

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

        self.active_engine.update_input()