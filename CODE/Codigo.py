from microbit import *
import utime

PCA = 0x40
FREQ = 60 

#registradores PCA9685
MODE1 = 0x00
PRESCALE = 0xFE
LED0_ON_L = 0x06

#servos de posição
PORTAS_NIVEL_1 = [0, 1] 
PORTA_NIVEL_2 = 3 
PORTA_NIVEL_3 = 4 
#servos de rotação
PORTA_NIVEL_4 = 5 
PORTA_NIVEL_5 = 6 

#constantes de pulso para os motores de rotação
NEUTRAL_PULSE = 380 
COUNTER_CLOCKWISE_PULSE = 220 
CLOCKWISE_PULSE = 500 

nivel_atual = 1

#angulos e pulsos iniciais
angulos = {
    1: 100,
    2: 90,
    3: 90,
    4: NEUTRAL_PULSE, 
    5: NEUTRAL_PULSE 
}

POSICOES_NIVEL_1 = [
    None, (40, 140), (50, 132), (60, 125), (70, 116), (80, 107), (90, 97),
    (100, 90),
    (110, 79), (120, 70), (130, 62), (140, 53), (150, 47), (160, 38)
]
posicao_nivel1 = 7

def write_reg(reg, val):
    try:
        i2c.write(PCA, bytes([reg, val]))
    except OSError:
        pass

def set_pwm_freq(freq):
    prescale_val = int(25000000.0 / (4096 * freq) - 1)
    try:
        i2c.write(PCA, bytes([0x00]))
        old = i2c.read(PCA, 1)[0]
        write_reg(0x00, (old & 0x7F) | 0x10)
        write_reg(0xFE, prescale_val)
        write_reg(0x00, old)
        utime.sleep_ms(5)
        write_reg(0x00, old | 0x80)
    except OSError:
        display.show("E")

def set_pwm(channel, on, off):
    reg = LED0_ON_L + 4 * channel
    write_reg(reg, on & 0xFF)
    write_reg(reg + 1, (on >> 8) & 0xFF)
    write_reg(reg + 2, off & 0xFF)
    write_reg(reg + 3, (off >> 8) & 0xFF)

def angle_to_pwm(angle):
    if angle < 0: angle = 0
    if angle > 180: angle = 180
    pulse_min = 500
    pulse_max = 2500
    pulse = pulse_min + (pulse_max - pulse_min) * angle / 180
    pwm_val = int(pulse / 1000000 * FREQ * 4096)
    return pwm_val

#controle dos servos de rotação
def stop_servo(channel):
    set_pwm(channel, 0, NEUTRAL_PULSE)

def move_counter_clockwise(channel):
    set_pwm(channel, 0, COUNTER_CLOCKWISE_PULSE)

def move_clockwise(channel):
    set_pwm(channel, 0, CLOCKWISE_PULSE)

def atualizar_motores(nivel_para_mover):
    if nivel_para_mover == 1:
        try:
            p0, p1 = POSICOES_NIVEL_1[posicao_nivel1]
        except Exception:
            p0 = angulos.get(1, 100)
            p1 = 190 - p0
        set_pwm(PORTAS_NIVEL_1[0], 0, angle_to_pwm(p0))
        set_pwm(PORTAS_NIVEL_1[1], 0, angle_to_pwm(p1))

    elif nivel_para_mover == 2:
        angulo_principal = angulos.get(2, 90)
        set_pwm(PORTA_NIVEL_2, 0, angle_to_pwm(angulo_principal))

    elif nivel_para_mover == 3:
        angulo_principal = angulos.get(3, 90)
        set_pwm(PORTA_NIVEL_3, 0, angle_to_pwm(angulo_principal))

    elif nivel_para_mover == 4:
        pass
    elif nivel_para_mover == 5:
        pass

def inicializar_braco():
    try:
        i2c.init() 
        write_reg(MODE1, 0x00) 
        utime.sleep_ms(5)
        set_pwm_freq(FREQ)
        i2c.write(PCA, bytes([MODE1]))
        old = i2c.read(PCA, 1)[0]
        write_reg(MODE1, old | 0xA0) 
    except OSError:
        display.show("E0")
        return
    utime.sleep_ms(10)

    atualizar_motores(1)
    atualizar_motores(2)
    atualizar_motores(3)
    stop_servo(PORTA_NIVEL_4)
    stop_servo(PORTA_NIVEL_5)

    utime.sleep_ms(200)
    display.show(nivel_atual)

inicializar_braco()


last_a_action = 0
last_b_action = 0
CLICK_DEBOUNCE_TIME = 200 

while True:
    current_time = utime.ticks_ms()

    if button_a.is_pressed() and button_b.is_pressed():
        if button_a.was_pressed() or button_b.was_pressed():
            stop_servo(PORTA_NIVEL_4)
            stop_servo(PORTA_NIVEL_5)
            nivel_atual += 1
            if nivel_atual > 5:
                nivel_atual = 1 
            display.show(nivel_atual)
            utime.sleep_ms(300) 
        continue 
        
    elif button_a.is_pressed():
        if nivel_atual <= 3:
            if (current_time - last_a_action) >= CLICK_DEBOUNCE_TIME:
                if nivel_atual == 1:
                    posicao_nivel1 = max(posicao_nivel1 - 1, 1)
                else:
                    angulos[nivel_atual] = max(angulos[nivel_atual] - 10, 0)
                atualizar_motores(nivel_atual)
                display.show("-") 
                last_a_action = current_time
                utime.sleep_ms(50) 
        elif nivel_atual >= 4:
            display.show("<")
            move_counter_clockwise(PORTA_NIVEL_4 if nivel_atual == 4 else PORTA_NIVEL_5)
    elif button_b.is_pressed():
        if nivel_atual <= 3:
            if (current_time - last_b_action) >= CLICK_DEBOUNCE_TIME:
                if nivel_atual == 1:
                    posicao_nivel1 = min(posicao_nivel1 + 1, 13)
                else:
                    angulos[nivel_atual] = min(angulos[nivel_atual] + 10, 180)
                atualizar_motores(nivel_atual)
                display.show("+")
                last_b_action = current_time
                utime.sleep_ms(50) 
        elif nivel_atual >= 4:
            display.show(">")
            move_clockwise(PORTA_NIVEL_4 if nivel_atual == 4 else PORTA_NIVEL_5)
    else:
        if nivel_atual == 4:
            stop_servo(PORTA_NIVEL_4)
        elif nivel_atual == 5:
            stop_servo(PORTA_NIVEL_5)
        display.show(nivel_atual)
        
    utime.sleep_ms(10)
