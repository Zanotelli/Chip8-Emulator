import sys
import cpu

def main (self):
    self.initialize()
    self.load_rom(sys.argv[1])
    while not self.has_exit:
        self.dispatch_events()
        self.cycle()
        self.draw()

main(cpu.Cpu())