"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.pc = 0
        self.reg = [0] * 8
        self.ram = [0] * 256
        self.SP = 7


    def load(self):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010,  # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111,  # PRN R0
        #     0b00000000,
        #     0b00000001,  # HLT
        # ]

        program = []

        if len(sys.argv) != 2:
            print("Usage: ls8.py <filename>")
            sys.exit(1)

        try:
            with open(sys.argv[1]) as f:
                for line in f:
                    try:
                        line = line.split("#", 1)[0].strip()
                        if line == "":
                            continue
                        line = int(line, 2)     # int() is base 10 by default and we need binary, hence (line, 2)
                        program.append(line)
                    except ValueError:
                        pass
            
            for instruction in program:
                self.ram[address] = instruction
                address += 1

        except FileNotFoundError:
            print(f"Could not find file: {sys.argv[1]}")
            sys.exit(1)

        # print("Program: ", program)
    

    def ram_read(self, MAR):
        # MAR (Memory Address Register) = Address that is being read/written
        MDR = self.ram[MAR]
        return MDR


    def ram_write(self, MAR, MDR):
        # MDR (Memory Data Register) = Data that will be read or will be written
        self.ram[MAR] = MDR
        # print("Updated Ram (self.ram): ", self.ram)


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]

        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]

        elif op == "SUB":
            if reg_a >= reg_b:
                self.reg[reg_a] -= self.reg[reg_b]
            else:
                self.reg[reg_b] -= self.reg[reg_a]

        elif op == "DIV":
            if reg_a >= reg_b:
                self.reg[reg_a] //= self.reg[reg_b]
            else:
                self.reg[reg_b] //= self.reg[reg_a]

        else:
            raise Exception("Unsupported ALU operation")


    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()


    def run(self):
        """Run the CPU."""
        running = True
        HLT = 0b00000001
        LDI = 0b10000010
        PRN = 0b01000111
        MUL = 0b10100010
        PUSH = 0b01000101
        POP = 0b01000110
        CALL = 0b01010000
        RET = 0b00010001
        ADD = 0b10100000

        while running:
            # IR (Instruction Register) = info from memory address stored at pc
            IR = self.ram_read(self.pc)
            # print("IR: ", IR)
            reg_a = self.ram_read(self.pc + 1)
            reg_b = self.ram_read(self.pc + 2)

            if IR == HLT:
                # print("Running HLT (Exiting)...")
                running = False
                self.pc += 1
                sys.exit()

            elif IR == LDI:
                # print("Running LDI...")
                self.reg[reg_a] = reg_b
                self.pc += 3

            elif IR == PRN:
                # print("Running PRN...")
                print(self.reg[reg_a])
                self.pc += 2

            elif IR == MUL:
                # print("Running MUL...")
                self.alu("MUL", reg_a, reg_b)
                self.pc += 3

            elif IR == PUSH:
                self.ram_write(self.SP, self.reg[reg_a])
                self.pc += 2
                self.SP -= 1

            elif IR == POP:
                self.reg[reg_a] = self.ram_read(self.SP + 1)
                self.SP += 1
                self.pc += 2

            elif IR == CALL:
                # Get address of the next instruction
                return_addr = self.pc + 2

                # Push that on the stack
                self.reg[self.SP] -= 1
                address_to_push_to = self.reg[self.SP]
                self.ram[address_to_push_to] = return_addr

                # Set the PC to the subroutine address
                reg_num = self.ram[self.pc + 1]
                subroutine_addr = self.reg[reg_num]

                self.pc = subroutine_addr
            elif IR == RET:
                # Get return address from the top of the stack
                address_to_pop_from = self.reg[self.SP]
                return_addr = self.ram[address_to_pop_from]
                self.reg[self.SP] += 1

                # Set the PC to the return address
                self.pc = return_addr     

            elif IR == ADD:
                self.alu("ADD", reg_a, reg_b)
                self.pc += 3

            else:
                print(f"Instruction is invalid: {IR} at index {self.pc}")
                running = False
                sys.exit()
                
