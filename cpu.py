import sys


class Cpu(pyglet.window.Window):

    # Botões do input
    key_inputs = [0]*16

    # Memória para pixels de exibição
    display_buffer = [0] * 32 * 64

    # Memória
    memory = [0] * 4096  # max 4096

    # Cache de memória
    gpio = [0]*16 # 16 zeroes

    # Temporizadores
    sound_timer = 0
    delay_timer = 0

    # Registrador de index
    index = 0

    # Contador de programa
    pc = 0

    # Pilha de ponteiros
    stack = []

    # Controlador de atualização de tela
    should_draw = False

    # Fontes para interpretação
    fonts = [
        0xF0, 0x90, 0x90, 0x90, 0xF0,  # 0
        0x20, 0x60, 0x20, 0x20, 0x70,  # 1
        0xF0, 0x10, 0xF0, 0x80, 0xF0,  # 2
        0xF0, 0x10, 0xF0, 0x10, 0xF0,  # 3
        0x90, 0x90, 0xF0, 0x10, 0x10,  # 4
        0xF0, 0x80, 0xF0, 0x10, 0xF0,  # 5
        0xF0, 0x80, 0xF0, 0x90, 0xF0,  # 6
        0xF0, 0x10, 0x20, 0x40, 0x40,  # 7
        0xF0, 0x90, 0xF0, 0x90, 0xF0,  # 8
        0xF0, 0x90, 0xF0, 0x10, 0xF0,  # 9
        0xF0, 0x90, 0xF0, 0x90, 0x90,  # A
        0xE0, 0x90, 0xE0, 0x90, 0xE0,  # B
        0xF0, 0x80, 0x80, 0x80, 0xF0,  # C
        0xE0, 0x90, 0x90, 0x90, 0xE0,  # D
        0xF0, 0x80, 0xF0, 0x80, 0xF0,  # E
        0xF0, 0x80, 0xF0, 0x80, 0x80,  # F
    ]

    def initialize(self):
        self.clear()
        self.memory = [0] * 4096
        self.gpio = [0] * 16
        self.display_buffer = [0] * 64 * 32
        self.stack = []
        self.key_inputs = [0] * 16
        self.index = 0

        self.delay_timer = 0
        self.sound_timer = 0
        self.should_draw = False

        # Inicializa o programa no primeiro espaço de memória
        # permitido para a RAM
        self.pc = 0x200

        for i in range(80):
            self.memory = self.fonts[i]

