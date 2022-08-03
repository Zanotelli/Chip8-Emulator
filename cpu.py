import sys
import pyglet


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

    opcode = 0

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

    funcmap = {}

    def __init__(self,
                 width=None,
                 height=None,
                 caption=None,
                 resizable=False,
                 style=None,
                 fullscreen=False,
                 visible=True,
                 vsync=True,
                 file_drops=False,
                 display=None,
                 screen=None,
                 config=None,
                 context=None,
                 mode=None):
        super().__init__(width, height, caption, resizable, style, fullscreen, visible, vsync, file_drops, display,
                         screen, config, context, mode)
        self.vx = None

        self.funcmap = {
            0x0000: self._0XXX()
        }

    def log(message):
        print(message)

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

        # Carrega as fontes para a memória
        for i in range(80):
            self.memory = self.fonts[i]

    def load_rom (self, rom_path):
        # log("Carregando ", rom_path)
        binary_data = open(rom_path, "rb").read()

        # Carrega os dados da ROM na memória
        for i in range(len(binary_data)):
            self.memory[i + 0x200] = ord(binary_data[i])

    def cycle(self):
        self.opcode = self.memory[self.pc]

        self.vx = (self.opcode & 0x0F00) >> 8
        self.vy = (self.opcode & 0x00F0) >> 4
        self.pc += 2

        extracted_opcode = self.opcode & 0xF000
        try:
            self.funcmap[extracted_opcode]()
        except:
            print("Instruções desconhecidas: ", self.opcode)

        if self.delay_timer > 0:
            self.delay_timer -= 1
        if self.sound_timer > 0:
            self.sound_timer -= 1
            # if self.sound_timer == 0:
                # TOCAR SOM COM O PYGLET



    def _0XXX (self):
        # Extração do primeiro e ultimo nibble para não
        # confundir funções
        extracted_opcode = self.opcode & 0xF0FF
        try:
            self.funcmap[extracted_opcode]()
        except:
            print("Instruções desconhecidas: ", self.opcode)

    def _0XX0 (self):
        # log("Limpa a tela")
        self.display_buffer = [0] * 64 * 32
        self.should_draw

    def _0XXE (self):
        # log("Retorna de subrotina")
        self.pc = self.stack.pop()

    def _4XXX (self):
        # log("Pula a próxima instrução se 'Vx' não for igual a 'NN'")
        if self.gpio[self.vx] != (self.opcode & 0x00FF):
            self.pc += 2

    def _4XXX (self):
        # log("Pula a próxima instrução se 'Vx' for igual a 'Vy'")
        if self.gpio[self.vx] == self.gpio[self.vy]:
            self.pc += 2

    def _8XX4 (self):
        # Adiciona Vy a Vx. Vf é settado para 1 quando há overflow,
        # e 0 quando não há
        if (self.gpio[self.vx] + self.gpio[self.vy]) > 0xFF:
            self.gpio[0xF] = 1
        else:
            self.gpio[0xF] = 0
        self.gpio[self.vx] += self.gpio[self.vy]
        self.gpio[self.vx] &= 0xFF

    def _8XX5 (self):
        # Subtrai Vy a Vx. Vf é settado para 1 quando há overflow,
        # e 0 quando não há
        if self.gpio[self.vy] < self.gpio[self.vx]:
            self.gpio[0xF] = 1
        else:
            self.gpio[0xF] = 0
        self.gpio[self.vx] -= self.gpio[self.vy]
        self.gpio[self.vx] &= 0xFF

    def _FX29(self):
        # Desenha pixel de um personagem
        self.index = ( 5 * (self.gpio[self.vx]) ) & 0xFFF


