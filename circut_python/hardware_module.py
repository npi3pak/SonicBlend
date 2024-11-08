import digitalio
import analogio
import rotaryio
import displayio
import audiobusio
import busio
import board
import adafruit_displayio_ssd1306

KNOB_1_PIN = board.GP26
KNOB_2_PIN = board.GP27
ENC_A_PIN = board.GP0
ENC_B_PIN = board.GP1
ENC_BTN_PIN = board.A3
CV_IN_PIN = board.GP28

I2S_BCK_PIN = board.GP3
I2S_LCK_PIN = board.GP4
I2S_DAT_PIN = board.GP2

DISPLAY_WIDTH = 128
DISPLAY_HEIGHT = 32

DISPLAY_SDA = board.GP6
DISPLAY_SCL = board.GP7

class Hardware:
    def __init__(self):
    
        self.init_hw()
        self.init_i2s()

        displayio.release_displays()
        self.init_display()


    def init_hw(self):
        self.knob1 = analogio.AnalogIn(KNOB_1_PIN)
        self.knob2 = analogio.AnalogIn(KNOB_2_PIN)
        self.cv_in = analogio.AnalogIn(CV_IN_PIN)

        self.encoder = rotaryio.IncrementalEncoder(ENC_A_PIN, ENC_B_PIN)

        self.button = digitalio.DigitalInOut(ENC_BTN_PIN)
        self.button.direction = digitalio.Direction.INPUT
        self.button.pull = digitalio.Pull.UP
        self.button_state = None

        

    def init_display(self):
        displayio.release_displays()

        i2c = busio.I2C(DISPLAY_SCL, DISPLAY_SDA, frequency=100000)
        display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
        
        self.display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT)
        self.display.auto_refresh = False

    def init_i2s(self):
        self.i2s = audiobusio.I2SOut(bit_clock=I2S_BCK_PIN, 
                          word_select=I2S_LCK_PIN, 
                          data=I2S_DAT_PIN)
            
    def get_i2s(self):
        return self.i2s
        
    def get_display(self):
        return self.display
    
    def get_knobs(self):
        return [self.knob1, self.knob2]

    def get_cv_in(self):
        return self.cv_in
    
    def get_encoder(self):
        return self.encoder
    
    def get_encoder_button(self):
        return self.button

