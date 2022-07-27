#!/usr/bin/env python3

# This file is part of Ridope project.
# Modified 2022 by lesteves <lesteves@insa-rennes.fr>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *
from litex.soc.interconnect import wishbone

class MemLogic(Module):

    def __init__(self, data_width, depth):

        mem = Memory(data_width, depth)

        length = depth * data_width//8
        
        self.specials.port = mem.get_port( write_capable=True )

        self.logic_write_data = Signal(data_width)
        self.local_adr = Signal(max=length)
        logic_write_enable_signal = Signal()

        pre_write_data = Signal(data_width)
        pre_local_adr = Signal(max=length)
        
        # connect the write port to local logic
        self.comb += [
        self.port.adr.eq( self.local_adr ),
        self.port.dat_w.eq( self.logic_write_data ),
        self.port.we.eq( logic_write_enable_signal )
        ]
        
        # attach a wishbone interface to the Memory() object, with a read-only port
        self.submodules.wb_sram_if = wishbone.SRAM(mem, read_only=True)
        
        # get the wishbone Interface accessor object
        self.bus = wishbone.Interface()
        
        # build an address filter object. This is a migen expression returns 1
        # when the address "a" matches the RAM address space. Useful for precisely
        # targeting the RAM relative to other wishbone-connected objects within
        # the logic, e.g. other RAM blocks or registers.
        # 
        # This filter means the RAM object will occupy its entire own CSR block,
        # with aliased copies of the RAM filling the entire block
        def slave_filter(a):
            return 1

        # This filter constrains the RAM to just its own address space
        decoder_offset = log2_int(depth, need_pow2=False)
        def slave_filter_noalias(a):
            return a[decoder_offset:32 - decoder_offset] == 0
        
        # connect the Wishbone bus to the Memory wishbone port, using the address filter
        # to help decode the address.
        # The decdoder address filter as a list with entries as follows:
        #   (filter_function, wishbone_interface.bus)
        # This is useful if you need to attach multiple local logic memories into the
        # same wishbone address bank.
        wb_con = wishbone.Decoder(self.bus, [(slave_filter, self.wb_sram_if.bus)], register=True)
        # add the decoder as a submodule so it gets pulled into the finalize sweep
        self.submodules += wb_con


        # Write Logic
        self.sync += [
            If((pre_write_data != self.logic_write_data) | (pre_local_adr != self.local_adr),
                logic_write_enable_signal.eq(1),
                pre_write_data.eq(self.logic_write_data),
                pre_local_adr.eq(self.local_adr)
            ).Else(
                logic_write_enable_signal.eq(0)
            )
        ]

