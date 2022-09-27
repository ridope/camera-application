#!/usr/bin/env python3

# This file is part of Ridope project.
# Modified 2022 by lesteves <lesteves@insa-rennes.fr>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.soc.cores import uart
from litex.soc.interconnect import wishbone
from litex.soc.interconnect import stream

class MemLogic(Module):

    def __init__(self, amp_soc, data_width, depth, bursting):

        length = depth * data_width//8

        addr_base = 3136
        
        self.logic_write_data = Signal(data_width)
        self.local_adr = Signal(max=length)

        logic_write_enable_signal = Signal()

        pre_write_data = Signal(data_width)
        pre_local_adr = Signal(max=length) 
       
        mem_if = wishbone.Interface()      
        
        self.submodules.arb = wishbone.Arbiter([mem_if, amp_soc.mmap_sp1], amp_soc.scratch1.bus)

        # FSM.
        self.submodules.fsm = fsm = FSM(reset_state="IDLE")
        
        fsm.act("IDLE",
            mem_if.cyc.eq(0),
            mem_if.stb.eq(0),
            mem_if.we.eq(0),
            mem_if.sel.eq(15),

            If(logic_write_enable_signal == 1,
                NextState("BUS-REQUEST")
            )
        )

        fsm.act("BUS-REQUEST",
            mem_if.cyc.eq(1),
            mem_if.stb.eq(1),
            mem_if.we.eq(1),
            If(mem_if.ack == 1,
                NextState("IDLE")
            )
        )

        # Write Logic
        self.sync += [
            If((pre_write_data != self.logic_write_data) | (pre_local_adr != self.local_adr),
                pre_write_data.eq(self.logic_write_data),
                pre_local_adr.eq(self.local_adr),
                mem_if.adr.eq(addr_base + self.local_adr),
                mem_if.dat_w.eq(self.logic_write_data),
                logic_write_enable_signal.eq(1),
            ).Else(
                logic_write_enable_signal.eq(0)
            )
        ]

