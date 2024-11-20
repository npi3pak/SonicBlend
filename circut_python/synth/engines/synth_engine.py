import displayio

class SynthEngine:
    def __init__(self, hardware, app_state):
        self.hardware = hardware
        self.app_state = app_state
        self.parameters = {}



    def show_main_screen(self):
        # Отображение основного экрана с параметрами
        # Пример использования глобального параметра
        volume = self.app_state.global_settings["volume"]
        print(f"Volume: {volume}")

    def update_parameters(self):
        # Обновление параметров на основе ввода
        pass
