from microbit import *
import utime

# --- Configurações do PCA9685 ---
PCA = 0x40
FREQ = 50  # Hz para servo analógico

# --- Mapeamento de Portas ---
PORTAS_NIVEL_1 = [0, 1]  # Motores da base (0 = Esquerda/Principal, 1 = Direita/Espelhado)
PORTA_NIVEL_2 = 3        # Articulação 2
PORTA_NIVEL_3 = 4        # Articulação 3

# --- Estado Inicial ---
# O nível atual começa em 1 (Base)
nivel_atual = 1

# Dicionário com os ângulos INICIAIS "lógicos" (baseado no motor principal de cada nível)
# Nível 1: O motor principal (porta 0) começa em 100.
# Nível 2 e 3: Começam em 90.
angulos = {
    1: 100, 
    2: 90,
    3: 90
}

# --- Mapeamento discreto de posições para o Nível 1 (P0, P1)
# Índices: 1..13 conforme tabela fornecida
POSICOES_NIVEL_1 = [
    None,           # índice 0 não usado
    (40, 140),      # posição 1
    (50, 132),      # posição 2
    (60, 125),      # posição 3
    (70, 116),      # posição 4
    (80, 107),      # posição 5
    (90, 97),       # posição 6
    (100, 90),      # posição 7 (inicial)
    (110, 79),      # posição 8
    (120, 70),      # posição 9
    (130, 62),      # posição 10
    (140, 53),      # posição 11
    (150, 47),      # posição 12
    (160, 38)       # posição 13
]

# posição atual do Nível 1 no mapeamento (1..13)
posicao_nivel1 = 7

# --- Funções de Baixo Nível (I2C) ---
def write_reg(reg, val):
    try:
        i2c.write(PCA, bytes([reg, val]))
    except OSError:
        pass 

def set_pwm_freq(freq):
    prescale_val = int(25000000.0 / (4096 * freq) - 1)
    try:
        old = i2c.read(PCA, 1)[0]
        write_reg(0x00, (old & 0x7F) | 0x10)  # sleep
        write_reg(0xFE, prescale_val)
        write_reg(0x00, old)
        utime.sleep_ms(5)
        write_reg(0x00, old | 0x80)
    except OSError:
        display.show("E")

def set_pwm(channel, on, off):
    reg = 0x06 + 4 * channel
    write_reg(reg, on & 0xFF)
    write_reg(reg + 1, (on >> 8) & 0xFF)
    write_reg(reg + 2, off & 0xFF)
    write_reg(reg + 3, (off >> 8) & 0xFF)

def angle_to_pwm(angle):
    # Proteção para não enviar valores negativos ou acima de 180 para o cálculo
    if angle < 0: angle = 0
    if angle > 180: angle = 180
    
    pulse_min = 500
    pulse_max = 2500
    pulse = pulse_min + (pulse_max - pulse_min) * angle / 180
    pwm_val = int(pulse / 1000000 * FREQ * 4096)
    return pwm_val

# --- Controle Lógico do Braço ---

def atualizar_motores(nivel_para_mover):
    """
    Move os motores baseados no ângulo armazenado no dicionário.
    Trata o caso especial de espelhamento do Nível 1.
    """
    if nivel_para_mover == 1:
        # --- Nível 1: Base (Portas 0 e 1) ---
        # Usar o mapeamento discreto POSICOES_NIVEL_1 por índice posicao_nivel1
        try:
            p0, p1 = POSICOES_NIVEL_1[posicao_nivel1]
        except Exception:
            # fallback para o valor em angulos[1] mantendo compatibilidade
            p0 = angulos.get(1, 100)
            p1 = 190 - p0

        set_pwm(PORTAS_NIVEL_1[0], 0, angle_to_pwm(p0))
        set_pwm(PORTAS_NIVEL_1[1], 0, angle_to_pwm(p1))
        return

    elif nivel_para_mover == 2:
        # --- Nível 2: Articulação 2 (Porta 3) ---
        angulo_principal = angulos.get(2, 90)
        set_pwm(PORTA_NIVEL_2, 0, angle_to_pwm(angulo_principal))

    elif nivel_para_mover == 3:
        # --- Nível 3: Articulação 3 (Porta 4) ---
        angulo_principal = angulos.get(3, 90)
        set_pwm(PORTA_NIVEL_3, 0, angle_to_pwm(angulo_principal))

def inicializar_braco():
    write_reg(0x00, 0x00)
    utime.sleep_ms(5)
    set_pwm_freq(FREQ)
    
    # Força a posição inicial de todos os níveis
    atualizar_motores(1) # Põe 0 em 100° e 1 em 90°
    utime.sleep_ms(50)
    atualizar_motores(2) # Põe 3 em 90°
    utime.sleep_ms(50)
    atualizar_motores(3) # Põe 4 em 90°
    
    display.show(nivel_atual)

# --- Execução ---
inicializar_braco()

while True:
    # --- Botão A: Diminui Angulo OU Sobe Nível ---
    if button_a.was_pressed():
        # Delay para detectar duplo clique
        utime.sleep_ms(300)
        
        if button_a.was_pressed():
            # >> CLIQUE DUPLO: Mudar Nível (Subir)
            nivel_atual += 1
            if nivel_atual > 3: 
                nivel_atual = 3
            display.show(nivel_atual)
        else:
            # >> CLIQUE ÚNICO: Mover Motor (passo discreto para Nível 1 ou -10° para outros)
            if nivel_atual == 1:
                # mover para posição anterior no mapeamento
                posicao_nivel1 -= 1
                if posicao_nivel1 < 1:
                    posicao_nivel1 = 1
            else:
                angulos[nivel_atual] -= 10
                # Limites de segurança (0 a 180)
                if angulos[nivel_atual] < 0:
                    angulos[nivel_atual] = 0

            atualizar_motores(nivel_atual)
            # Feedback visual rápido de movimento
            display.show(".")
            utime.sleep_ms(100)
            display.show(nivel_atual)

    # --- Botão B: Aumenta Angulo OU Desce Nível ---
    if button_b.was_pressed():
        # Delay para detectar duplo clique
        utime.sleep_ms(300)
        
        if button_b.was_pressed():
            # >> CLIQUE DUPLO: Mudar Nível (Descer)
            nivel_atual -= 1
            if nivel_atual < 1: 
                nivel_atual = 1
            display.show(nivel_atual)
        else:
            # >> CLIQUE ÚNICO: Mover Motor (passo discreto para Nível 1 ou +10° para outros)
            if nivel_atual == 1:
                # mover para próxima posição no mapeamento
                posicao_nivel1 += 1
                if posicao_nivel1 > 13:
                    posicao_nivel1 = 13
            else:
                angulos[nivel_atual] += 10
                # Limites de segurança
                if angulos[nivel_atual] > 180:
                    angulos[nivel_atual] = 180

            atualizar_motores(nivel_atual)
            # Feedback visual
            display.show(".")
            utime.sleep_ms(100)
            display.show(nivel_atual)
            
    utime.sleep_ms(50)
