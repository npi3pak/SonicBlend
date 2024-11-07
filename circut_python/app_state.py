class AppState:
    def __init__(self, synth_engines):
        self.synth_engines = synth_engines         # Список доступных движков
        self.active_engine_index = 0               # Индекс активного синтезаторного движка
        self.global_settings = {                   # Глобальные настройки приложения
            "volume": 0.8,
            "output_mode": "stereo",
            # Добавьте другие глобальные параметры по мере необходимости
        }
        self.is_modal_active = False               # Флаг активности модального окна
        self.modal_text = ""                       # Текст текущего модального окна

    def get_active_engine(self):
        return self.synth_engines[self.active_engine_index]

    def set_active_engine(self, index):
        if 0 <= index < len(self.synth_engines):
            self.active_engine_index = index

    def toggle_modal(self, text=""):
        # Открыть или закрыть модальное окно
        self.is_modal_active = not self.is_modal_active
        self.modal_text = text if self.is_modal_active else ""
    
    def update_global_setting(self, setting, value):
        # Обновление глобального параметра
        if setting in self.global_settings:
            self.global_settings[setting] = value
