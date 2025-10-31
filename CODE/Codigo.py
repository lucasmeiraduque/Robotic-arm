import ustruct
import time
from microbit import * 
_MODE1 = 0x00
_PRESCALE = 0xFE
_LED0_ON_L = 0x06
_LED0_ON_H = 0x07
_LED0_OFF_L = 0x08
_LED0_OFF_H = 0x09

class PCA9685:
    """Classe para controlar o driver PCA9685, adaptada para o objeto 'i2c' do micro:bit."""
    def __init__(self, i2c, address=0x40):
        self.i2c = i2c
        self.address = address
        
        self.i2c.write(self.address, bytearray([_MODE1, 0x00]))
        self.freq(50) 

    def _write(self, register, value):
        self.i2c.write(self.address, bytearray([register, value & 0xFF]))

    def _read(self, register):
        self.i2c.write(self.address, bytearray([register]), repeat=True) 
        return self.i2c.read(self.address, 1)[0]

    def freq(self, freq=None):
        if freq is None:
            return int(25000000.0 / 4096 / (self._read(_PRESCALE) - 0.5))
        prescaleval = int(25000000.0 / 4096.0 / float(freq) + 0.5)
        oldmode = self._read(_MODE1)
        newmode = (oldmode & 0x7F) | 0x10
        self._write(_MODE1, newmode)
        self._write(_PRESCALE, prescaleval)
        self._write(_MODE1, oldmode)
        time.sleep_ms(5)
        self._write(_MODE1, oldmode | 0xA1) 

    def duty(self, channel, value, invert=False):
        if not 0 <= value <= 4095:
            raise ValueError("Value must be 0-4095")
        
        buf = bytearray(5)
        buf[0] = _LED0_ON_L + 4 * channel
        buf[1] = 0 & 0xFF 
        buf[2] = (0 >> 8) & 0xFF 
        buf[3] = value & 0xFF 
        buf[4] = (value >> 8) & 0xFF 
        self.i2c.write(self.address, buf)

    def servo_angle(self, channel, angle):
        if not 0 <= angle <= 180:
            raise ValueError("Angle must be 0-180")
            
        min_pulse = 102  
        max_pulse = 512  
        
        duty = min_pulse + (max_pulse - min_pulse) * (angle / 180)
        self.duty(channel, int(duty))
i2c.init(scl=pin19, sda=pin20)
CANAL_NIVEL_2_A = 1
CANAL_NIVEL_2_B = 2
CANAL_NIVEL_3 = 3
CANAL_NIVEL_5 = 4  
CANAL_NIVEL_6 = 5  
CANAL_NIVEL_4 = 6  
angulos_atuais = {
    2: 90, 3: 90, 4: 90, 5: 90, 6: 90 
}
ANGULO_MAX = 180
ANGULO_MIN = 0
TEMPO_ATUALIZACAO_MS = 20 
MOVIMENTO_MACRO_INCREMENTO = 3 
def send_servo_angle(nivel, angulo):
    """Encapsula a lógica de envio do ângulo para o PCA9685 (Para Mover e Hold)."""
    if nivel == 2:
        pca.servo_angle(CANAL_NIVEL_2_A, angulo)
        pca.servo_angle(CANAL_NIVEL_2_B, 180 - angulo)
    elif nivel == 3: pca.servo_angle(CANAL_NIVEL_3, angulo)
    elif nivel == 4: pca.servo_angle(CANAL_NIVEL_4, angulo)
    elif nivel == 5: pca.servo_angle(CANAL_NIVEL_5, angulo)
    elif nivel == 6: pca.servo_angle(CANAL_NIVEL_6, angulo)
def mover_para_angulo_suave(nivel, angulo_alvo):
    """Move um servo para o angulo_alvo de forma incremental, garantindo hold nos outros."""
    global angulos_atuais
    angulo_atual = angulos_atuais.get(nivel, 90)
    direcao = 1 if angulo_alvo > angulo_atual else -1
    while abs(angulo_alvo - angulo_atual) > MOVIMENTO_MACRO_INCREMENTO:
        angulo_atual += direcao * MOVIMENTO_MACRO_INCREMENTO
        angulo_atual = max(ANGULO_MIN, min(ANGULO_MAX, angulo_atual))
        send_servo_angle(nivel, angulo_atual)
        angulos_atuais[nivel] = angulo_atual
        for n, ang in angulos_atuais.items():
            if n != nivel:
                send_servo_angle(n, ang)
        time.sleep_ms(TEMPO_ATUALIZACAO_MS) 
    if angulo_alvo != angulo_atual:
        send_servo_angle(nivel, angulo_alvo)
        angulos_atuais[nivel] = angulo_alvo
        time.sleep_ms(TEMPO_ATUALIZACAO_MS)
def executar_macro_a():
    """Coreografia 1: Abre Braço Baixo, Levanta Articulação 1 e Abre Garra."""
    display.show("A")
    time.sleep_ms(300)
    mover_para_angulo_suave(2, 60)   
    mover_para_angulo_suave(3, 120)  
    mover_para_angulo_suave(6, 110)  
    mover_para_angulo_suave(5, 105)  
    mover_para_angulo_suave(3, 90) 
    mover_para_angulo_suave(2, 90)
    mover_para_angulo_suave(6, 90)
    mover_para_angulo_suave(5, 90)
    
    display.show(Image.HEART) 
    time.sleep_ms(1000)

def executar_macro_b():
    """Coreografia 2: Twist, Fechamento Leve e Abaixamento."""
    display.show("B")
    time.sleep_ms(300)
    mover_para_angulo_suave(5, 60)  
    mover_para_angulo_suave(4, 115) 
    mover_para_angulo_suave(6, 75)  
    mover_para_angulo_suave(3, 65)  
    mover_para_angulo_suave(5, 90)
    mover_para_angulo_suave(4, 90)
    mover_para_angulo_suave(6, 90)
    mover_para_angulo_suave(3, 90)
    
    display.show(Image.HEART)
    time.sleep_ms(1000)

try:
    pca = PCA9685(i2c)
    pca.freq(50)
    for nivel, angulo in angulos_atuais.items():
        send_servo_angle(nivel, angulo)

    display.show(Image.YES)
    time.sleep(1)
except OSError as e:
    display.show(Image.NO)
    while True:
        display.scroll("ERRO I2C")
        time.sleep(1000)
display.clear() 
while True:
    if button_a.was_pressed():
        executar_macro_a()
        display.clear()

    if button_b.was_pressed():
        executar_macro_b()
        display.clear()
    for nivel, angulo in angulos_atuais.items(): 
        send_servo_angle(nivel, angulo) 
    time.sleep_ms(TEMPO_ATUALIZACAO_MS)
