#!/usr/bin/env python3

# This file is part of LiteX-Boards.
# Copyright (c) 2019 msloniewski <marcin.sloniewski@gmail.com>
# Modified 2021 by mpelcat <mpelcat@insa-rennes.fr>
# Modified 2022 by lesteves <lesteves@insa-rennes.fr>
# SPDX-License-Identifier: BSD-2-Clause

import os
import argparse

from litex.build import io
from litex.soc.doc import generate_docs, generate_svd
from litex.soc.cores.gpio import GPIOOut, GPIOTristate
from litex.soc.cores.led import LedChaser
from litex_boards.platforms.muselab_icesugar import led_pmod_io_v11

from migen import *
from migen.genlib.cdc import MultiReg
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex_boards.platforms import terasic_de10lite # referencing the platform

from litex.soc.cores.clock import Max10PLL
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.build.generic_platform import *

from litex.soc.interconnect.csr import *
from litex.soc.interconnect import wishbone

from migen.genlib.cdc import BlindTransfer

from camera_d8m import Camera_D8M
from memlogic import MemLogic

class _CRG(Module): # Clock Region definition
    def __init__(self, platform, sys_clk_freq):
        self.rst = Signal()
        self.clock_domains.cd_sys = ClockDomain()
        self.clock_domains.cd_d8m = ClockDomain()
        self.clock_domains.cd_vga = ClockDomain()
        self.clock_domains.cd_sdram = ClockDomain()
        self.clock_domains.cd_sdram_ps = ClockDomain()
       
        clk50 = platform.request("clk50")

        # PLL - instanciating an Intel FPGA PLL outputing a clock at sys_clk_freq
        self.submodules.pll = pll = Max10PLL(speedgrade="-7")
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(clk50, 50e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)
        pll.create_clkout(self.cd_sdram, sys_clk_freq*2)
        pll.create_clkout(self.cd_sdram_ps, sys_clk_freq*2, phase=-108)
        pll.create_clkout(self.cd_vga,  sys_clk_freq/2)
        pll.create_clkout(self.cd_d8m,  20e6)
        
class BaseSoC(SoCCore): # SoC definition - memory sizes are overloaded

    mem_map = {
      "logic_memory": 0x80000000,  # this just needs to be a unique block
    }
    mem_map.update(SoCCore.mem_map)

    def __init__(self, sys_clk_freq=int(50e6), with_video_terminal=False, **kwargs):
        platform = terasic_de10lite.Platform()

        # SoCCore ----------------------------------------------------------------------------------
        #These kwargs overwrite the value find on soc / soc_core
        #So you can change here the sizes of the different memories
        kwargs["integrated_rom_size"] = 0x8000 # chose rom size, holding bootloader (min = 0x6000)
        kwargs["integrated_sram_size"] = 0x8000 # chose sram size, holding stack and heap. (min = 0x6000)
        kwargs["integrated_main_ram_size"] = 0x10000 # 0 means external RAM is used, non 0 allocates main RAM internally
        kwargs["uart_name"] = "arduino_serial"

        platform.add_extension([("d8m", 0,
                        Subsignal("mipi_d", Pins(
                            "W9 V8 W8 V7 W7 W6 V5 W5",
                            "AA15 AA14")),
                        Subsignal("mipi_rst_n",   Pins("AA8")),
                        Subsignal("mipi_clk", Pins("W10")),
                        Subsignal("mipi_hs",    Pins("AA9")),
                        Subsignal("mipi_vs",  Pins("AB10")),
                        Subsignal("mipi_cs_n",   Pins("Y8")),
                        Subsignal("mipi_ref_clk", Pins("AB11")),
                        Subsignal("mipi_scl", Pins("AA5")),
                        Subsignal("mipi_sda", Pins("Y4")),
                        Subsignal("cam_pwdn_n",  Pins("Y7")),
                        Subsignal("cam_scl", Pins("AA7")),
                        Subsignal("cam_sda", Pins("Y6")), 
                        Subsignal("mipi_clk_rsd", Pins("V10")), 
                        Subsignal("mipi_mclk", Pins("AA6")),
                        Subsignal("cam_resv", Pins("AB2")),  
                        IOStandard("3.3-V LVTTL")
                    )])

        platform.add_extension([("arduino_serial", 0,
                                    Subsignal("tx", Pins("AA19"), IOStandard("3.3-V LVTTL")), # Arduino IO11
                                    Subsignal("rx", Pins("Y19"), IOStandard("3.3-V LVTTL"))  # Arduino IO12
                                ),])
        
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident          = "LiteX SoC on DE10-Lite",
            **kwargs)

        self.submodules.crg = _CRG(platform, sys_clk_freq) # CRG instanciation   
       
        
        self.submodules.camera = Camera_D8M(platform)
        self.add_csr("camera")

        # infer the logic block with memory
        memdepth = 32*32
        data_width = 32
        length = memdepth * data_width//8
        self.submodules.logicmem = MemLogic(data_width,memdepth)

        # define the memory region size/location
        # memdepth is the depth of the memory inferred in your logic block
        # the length is in bytes, so for example if the data_width of your memory
        # block is 32 bits, the total length is memdepth * 4
        self.add_memory_region("logic_memory", self.mem_map["logic_memory"], length, type='io')

        self.add_wb_slave(self.mem_map["logic_memory"], self.logicmem.bus)

        # Writing in the scratch-pad mem
        addr = Signal(max=length)

        self.sync.vga += [
            If(self.camera.pvalid==1,
                self.logicmem.logic_write_data.eq(self.camera.pixel_o),
                self.logicmem.local_adr.eq(addr),
                addr.eq(addr+1)
            ),

            If(self.camera.framedone_vga==1,
                addr.eq(0)
            )
        ]


def main(): # Instanciating the SoC and options
    parser = argparse.ArgumentParser(description="LiteX SoC on DE10-Lite")
    parser.add_argument("--build",               action="store_true", help="Build bitstream")
    parser.add_argument("--load",                action="store_true", help="Load bitstream")
    parser.add_argument("--sys-clk-freq",        default=50e6,        help="System clock frequency (default: 50MHz)")
    parser.add_argument("--csr_csv",            default="csr.csv",    help="Write SoC mapping to the specified CSV file.")
    parser.add_argument("--with-video-terminal", action="store_true", help="Enable Video Terminal (VGA)")
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq        = int(float(args.sys_clk_freq)),
        with_video_terminal = args.with_video_terminal,
        
        **soc_core_argdict(args)
    )

    builder = Builder(soc, **builder_argdict(args))
    builder.build(run=args.build)
    soc.do_exit(builder)
    generate_docs(soc, "build/documentation",
                        project_name="My SoC",
                        author="LiteX User")
    generate_svd(soc, "build/documentation")

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(os.path.join(builder.gateware_dir, soc.build_name + ".sof"))

if __name__ == "__main__":
    main()
