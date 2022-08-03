import sys
import pyglet


KEY_MAP = {
   pyglet.window.key._1: 0x1,
   pyglet.window.key._2: 0x2,
   pyglet.window.key._3: 0x3,
   pyglet.window.key._4: 0xc,
   pyglet.window.key.Q: 0x4,
   pyglet.window.key.W: 0x5,
   pyglet.window.key.E: 0x6,
   pyglet.window.key.R: 0xd,
   pyglet.window.key.A: 0x7,
   pyglet.window.key.S: 0x8,
   pyglet.window.key.D: 0x9,
   pyglet.window.key.F: 0xe,
   pyglet.window.key.Z: 0xa,
   pyglet.window.key.X: 0,
   pyglet.window.key.C: 0xb,
   pyglet.window.key.V: 0xf
}

class Cpu(pyglet.window.Window):

    # Pseudo pixel de 10x10
    pixel = pyglet.resource.image('pixel.png')

    # Buffer de 'pixels'
    sprites = []
    batch = None

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

    # Código da operção em execção
    opcode = 0

    # Controlador de atualização de tela
    should_draw = False

    # Indica que uma tecla foi pressionada
    key_wait = False

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

        self.batch = pyglet.graphics.Batch()
        for i in range(2048):
            self.sprites.append(pyglet.sprite.Sprite(self.pixel, batch=self.batch))

        # Carrega as fontes para a memória
        for i in range(80):
            self.memory = self.fonts[i]

        self.funcmap = {
            0x0000: self._0XXX()
        }

    def draw(self):
        if self.should_draw:
            self.clear()
            for i in range(2048):
                if self.display_buffer[i] == 1:
                    self.sprites[i].x = (i % 64) * 10
                    self.sprites[i].y = 310 - ((i / 64) * 10)
                    self.sprites[i].batch = self.batch
                else:
                    self.sprites[i].batch = None
            self.clear()
            self.batch.draw()
            self.flip()
            self.should_draw = False

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


    def on_key_press(self, symbol, modifiers):
        # log("Botão apertado: ", symbol)
        if symbol in KEY_MAP.keys():
            self.key_inputs[KEY_MAP[symbol]] = 1
            if self.key_wait:
                self.key_wait = False
            else:
                super(Cpu, self).on_key_press(symbol, modifiers)

    def on_key_release(self, symbol, modifiers):
        # log("Botão solto: ", symbol)
        if symbol in KEY_MAP.keys():
            self.key_inputs[KEY_MAP[symbol]] = 0

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

    def _FX29 (self):
        # Desenha pixel de um personagem
        self.index = ( 5 * (self.gpio[self.vx]) ) & 0xFFF

    def _DXXX (self):
        # Desenha um sprite no ponto expecificado
        self.gpio[0xF] = 0

        x = self.gpio[self.vx] & 0xFF
        y = self.gpio[self.vy] & 0xFF
        height = self.opcode & 0x00F    # extrai os dados do ultimo nibble

        for row in range(height):
            current_row = self.memory[self.index + row]
            pixel_offset = 0
            while pixel_offset < 8:
                loc = x + pixel_offset + ((y + row) * 64)
                pixel_offset += 1
                if ((y + row) >= 32) or ((x + pixel_offset - 1) >= 64):
                    continue    # ignora pixels fora da tela
                mask = 1 << (8 - pixel_offset)
                current_pixel = (current_row & mask) >> (8 - pixel_offset)
                # Utilizamos um XOR para atualizar apenas os pixels relevantes a cada quadro
                self.display_buffer[loc] ^= current_pixel
                if self.display_buffer[loc] == 0:
                    self.gpio[0xF] = 1
                else:
                    self.gpio[0xF] = 0
        self.should_draw = True

    def _EXXE(self):
        # Pula pra próxima instrução se a tecla em Vx está apertada
        key = self.gpio[self.vx] & 0xF
        if self.key_inputs[key] == 1:
            self.pc += 2

    def _EXX1(self):
        # Pula pra próxima instrução se a tecla em Vx não está apertada
        key = self.gpio[self.vx] & 0xF
        if self.key_inputs[key] != 1:
            self.pc += 2



