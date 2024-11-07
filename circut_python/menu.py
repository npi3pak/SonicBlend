class Menu:
    def __init__(self, hardware, app_state):
        self.hardware = hardware
        self.app_state = app_state



    def show_menu(self):
        # Логика для отображения меню
        if self.app_state.is_modal_active:
            self.display_modal()
        else:
            # Отобразить список синтезаторных движков или текущие настройки
            pass

    def handle_input(self):
        encoder_value = self.hardware.get_encoder_value()
        button_state = self.hardware.get_button_state()
        
        # Управление выбором движков через энкодер
        if button_state == "SELECT":
            self.app_state.set_active_engine(encoder_value)
        elif button_state == "MENU":
            self.app_state.toggle_modal("Перейти к настройкам?")

    def display_modal(self):
        # Логика отображения модального окна с подтверждением или настройками
        print(self.app_state.modal_text)
