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

_io = [

    # Leds
    ("user_led", 0, Pins("A8"),  IOStandard("3.3-V LVTTL")),
    ("user_led", 1, Pins("A9"),  IOStandard("3.3-V LVTTL")),
    ("user_led", 2, Pins("A10"), IOStandard("3.3-V LVTTL")),
    ("user_led", 3, Pins("B10"), IOStandard("3.3-V LVTTL")),
    ("user_led", 4, Pins("D13"), IOStandard("3.3-V LVTTL")),
    ("user_led", 5, Pins("C13"), IOStandard("3.3-V LVTTL")),
    ("user_led", 6, Pins("E14"), IOStandard("3.3-V LVTTL")),
    ("user_led", 7, Pins("D14"), IOStandard("3.3-V LVTTL")),
    ("user_led", 8, Pins("A11"), IOStandard("3.3-V LVTTL")),
    ("user_led", 9, Pins("B11"), IOStandard("3.3-V LVTTL"))

]

class FomuRGB(Module, AutoCSR):
    def __init__(self, pads):
        self.output = CSRStorage(3)
        self.specials += Instance("SB_RGBA_DRV",
            i_CURREN = 0b1,
            i_RGBLEDEN = 0b1,
            i_RGB0PWM = self.output.storage[0],
            i_RGB1PWM = self.output.storage[1],
            i_RGB2PWM = self.output.storage[2],
            o_RGB0 = pads.r,
            o_RGB1 = pads.g,
            o_RGB2 = pads.b,
            p_CURRENT_MODE = "0b1",
            p_RGB0_CURRENT = "0b000011",
            p_RGB1_CURRENT = "0b000011",
            p_RGB2_CURRENT = "0b000011",
        )


""" class Camera(Module, AutoCSR):
    def __init__(self, platform, sdram_pads, sdram_clock_pad, vga_pads, sensor_pads, counter_hex, sw_pads, led_pads, btn_pads, sys_clk):
        n_regs = 2
        regs_size = 16 # bits

        img_size = 640*480 #pixels

        self.input = CSRStorage(n_regs*regs_size)
        self.output = CSRStatus(img_size*regs_size)

        self.specials += Instance("Camera",
            i_MAX10_CLK1_50 = sys_clk,
            i_MAX10_CLK2_50 = sys_clk,
            o_DRAM_ADDR    = sdram_pads.a,
            o_DRAM_BA = sdram_pads.ba,
            o_DRAM_CAS_N = sdram_pads.cas_n,
            o_DRAM_CKE = sdram_pads.cke,
            o_DRAM_CLK = sdram_clock_pad,
            o_DRAM_CS_N = sdram_pads.cs_n,
            io_DRAM_DQ = sdram_pads.dq,
            o_DRAM_LDQM = sdram_pads.dm,
            o_DRAM_RAS_N = sdram_pads.ras_n,
            o_DRAM_UDQM = sdram_pads.dm,
            o_DRAM_WE_N = sdram_pads.cs_n,
            o_HEX0 = counter_hex.seven_seg[0],
            o_HEX1 = counter_hex.seven_seg[1],
            o_HEX2 = counter_hex.seven_seg[2],
            o_HEX3 = counter_hex.seven_seg[3],
            o_HEX4 = counter_hex.seven_seg[4],
            o_HEX5 = counter_hex.seven_seg[5],
            i_KEY = btn_pads,
            o_LEDR = led_pads,
            i_SW = sw_pads,
            o_VGA_B = vga_pads.b,
            o_VGA_G = vga_pads.g,
            o_VGA_HS = vga_pads.hsync_n,
            o_VGA_R = vga_pads.r,
            o_VGA_VS = vga_pads.vsync_n
            i_D5M_D = sensor_pads.d,
            i_D5M_FVAL = sensor_pads.fval,
            i_D5M_LVAL = sensor_pads.lval,
            i_D5M_PIXLCLK = sensor_pads.pixclk,
            o_D5M_RESET_N = sensor_pads.rstn,
            o_D5M_SCLK = sensor_pads.sclk,
            i_D5M_SDATA = sensor_pads.sdata,
            i_D5M_STROBE = sensor_pads.strobe,
            o_D5M_TRIGGER = sensor_pads.trigger,
            o_D5M_XCLKIN = sensor_pads.xclkin,

        )

        platform.add_source_dir(path="../Camera/")
        platform.add_source_dir(path="../Camera/v/")
        platform.add_source_dir(path="../Camera/v/vga")
        platform.add_source_dir(path="../Camera/v/7SEG/")
        platform.add_source_dir(path="../Camera/v/Sdram_Control/")
        platform.add_source_dir(path="../Camera/v/TRDB-DM_Control/") """




class _CRG(Module): # Clock Region definition
    def __init__(self, platform, sys_clk_freq):
        self.rst = Signal()
        self.clock_domains.cd_sys = ClockDomain()
        self.clock_domains.cd_vga    = ClockDomain()

        clk50 = platform.request("clk50")

        # PLL - instanciating an Intel FPGA PLL outputing a clock at sys_clk_freq
        self.submodules.pll = pll = Max10PLL(speedgrade="-7")
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(clk50, 50e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)
        pll.create_clkout(self.cd_vga,  sys_clk_freq/2)

class BaseSoC(SoCCore): # SoC definition - memory sizes are overloaded
    def __init__(self, sys_clk_freq=int(50e6), with_video_terminal=False, **kwargs):
        platform = terasic_de10lite.Platform()

        # SoCCore ----------------------------------------------------------------------------------
        #These kwargs overwrite the value find on soc / soc_core
        #So you can change here the sizes of the different memories
        kwargs["integrated_rom_size"] = 0x8000 # chose rom size, holding bootloader (min = 0x6000)
        kwargs["integrated_sram_size"] = 0x8000 # chose sram size, holding stack and heap. (min = 0x6000)
        kwargs["integrated_main_ram_size"] = 0x10000 # 0 means external RAM is used, non 0 allocates main RAM internally
        
        SoCCore.__init__(self, platform, sys_clk_freq,
            ident          = "LiteX SoC on DE10-Lite",
            **kwargs)

        self.submodules.crg = _CRG(platform, sys_clk_freq) # CRG instanciation     
        
        # Led ------------------------------------------------------------------------------------
        led = platform.request_all("user_led")
        #self.submodules.leds = LedChaser(led, sys_clk_freq)
        #self.add_csr("leds")


        # GPIOs ------------------------------------------------------------------------------------
        gpio = platform.request_all("gpio_0")
        self.submodules.gpio = GPIOOut(gpio)
        self.add_csr("gpio")

        # 7SEGMENT ------------------------------------------------------------------------------------
        seg =  platform.request("seven_seg")
        self.submodules.seven = LedChaser(seg, sys_clk_freq)

        vga_pads = platform.request("vga")

        btn_user = platform.request_all("user_btn")

        vga_clk = ClockSignal("vga")

        self.specials += Instance("vga_controller",
            i_iRST_n = btn_user[0],
            i_iVGA_CLK = vga_clk,
            o_oHS = vga_pads.hsync_n,
            o_oVS = vga_pads.vsync_n, 
            o_oVGA_B = vga_pads.b,
            o_oVGA_G = vga_pads.g,
            o_oVGA_R = vga_pads.r
            )



        platform.add_source_dir(path="../VGA_Pattern/")
        platform.add_source_dir(path="../VGA_Pattern/v/")

        #Reset
        #btn0_press = UserButtonPress(platform.request("user_btn"))
        #self.submodules += btn0_press

        #self.submodules.camera = Camera(led)
        #self.add_csr("speriph")

        
        



def main(): # Instanciating the SoC and options
    parser = argparse.ArgumentParser(description="LiteX SoC on DE10-Lite")
    parser.add_argument("--build",               action="store_true", help="Build bitstream")
    parser.add_argument("--load",                action="store_true", help="Load bitstream")
    parser.add_argument("--sys-clk-freq",        default=50e6,        help="System clock frequency (default: 50MHz)")
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
