#!/usr/bin/env python3

# This file is part of Ridope project.
# Modified 2022 by lesteves <lesteves@insa-rennes.fr>
# SPDX-License-Identifier: BSD-2-Clause

from this import s
from migen import *
from litex.soc.interconnect.csr import *

from migen.genlib.cdc import BlindTransfer


class Camera_D8M(Module, AutoCSR):
    
    def __init__(self, platform):
        self.input = CSRStorage(fields=[
            CSRField("Trigger",  size=1, description="Triggers the sensor to start/stop the capture.", pulse=True),
            CSRField("Reset", size=1, description="Resets the sensor.", reset=1, pulse=True),
            CSRField("Exposure", size=16, description="Sensor exposure", reset=1000),
        ])

        self.control = CSRStorage(fields=[
            CSRField("WSize", size=16, description="Sensor Width Size", reset=640),
            CSRField("HSize", size=16, description="Sensor Height Size", reset=480)
        ])

        self.test = CSRStorage(fields=[
            CSRField("Pattern", size=8, description="Test Pattern Register", reset=146)
        ])

        self.sram = CSRStorage(fields=[
            CSRField("RD_L", size=9, description="SRAM Read Length", reset=32),
            CSRField("WR_L", size=9, description="SRAM Write Length", reset=32),
        ])

        self.vga = CSRStorage(fields=[
            CSRField("W", size=16, description="VGA Video Width", reset=640),
            CSRField("H", size=16, description="VGA Video Height", reset=480),
        ])

        sys_clk = ClockSignal("sys")
        mipi_refclk = ClockSignal("d8m")
        vga_clk = ClockSignal("vga")
        sdram_ctrl_clk = ClockSignal("sdram")
        sdram_clk_ps = ClockSignal("sdram_ps")

        vga_pads = platform.request("vga")
        btn_pads = platform.request_all("user_btn")
       
        led_pads = platform.request_all("user_led")
        sw_pads = platform.request_all("user_sw")
        sdram_clock_pad = platform.request("sdram_clock")
        sdram_pads = platform.request("sdram")
        sensor_pads = platform.request("d8m")

        self.framedone_vga = Signal()
        framenew_capture = Signal()

        sdram_rd_data = Signal(16)
        dly_rst_0 = Signal()
        dly_rst_1 = Signal()
        dly_rst_2 = Signal()
        vga_ctrl_clk = Signal()

        ready = Signal()

        red = Signal(8)
        green = Signal(8)
        blue = Signal(8)

        vga_h_cnt = Signal(13)
        vga_v_cnt = Signal(13)

        read_request = Signal()
        b_auto = Signal(8)
        g_auto = Signal(8)
        r_auto = Signal(8)
        reset_n = Signal()

        i2c_release = Signal()
        auto_foc = Signal()
        camera_i2c_scl_mipi = Signal()
        camera_i2c_scl_af = Signal()
        camera_mipi_release = Signal()
        mipi_bridge_release = Signal()

        lut_mipi_pixel_hs = Signal()
        lut_mipi_pixel_vs = Signal()
        lut_mipi_pixel_d = Signal(10)
        mipi_pixel_clk_ = Signal()

        #=======================================================
        # Structural coding
        #=======================================================
        #--INPU MIPI-PIXEL-CLOCK DELAY

        # Reset module
        self.specials += Instance("CLOCK_DELAY",
            i_iCLK = sensor_pads.mipi_clk,
            o_oCLK = mipi_pixel_clk_
        )

        self.comb += [
            lut_mipi_pixel_hs.eq(sensor_pads.mipi_hs),
            lut_mipi_pixel_vs.eq(sensor_pads.mipi_vs),
            lut_mipi_pixel_d.eq(sensor_pads.mipi_d),
            sensor_pads.mipi_ref_clk.eq(mipi_refclk)
        ]

        self.comb += sdram_clock_pad.eq(sdram_clk_ps)
        self.comb += vga_ctrl_clk.eq(~vga_clk)
        self.comb += led_pads.eq(sw_pads)

        #------ MIPI BRIGE & CAMERA RESET  --
        self.comb += [
            sensor_pads.cam_pwdn_n.eq(sw_pads[9]),
            sensor_pads.mipi_cs_n.eq(0),
            sensor_pads.mipi_rst_n.eq(reset_n),
        ]

        #------ CAMERA MODULE I2C SWITCH  --
        self.comb += [ 
            i2c_release.eq(camera_mipi_release&mipi_bridge_release),
            If(
                i2c_release == 1,
                sensor_pads.cam_scl.eq(camera_i2c_scl_af)
            ).Else(
                sensor_pads.cam_scl.eq(camera_i2c_scl_mipi)
            )
        ]

        #----- RESET RELAY  --	
        self.specials += Instance("RESET_DELAY",
            i_iRST = btn_pads[0],
            i_iCLK = sys_clk,
            o_oRST_0 = dly_rst_0,
            o_oRST_1 = dly_rst_1,
            o_oRST_2 = dly_rst_2,
            o_oREADY = reset_n
        )

        #------ MIPI BRIGE & CAMERA SETTING  --  
        self.specials += Instance("MIPI_BRIDGE_CAMERA_Config",
            i_RESET_N = reset_n,
            i_CLK_50 = sys_clk,
            o_MIPI_I2C_SCL = sensor_pads.mipi_scl,
            io_MIPI_I2C_SDA = sensor_pads.mipi_sda,
            o_MIPI_I2C_RELEASE = mipi_bridge_release,
            o_CAMERA_I2C_SCL = camera_i2c_scl_mipi,
            io_CAMERA_I2C_SDA = sensor_pads.cam_sda,
            o_CAMERA_I2C_RELAESE = camera_mipi_release       
        )

        self.comb += [
            If(lut_mipi_pixel_hs == 0 and lut_mipi_pixel_vs==0,
                framenew_capture.eq(1)
            ).Else(
                framenew_capture.eq(0)
            )
        ]

        # SDRAM Frame buffer
        self.specials += Instance("Sdram_Control",
            # Host Side
            i_CLK = sdram_ctrl_clk,
            i_RESET_N = btn_pads[0],
            # FIFO write side
            i_WR_DATA = Cat(lut_mipi_pixel_d,0,0,0,0,0,0),
            i_WR = lut_mipi_pixel_hs&lut_mipi_pixel_vs,
            i_WR_ADDR = 0,
            i_WR_MAX_ADDR = 640*480,
            i_WR_LENGTH = self.sram.fields.WR_L,
            i_WR_LOAD = ~dly_rst_0,#framenew_capture,
            i_WR_CLK = mipi_pixel_clk_,
            # FIFO read side
            o_RD_DATA = sdram_rd_data,
            i_RD = read_request,
            i_RD_ADDR = 0,
            i_RD_MAX_ADDR = 640*480,
            i_RD_LENGTH = self.sram.fields.RD_L,
            i_RD_LOAD = ~dly_rst_1,#self.framedone_vga,
            i_RD_CLK = vga_ctrl_clk,
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
        )

        #------ CMOS CCD_DATA TO RGB_DATA -- 
        self.specials += Instance("RAW2RGB_J",
            i_RST = vga_pads.vsync_n,
            i_iDATA = sdram_rd_data,

            i_VGA_CLK = vga_ctrl_clk,
            i_READ_Request = read_request,
            i_VGA_HS = vga_pads.hsync_n,
            i_VGA_VS = vga_pads.vsync_n,
            
            o_oRed = red,
            o_oGreen = green,
            o_oBlue = blue
        )

        # VGA Controller module
        self.specials += Instance("VGA_Controller",
            # Host side
            o_oRequest = read_request,
            i_iRed = red,
            i_iGreen = green,
            i_iBlue = blue,

            o_oFrameDone = self.framedone_vga,            
            #i_iVideo_W = self.vga.fields.W,
            #i_iVideo_H = self.vga.fields.H,

            # VGA side
            o_oVGA_R = r_auto,
            o_oVGA_G = g_auto,
            o_oVGA_B = b_auto,
            o_oVGA_H_SYNC = vga_pads.hsync_n,
            o_oVGA_V_SYNC = vga_pads.vsync_n,

            # Control signal
            i_iCLK = vga_ctrl_clk,
            i_iRST_N = dly_rst_2,
            o_H_Cont = vga_h_cnt,
            o_V_Cont = vga_v_cnt
        )

        #------AOTO FOCUS ENABLE  --
        self.specials += Instance("AUTO_FOCUS_ON",
            i_CLK_50 = sys_clk,
            i_I2C_RELEASE = i2c_release,
            o_AUTO_FOC = auto_foc,
        )

        #------AOTO FOCUS ADJ  --
        self.specials += Instance("FOCUS_ADJ",
            i_CLK_50 = sys_clk,
            i_RESET_N = i2c_release,
            i_RESET_SUB_N = i2c_release,
            i_AUTO_FOC = btn_pads[1]&auto_foc,
            i_SW_Y = 0,
            i_SW_H_FREQ = 0,
            i_SW_FUC_LINE = sw_pads[3],
            i_SW_FUC_ALL_CEN = sw_pads[3],
            i_VIDEO_HS = vga_pads.hsync_n,
            i_VIDEO_VS = vga_pads.vsync_n,
            i_VIDEO_CLK = vga_ctrl_clk,
            i_VIDEO_DE = read_request,
            i_iR = r_auto,
            i_iG = g_auto,
            i_iB = b_auto,
            o_oR = vga_pads.r,
            o_oG = vga_pads.g,
            o_oB = vga_pads.b,

            o_READY = ready,
            o_SCL = camera_i2c_scl_af,
            io_SDA = sensor_pads.mipi_sda
        )

         


        platform.add_source_dir(path="../Camera/")


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
