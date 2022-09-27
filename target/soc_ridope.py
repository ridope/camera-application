#!/usr/bin/env python3

# This file is part of LiteX-Boards.
# Copyright (c) 2019 msloniewski <marcin.sloniewski@gmail.com>
# Modified 2021 by mpelcat <mpelcat@insa-rennes.fr>
# Modified 2022 by lesteves <lesteves@insa-rennes.fr>
# SPDX-License-Identifier: BSD-2-Clause

import os
import argparse
import sys

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

# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '../ext_lib/Asymetric-Multi-Processing/Dual_Core')

from amp import BaseSoC

def main(): # Instanciating the SoC and options
    parser = argparse.ArgumentParser(description="LiteX SoC on DE10-Lite")
    parser.add_argument("--build",               action="store_true", help="Build bitstream")
    parser.add_argument("--load",                action="store_true", help="Load bitstream")
    parser.add_argument("--build_dir",      default='',                  help="Base output directory.")
    parser.add_argument("--sys-clk-freq",        default=50e6,        help="System clock frequency (default: 50MHz)")
    parser.add_argument("--csr_csv",            default="csr.csv",    help="Write SoC mapping to the specified CSV file.")
    parser.add_argument("--with-video-terminal", action="store_true", help="Enable Video Terminal (VGA)")
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    platform = terasic_de10lite.Platform()

    platform.add_extension([
                        ("arduino_serial", 0,
                            Subsignal("tx", Pins("AA19"), IOStandard("3.3-V LVTTL")), # Arduino IO11
                            Subsignal("rx", Pins("Y19"), IOStandard("3.3-V LVTTL"))  # Arduino IO12
                        ),
                        ("arduino_serial", 1,
                            Subsignal("tx", Pins("AB20"), IOStandard("3.3-V LVTTL")), # Arduino IO11
                            Subsignal("rx", Pins("F16"), IOStandard("3.3-V LVTTL"))  # Arduino IO12
                        ),
                        ])

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

    sys_clk_freq = int(float(args.sys_clk_freq))

    soc = BaseSoC(
        platform_name  = 'De10Lite',
        platform       = platform,
        sys_clk_freq   = sys_clk_freq,
        bus_data_width=  32,
        mux            = False,
        build_dir      = args.build_dir,
        shared_ram_size= int("0x200",0),
        name_1         = "femtorv",
        name_2         = "firev",
        sram_1_size    = int("0x8000",0),
        sram_2_size    = int("0x10000",0),
        ram_1_size     = int("0x2000",0),
        ram_2_size     = int("0x0",0),
        rom_1_size     = int("0x8000",0),
        rom_2_size     = int("0x8000",0),
        sp_1_size      = int("0x1000",0),
        sp_2_size      = int("0x0",0),
    )

    soc.crg.clock_domains.cd_d8m = ClockDomain()
    soc.crg.clock_domains.cd_vga = ClockDomain()
    soc.crg.clock_domains.cd_sdram = ClockDomain()
    soc.crg.clock_domains.cd_sdram_ps = ClockDomain()

    soc.crg.pll.create_clkout(soc.crg.cd_sdram, sys_clk_freq*2)
    soc.crg.pll.create_clkout(soc.crg.cd_sdram_ps, sys_clk_freq*2, phase=-108)
    soc.crg.pll.create_clkout(soc.crg.cd_vga,  sys_clk_freq/2)
    soc.crg.pll.create_clkout(soc.crg.cd_d8m,  20e6)

    soc.submodules.camera = Camera_D8M(platform)
    soc.add_csr("camera")

    # infer the logic block with memory
    memdepth = 28*28
    data_width = 32
    length = memdepth * data_width//8
    soc.submodules.logicmem = MemLogic(soc,soc.bus1.data_width,int("0x1000",0),soc.bus1.bursting)

    # Writing in the scratch-pad mem
    addr = Signal(32)
    write_data = Signal(data_width)
    logic_counter = Signal(max=3)

    soc.sync.vga += [
        If(soc.camera.read_request==1,
            write_data.eq(Cat(write_data[8:32],soc.camera.r_auto)),
            If(logic_counter == 3,
                soc.logicmem.logic_write_data.eq(write_data),
                soc.logicmem.local_adr.eq(addr),
                addr.eq(addr+1),
                logic_counter.eq(0),
            ).Else(
                logic_counter.eq(logic_counter+1),
            )     
            
        ),

        If(soc.camera.framedone_vga==1,
            addr.eq(0),
            logic_counter.eq(0)
        )
    ]

       
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
