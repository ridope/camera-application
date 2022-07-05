#!/usr/bin/env python3

# This file is part of Ridope project.
# Modified 2022 by lesteves <lesteves@insa-rennes.fr>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *
from litex.soc.interconnect.csr import *

from migen.genlib.cdc import BlindTransfer


class Camera(Module, AutoCSR):
    
    def __init__(self, platform):
        n_regs = 2
        regs_size = 16 # bits

        img_size = 28*28 #pixels

        self.input = CSRStorage(n_regs*regs_size, fields=[
            CSRField("Trigger",  size=1, description="Triggers the sensor to start/stop the capture.", pulse=True),
            CSRField("Reset", size=1, description="Resets the sensor.", reset=1, pulse=True),
            CSRField("Exposure", size=16, description="Sensor exposure", reset=1000),
        ])

        self.d5m_control = CSRStorage(fields=[
            CSRField("RowSize", size=16, description="Sensor Row Size", reset=1919),
            CSRField("ColSize", size=16, description="Sensor Col Size", reset=2559),
        ])

        # self.output = CSRStatus(fields=[
        #     CSRField("Image",  size=img_size, description="The image captured by the sensor."),
        # ])
        
        
        sdram_clock_pad = platform.request("sdram_clock")
        vga_pads = platform.request("vga")
        sdram_pads = platform.request("sdram")
        btn_pads = platform.request_all("user_btn")
       
        led_pads = platform.request_all("user_led")
        sw_pads = platform.request_all("user_sw")
        sensor_pads = platform.request("trdb")
  
        #=======================================================
        #  Signals declarations
        #=======================================================
        d5m_trigger = Signal()
        d5m_rstn = Signal()
        dly_rst_1 = Signal()
        vga_ctrl_clk = Signal()

        self.clock_domains.cd_pixclk = ClockDomain()
  
        sys_clk = ClockSignal("sys")
        vga_clk = ClockSignal("vga")
        d5m_pixclk = ClockSignal("pixclk")
        d5m_clkin = ClockSignal("d5m")
        sdram_clk = ClockSignal("sdram")
        sdram_clk_ps = ClockSignal("sdram_ps")

        read_data = Signal(16)
        read = Signal()

        mccd_data = Signal(12)
        mccd_dval = Signal()
        x_cont = Signal(12)
        y_cont = Signal(12)
        frame_count = Signal(32)
        trigger_start = Signal()
        capture_cmd = Signal()
        capture_cmd_n = Signal()
        trigger_end = Signal()

        rccd_data = Signal(12)
        rccd_lval = Signal()
        rccd_fval = Signal()
        sccd_r = Signal(12)
        sccd_g = Signal(12)
        sccd_b = Signal(12)
        sccd_dval = Signal()
        
        dly_rst_0 = Signal()
        dly_rst_1 = Signal()
        dly_rst_2 = Signal()
        dly_rst_3 = Signal()
        dly_rst_4 = Signal()

        framenew_capture = Signal()
        framenew_raw = Signal()

        vga_r = Signal(4)
        vga_g = Signal(4)
        vga_b = Signal(4)

        auto_start = Signal() 

        
        #=======================================================
        #  Structural coding
        #=======================================================
        # D5M
        self.comb += d5m_trigger.eq(1)
        self.comb += d5m_rstn.eq(dly_rst_1)
        self.comb += vga_ctrl_clk.eq(~vga_clk)
        self.comb += led_pads.eq(sw_pads)
        self.comb += vga_pads.r.eq(vga_r)
        self.comb += vga_pads.g.eq(vga_g)
        self.comb += vga_pads.b.eq(vga_b)
        self.comb += auto_start.eq(btn_pads[0] & dly_rst_3 & ~dly_rst_4)
        self.comb += self.cd_pixclk.clk.eq(sensor_pads.pixclk)
        self.comb += sensor_pads.xclkin.eq(d5m_clkin)
        self.comb += sdram_clock_pad.eq(sdram_clk_ps)

         
        self.submodules.trigstart = BlindTransfer("sys", "pixclk")
        self.comb += [self.trigstart.i.eq(self.input.fields.Trigger), trigger_start.eq(self.trigstart.o)]

        self.comb += [
            capture_cmd.eq(~(trigger_end | capture_cmd_n)),
            capture_cmd_n.eq(~(trigger_start | capture_cmd)),
            ]

        #D5M read 
        self.sync.pixclk += [
            rccd_data.eq(sensor_pads.d), 
            rccd_lval.eq(sensor_pads.lval),
            rccd_fval.eq(sensor_pads.fval),
            ]

        # SDRAM Frame buffer
        self.specials += Instance("Sdram_Control",
            # Host Side
            i_REF_CLK = sys_clk,
            i_RESET_N = 1,
            # FIFO write side
            i_WR_DATA = Cat(sccd_b[8:12], sccd_g[8:12],sccd_r[8:12],0,0,0,0),
            i_WR = sccd_dval,
            i_WR_ADDR = 0,
            i_WR_MAX_ADDR = 640*480,
            i_WR_LENGTH = 128,
            i_WR_LOAD = framenew_raw,
            i_WR_CLK = d5m_pixclk,
            # FIFO read side
            o_RD_DATA = read_data,
            i_RD = read,
            i_RD_ADDR = 0,
            i_RD_MAX_ADDR = 640*480,
            i_RD_LENGTH = 128,
            i_RD_LOAD = ~dly_rst_0,
            i_RD_CLK = ~vga_ctrl_clk,
            # SDRAM side
            o_SA = sdram_pads.a,
            o_BA = sdram_pads.ba,
            o_CS_N = sdram_pads.cs_n,
            o_CKE = sdram_pads.cke,
            o_RAS_N = sdram_pads.ras_n,
            o_CAS_N = sdram_pads.cas_n,
            o_WE_N = sdram_pads.we_n,
            io_DQ = sdram_pads.dq,
            o_DQM = sdram_pads.dm,
            i_CLK = sdram_clk
        )

        # Reset module
        self.specials += Instance("Reset_Delay",
            i_iCLK = sys_clk,
            i_iRST = btn_pads[0],
            o_oRST_0 = dly_rst_0,
            o_oRST_1 = dly_rst_1,
            o_oRST_2 = dly_rst_2,
            o_oRST_3 = dly_rst_3,
            o_oRST_4 = dly_rst_4,
        )

        # D5M image capture
        self.specials += Instance("CCD_Capture",
            o_oDATA = mccd_data,
            o_oDVAL = mccd_dval,
            o_oX_Cont = x_cont,
            o_oY_Cont = y_cont,
            o_oDone = trigger_end,
            o_oFrameNew = framenew_capture,
            o_oFrame_Cont = frame_count,
            i_iDATA = rccd_data,
            i_iFVAL = rccd_fval,
            i_iLVAL = rccd_lval,
            i_iSTART = ~sw_pads[1]|auto_start,
            i_iEND = ~sw_pads[0],#capture_cmd_n,
            i_iCLK = d5m_pixclk,
            i_iRST = dly_rst_2
        )

        # D5M raw date convert to RGB data
        self.specials += Instance("RAW2RGB",
            i_iCLK = ~d5m_pixclk,
            i_iRST = dly_rst_1,
            i_iDATA = mccd_data,
            i_iDVAL = mccd_dval,
            i_iFrameNew = framenew_capture,
            o_oFrameNew = framenew_raw,
            o_oRed = sccd_r,
            o_oGreen = sccd_g,
            o_oBlue = sccd_b,
            o_oDVAL = sccd_dval,
            i_iX_Cont = x_cont,
            i_iY_Cont = y_cont
        )

        # Frame count display
        self.specials += Instance("SEG7_LUT_8",
            o_oSEG0 = platform.request("seven_seg",0),
            o_oSEG1 = platform.request("seven_seg",1),
            o_oSEG2 = platform.request("seven_seg",2),
            o_oSEG3 = platform.request("seven_seg",3),
            o_oSEG4 = platform.request("seven_seg",4),
            o_oSEG5 = platform.request("seven_seg",5),
            i_iDIG = frame_count[0:24]
        )

        # D5M I2C control
        self.specials += Instance("I2C_CCD_Config",
            # Host side
            i_iCLK = sys_clk,
            i_iRST_N = dly_rst_2,
            i_iEnable = sw_pads[5],
            i_iEXPOSURE = self.input.fields.Exposure,
            i_iRowSize = self.d5m_control.fields.RowSize,
            i_iColSize = self.d5m_control.fields.ColSize,
            i_iEXPOSURE_ADJ = sw_pads[2],
            i_iEXPOSURE_DEC_p = sw_pads[3],
            i_iZOOM_MODE_SW = sw_pads[9],
            # I2C side
            o_I2C_SCLK = sensor_pads.sclk,
            io_I2C_SDAT = sensor_pads.sdata
        )

        counter = Signal(32)
        fake_read_data = Signal(12)
        counter.eq(0)

        self.sync.vga += [
            If(read,
                counter.eq(counter+1),

                If((counter>0) & (counter <= 320),
                    fake_read_data.eq(3840),
                ).Elif(
                    (counter>320) & (counter <= 640),
                    fake_read_data.eq(15),
                ).Else(
                    fake_read_data.eq(0),
                )
            ).Else(
                counter.eq(0),
            )
        ]

        # VGA Controller module
        self.specials += Instance("VGA_Controller",
            # Host side
            o_oRequest = read,
            i_iRed = read_data[8:12],
            i_iGreen = read_data[4:8],
            i_iBlue = read_data[0:4],
            # VGA side
            o_oVGA_R = vga_r,
            o_oVGA_G = vga_g,
            o_oVGA_B = vga_b,
            o_oVGA_H_SYNC = vga_pads.hsync_n,
            o_oVGA_V_SYNC = vga_pads.vsync_n,
            # Control signal
            i_iVGA_CLK = vga_ctrl_clk,
            i_iRST_n = dly_rst_2
        )


        platform.add_source_dir(path="../Camera/")
        platform.add_source_dir(path="../Camera/v/")
        platform.add_source_dir(path="../Camera/v/vga")
        platform.add_source_dir(path="../Camera/v/7SEG/")
        platform.add_source_dir(path="../Camera/v/Sdram_Control/")
        platform.add_source_dir(path="../Camera/v/TRDB-DM_Control/")

        platform.toolchain.additional_sdc_commands = [
            "create_generated_clock -name sdram_clk -source [get_pins {ALTPLL|auto_generated|pll1|clk[2]}] [get_ports {sdram_clock}]",
            "derive_pll_clocks",
            "derive_clock_uncertainty",
            "set_input_delay -max -clock sdram_clk 5.9 [get_ports sdram_dq*]",
            "set_input_delay -min -clock sdram_clk 3.0 [get_ports sdram_dq*]",
            "set_multicycle_path -from [get_clocks {sdram_clk}] -to [get_clocks {ALTPLL|auto_generated|pll1|clk[1]}] -setup 2",
            "set_output_delay -max -clock sdram_clk 1.6  [get_ports {sdram_dq* sdram_dm*}]",
            "set_output_delay -min -clock sdram_clk -0.9 [get_ports {sdram_dq* sdram_dm*}]",
            "set_output_delay -max -clock sdram_clk 1.6  [get_ports {sdram_a* sdram_ba* sdram_ras_n sdram_cas_n sdram_we_n sdram_cke sdram_cs_n}]",
            "set_output_delay -min -clock sdram_clk -0.9 [get_ports {sdram_a* sdram_ba* sdram_ras_n sdram_cas_n sdram_we_n sdram_cke sdram_cs_n}]"
        ]
