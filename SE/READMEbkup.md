# Projeto Braço Robótico

---

## **Disciplina:** Sistemas Embarcados

**Engenharia da Computação - PUC Minas Lourdes**

### **Objetivo Principal**

O projeto visa o desenvolvimento e a construção de um **braço robótico funcional**. A estrutura será impressa em 3D, e o controle será feito por um **microcontrolador Micro:bit**. O braço deverá ser capaz de manipular objetos leves e ser operado remotamente por um controle de videogame, utilizando comunicação sem fio.

### **Objetivos Específicos**

* **Programação:** Desenvolver o código (em **Python** ou **C++**) para controlar os movimentos do braço através do Micro:bit.
* **Controle de Movimento:** Utilizar **motores de passo** para garantir movimentos precisos e controlados.
* **Interface de Controle:** O controle remoto será um **controle de videogame**, proporcionando uma interface intuitiva e familiar.

### **Arquitetura Utilizada**

A arquitetura do projeto é baseada no seguinte hardware:

* **Microcontrolador:** BBC micro:bit V2
    * **CPU:** Nordic ARM Cortex-M4 nRF52833 (64 MHz)
    * **Memória:** 128 KB de RAM / 512 KB de Flash
    * **Comunicação:** Bluetooth 5.1 (BLE)

### **Desenvolvimento de Software**

O código do projeto foi desenvolvido em Python. Para o carregamento dos códigos no Microcontrolador, utilizamos a plataforma web do micro:bit, que permite editar, compilar e enviar o código diretamente para a placa.

### **Modelo 3D**

Utilizamos o modelo 3D desenvolvido por **LimpSquid**.

- Link do projeto no Thingiverse: https://www.thingiverse.com/LimpSquid/

### **Componentes Utilizados**

- 6 motores servo **TowerPro MG995** (servo de rotação com engrenagem metálica)
- 1 motor de passo **NEMA 17**
- Módulo controlador de servos **PCA9685** (PWM I2C, 16 canais)
- Microcontrolador **micro:bit V2**
- Fonte **5V**

### **Outros Materiais Utilizados**

- Rolamentos 6200ZZ (2x)
- Rolamentos 688ZZ (5x)
- Esferas de aço de 10 mm (10x)
- Parafuso M3, 3 mm — parafuso sem cabeça (grub screw) (1x)
- Parafuso M3, 8 mm — cabeça redonda (34x)
- Parafuso M3, 10 mm — cabeça redonda (61x)
- Parafuso M3, 10 mm — cabeça chata (countersunk) (1x)
- Parafuso M3, 25 mm — cabeça redonda (2x)
- Parafuso M3, 16 mm — cabeça redonda (4x)
- Parafuso M3, 63 mm — cabeça redonda (2x)
- Porca M3 (2x)
- Parafuso M4, 3 mm — parafuso sem cabeça (grub screw) (1x)
