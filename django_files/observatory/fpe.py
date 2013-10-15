#!/usr/bin/env python3
"""
Format-preserving encryption.
See proposed AES-FFX specs:
    http://csrc.nist.gov/groups/ST/toolkit/BCM/documents/proposedmodes/ffx/ffx-spec.pdf
    http://csrc.nist.gov/groups/ST/toolkit/BCM/documents/proposedmodes/ffx/ffx-spec2.pdf
This uses the overall principles of AES-FFX, method 2. It doesn't conform to the proposed
FFX-A2, FFX-A10, or FFX[radix] standards.

MIT license:

----------------------------------------------------------------------------
Copyright (c) 2012 Craig McQueen

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
----------------------------------------------------------------------------
"""

# Standard Python library modules
import struct

# 3rd-party modules
from Crypto.Cipher import AES

class FPEInteger:
    """
    Format-Preserving Encryption.
    This uses AES, but it does not conform to the proposed AES-FFX[radix] standard.
    Inputs and outputs for encryption and decryption are integers.
    This should be suitable for block sizes of up to 2**96.
    """
    def __init__(self, key, rounds=10, radix=2, width=32):
        '''
        key is a 16- 24- or 32-byte string
        '''
        self.key = key
        self.aes_obj = AES.new(key, AES.MODE_ECB)
        self.rounds = rounds
        part_widths = [(width + 1) // 2, width // 2]
        modulos = [ radix**part_width for part_width in part_widths ]
        self.modulos = modulos

        # Pick a suitable block encryption function, with a large enough block size, and also
        # keeping any bias of the final modulo operation reasonably small.
        block_size = radix**width
        self.block_size = block_size
        if ((block_size <= 2**32) or
          ((block_size <= 2**64) and ((2**128 % block_size) == 0))):
            self.block_encrypt_func = self.block_encrypt_func_small
        else:
            self.block_encrypt_func = self.block_encrypt_func_large

    def split_message(self, message):
        '''Split message into working parts. Return a list of parts.'''
        work_0 = message % self.modulos[0]
        message //= self.modulos[0]
        work_1 = message % self.modulos[1]
        return [ work_0, work_1 ]

    def join_message(self, work):
        '''Join list of message parts back into message. Return the message.
        Inverse of self.split_message().'''
        return (work[1] * self.modulos[0]) + work[0]

    def block_encrypt_func_small(self, work_val, round_num, out_modulo):
        '''Block encryption function--small one for block size 2**32 or smaller.'''
        byte_data = struct.pack("<QQ", round_num, work_val)
        encrypt_data = self.aes_obj.encrypt(byte_data)
        temp, = struct.unpack("<8xQ", encrypt_data)
        temp %= out_modulo
        return temp

    def block_encrypt_func_large(self, work_val, round_num, out_modulo):
        '''Block encryption function--large one for block size bigger than 2**32.'''
        byte_data = struct.pack("<QQ", round_num, work_val)
        encrypt_data = self.aes_obj.encrypt(byte_data)
        temp_lo, temp_hi = struct.unpack("<QQ", encrypt_data)
        temp = (temp_hi << 64) | temp_lo
        temp %= out_modulo
        return temp

    def encrypt(self, message):
        '''message is an integer. Returns an integer.'''
        work = self.split_message(message)
        i_from, i_to = 0, 1
        for round_num in range(self.rounds):
            temp = self.block_encrypt_func(work[i_from], round_num, self.modulos[i_to])
            work[i_to] = (work[i_to] + temp) % self.modulos[i_to]
            i_from, i_to = i_to, i_from
        return self.join_message(work)

    def decrypt(self, message):
        '''message is an integer. Returns an integer.'''
        work = self.split_message(message)
        i_from, i_to = (self.rounds - 1) % 2, self.rounds % 2
        for round_num in range(self.rounds-1, -1, -1):
            temp = self.block_encrypt_func(work[i_from], round_num, self.modulos[i_to])
            work[i_to] = (work[i_to] - temp) % self.modulos[i_to]
            i_from, i_to = i_to, i_from
        return self.join_message(work)

if __name__ == "__main__":
    radix = 10
    width = 10
    should_print = True

    fpe_obj = FPEInteger(key=b"mypetsnameeloise", radix=radix, width=width)
    #print("Using block encrypt function '{0}'".format(fpe_obj.block_encrypt_func.__name__))

    if should_print:
        print("Radix {0}, width {1}".format(radix, width))
        if radix == 10:
            print_base = 'd'
            print_width = width
        elif radix == 8:
            print_base = 'o'
            print_width = width
        else:
            print_base = 'X'
            print_width = 1
            while 16**print_width < fpe_obj.block_size:
                print_width += 1
        print("Printing as format '{0}', width {1}".format(print_base, print_width))

    run_range = 16
    #run_range = radix**width
    for i in range(run_range):
        try:
            encrypted = fpe_obj.encrypt(i)
            decrypted = fpe_obj.decrypt(encrypted)
            if should_print:
                print("{0:0{width}{base}} {1:0{width}{base}} {2:0{width}{base}}".format(i, encrypted, decrypted,
                    width=print_width, base=print_base))
            assert (i == decrypted)
        except KeyboardInterrupt:
            print('Completed {0} calculations'.format(i))
            break
			
