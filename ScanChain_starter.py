import copy
import cocotb
from cocotb.triggers import Timer


# Make sure to set FILE_NAME
# to the filepath of the .log
# file you are working with
CHAIN_LENGTH = -1
FILE_NAME    = "adder/adder.log"



# Holds information about a register
# in your design.

################
# DO NOT EDIT!!!
################
class Register:

    def __init__(self, name) -> None:
        self.name = name            # Name of register, as in .log file
        self.size = -1              # Number of bits in register

        self.bit_list = list()      # Set this to the register's contents, if you want to
        self.index_list = list()    # List of bit mappings into chain. See handout

        self.first = -1             # LSB mapping into scan chain
        self.last  = -1             # MSB mapping into scan chain


# Holds information about the scan chain
# in your design.
        
################
# DO NOT EDIT!!!
################
class ScanChain:

    def __init__(self) -> None:
        self.registers = dict()     # Dictionary of Register objects, indexed by 
                                    # register name
        
        self.chain_length = 0       # Number of FFs in chain


# Sets up a new ScanChain object
# and returns it

################     
# DO NOT EDIT!!!
################
def setup_chain(filename):

    scan_chain = ScanChain()

    f = open(filename, "r")
    for line in f:
        linelist = line.split()
        index, name, bit = linelist[0], linelist[1], linelist[2]

        if name not in scan_chain.registers:
            reg = Register(name)
            reg.index_list.append((int(bit), int(index)))
            scan_chain.registers[name] = reg

        else:
            scan_chain.registers[name].index_list.append((int(bit), int(index)))
        
    f.close()

    for name in scan_chain.registers:
        cur_reg = scan_chain.registers[name]
        cur_reg.index_list.sort()
        new_list = list()
        for tuple in cur_reg.index_list:
            new_list.append(tuple[1])
        
        cur_reg.index_list = new_list
        cur_reg.bit_list   = [0] * len(new_list)
        cur_reg.size = len(new_list)
        cur_reg.first = new_list[0]
        cur_reg.last  = new_list[-1]
        scan_chain.chain_length += len(cur_reg.index_list)

    return scan_chain


# Prints info of given Register object

################
# DO NOT EDIT!!!
################
def print_register(reg):
    print("------------------")
    print(f"NAME:    {reg.name}")
    print(f"BITS:    {reg.bit_list}")
    print(f"INDICES: {reg.index_list}")
    print("------------------")


# Prints info of given ScanChain object

################   
# DO NOT EDIT!!!
################
def print_chain(chain):
    print("---CHAIN DISPLAY---\n")
    print(f"CHAIN SIZE: {chain.chain_length}\n")
    print("REGISTERS: \n")
    for name in chain.registers:
        cur_reg = chain.registers[name]
        print_register(cur_reg)



#-------------------------------------------------------------------

# This function steps the clock once.
    
# Hint: Use the Timer() builtin function
async def step_clock(dut):

    ######################
    # TODO: YOUR CODE HERE 
    ######################

    # Set clock high
    dut.clk.value = 1
    
    # Wait for 10 ns
    await Timer(10, units='ns')
    
    # Set clock low
    dut.clk.value = 0
    
    # Wait for 10 more ns
    await Timer(10, units='ns')
    

#-------------------------------------------------------------------

# This function places a bit value inside FF of specified index.
        
# Hint: How many clocks would it take for value to reach
#       the specified FF?
        
async def input_chain_single(dut, bit, ff_index):

    ######################
    # TODO: YOUR CODE HERE 
    ######################

    # Enable scan mode
    dut.scan_en.value = 1
    
    # Shift the bit to the correct position in the chain
    for i in range(ff_index):
        dut.scan_in.value = 0
        await step_clock(dut)
    
    # Insert target bit
    dut.scan_in.value = bit
    await step_clock(dut)
    
    # Disable scan mode when done
    dut.scan_en.value = 0
#-------------------------------------------------------------------

# This function places multiple bit values inside FFs of specified indexes.
# This is an upgrade of input_chain_single() and should be accomplished
#   for Part H of Task 1
        
# Hint: How many clocks would it take for value to reach
#       the specified FF?
        
async def input_chain(dut, bit_list, ff_index):

    ######################
    # TODO: YOUR CODE HERE 
    ######################

    # Enable scan mode
    dut.scan_en.value = 1
    
    # Put the first bit at position ff_index
    for i in range(ff_index):
        dut.scan_in.value = 0
        await step_clock(dut)
    
    # Insert list of bits in reverse order
    for bit in reversed(bit_list):
        dut.scan_in.value = bit
        await step_clock(dut)
    
    # Disable scan mode when done
    dut.scan_en.value = 0

#-----------------------------------------------

# This function retrieves a single bit value from the
# chain at specified index 
        
async def output_chain_single(dut, ff_index):

    ######################
    # TODO: YOUR CODE HERE 
    ######################

    # Enable scan mode
    dut.scan_en.value = 1
    
    
    shifts_needed = CHAIN_LENGTH - ff_index - 1
    result = None
    
    for i in range(CHAIN_LENGTH):
        await step_clock(dut)
        if i == shifts_needed:
            result = int(dut.scan_out.value)
    
    # Disable scan mode when done
    dut.scan_en.value = 0
    
    return result 

#-----------------------------------------------

# This function retrieves a single bit value from the
# chain at specified index 
# This is an upgrade of input_chain_single() and should be accomplished
#   for Part H of Task 1
        
async def output_chain(dut, ff_index, output_length):

    ######################
    # TODO: YOUR CODE HERE 
    ######################

    # Enable scan mode
    dut.scan_en.value = 1

    shifts_needed = CHAIN_LENGTH - (ff_index + output_length - 1) - 1
    result = []
    
    # Shift out all bits
    for i in range(CHAIN_LENGTH):
        await step_clock(dut)
        bit_position = i - shifts_needed
        if 0 <= bit_position < output_length:
            result.append(int(dut.scan_out.value))
    
    # Disable scan mode when done
    dut.scan_en.value = 0
    
    return result

#-----------------------------------------------

# Your main testbench function

# @cocotb.test()
# async def test(dut):

#     global CHAIN_LENGTH
#     global FILE_NAME        # Make sure to edit this guy
#                             # at the top of the file

#     # Setup the scan chain object
#     chain = setup_chain(FILE_NAME)

#     ######################
#     # TODO: YOUR CODE HERE 
#     ######################
    
#     CHAIN_LENGTH = chain.chain_length
    
#     print_chain(chain)
    
#     # Init
#     dut.scan_en.value = 0
#     dut.scan_in.value = 0
#     dut.clk.value = 0
    
#     test_cases = [
#         (0b0101, 0b0011),  # 5 + 3 = 8
#         (0b1010, 0b0011),  # 10 + 3 = 13
#         (0b1111, 0b0001)   # 15 + 1 = 16
#     ]
    
#     for a_val, b_val in test_cases:
#         # Convert inputs to bit lists
#         a_bits = [int(bit) for bit in bin(a_val)[2:].zfill(4)]
#         b_bits = [int(bit) for bit in bin(b_val)[2:].zfill(4)]
        
#         a_reg = chain.registers["a_reg"]
#         b_reg = chain.registers["b_reg"]
#         x_out = chain.registers["x_out"]
        
#         all_bits = [0] * CHAIN_LENGTH
#         # Reverse bits
#         a_bits_reversed = a_bits[::-1]
#         b_bits_reversed = b_bits[::-1]
        
#         # Load input bits 
#         for i in range(a_reg.size):
#             all_bits[a_reg.index_list[i]] = a_bits_reversed[i]
        
#         for i in range(b_reg.size):
#             all_bits[b_reg.index_list[i]] = b_bits_reversed[i]
        
#         await input_chain(dut, all_bits, 0)
#         dut.scan_en.value = 0
#         await step_clock(dut)
        
#         dut.scan_en.value = 1
#         result_bits = await output_chain(dut, x_out.first, x_out.size)
        
#         result = int(''.join(map(str, result_bits[:4])), 2)
#         expected = a_val + b_val
        
#         print(f"Test: {a_val} + {b_val} = {result}, Expected: {expected}")
#         assert result == expected, f"Test failed: {a_val} + {b_val} = {result}, Expected: {expected}"


@cocotb.test()
async def test_fsm(dut):
    global CHAIN_LENGTH
    
    chain = setup_chain("hidden_fsm/hidden_fsm.log")
    CHAIN_LENGTH = chain.chain_length
    
    print_chain(chain)
    
    # Init
    dut.scan_en.value = 0
    dut.scan_in.value = 0
    dut.clk.value = 0
    dut.data_avail.value = 0 
    
    state_reg = chain.registers["cur_state"]
    
    # Prints so its organized
    print("State Transition Table:")
    print("| Current State | data_avail | buf_en | out_sel | out_writing | Next State |")
    print("|---------------|------------|--------|---------|-------------|------------|")
    
    # Try all possible states
    for state_val in range(8): 
        state_bits = [int(bit) for bit in bin(state_val)[2:].zfill(3)]
        state_bits_reversed = state_bits[::-1]  
        
        for data_avail_val in [0, 1]:
            all_bits = [0] * CHAIN_LENGTH
            
            for i in range(state_reg.size):
                all_bits[state_reg.index_list[i]] = state_bits_reversed[i]
            
            await input_chain(dut, all_bits, 0)
            dut.scan_en.value = 0
            dut.data_avail.value = data_avail_val
            
            buf_en = int(dut.buf_en.value)
            out_sel = int(dut.out_sel.value)
            out_writing = int(dut.out_writing.value)
            
            await step_clock(dut)
            dut.scan_en.value = 1
            result_bits = await output_chain(dut, state_reg.first, state_reg.size)

            next_state = 0
            for i, bit in enumerate(result_bits):
                next_state |= (bit << i)
            
            # Print the transition in table format
            print(f"| {state_val:^13} | {data_avail_val:^10} | {buf_en:^6} | {out_sel:^7} | {out_writing:^11} | {next_state:^10} |")