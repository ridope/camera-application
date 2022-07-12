#!/usr/bin/env python3

# This file is part of Ridope project.
# Modified 2022 by lesteves <lesteves@insa-rennes.fr>
# SPDX-License-Identifier: BSD-2-Clause

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

        self.output = Signal(8)
        self.read_en = Signal()
        
        vga_pads = platform.request("vga")
        btn_pads = platform.request_all("user_btn")
       
        led_pads = platform.request_all("user_led")
        sw_pads = platform.request_all("user_sw")
        sensor_pads = platform.request("d8m")

        #=======================================================
        #  Signals declarations
        #=======================================================
        mipi_rst_n = Signal()

        cam_mipi_release = Signal()
        mipi_bridge_release = Signal()
        i2c_release = Signal()
        auto_foc = Signal()
        ready = Signal()

        camera_i2c_scl = Signal()
        camera_i2c_scl_af = Signal()
        camera_i2c_scl_mipi = Signal()
        
        dly_rst_1 = Signal()
        vga_ctrl_clk = Signal()

        self.clock_domains.cd_pixclk = ClockDomain()
  
        sys_clk = ClockSignal("sys")
        mipi_refclk = ClockSignal("d8m")

        read_data = Signal(16)
        read = Signal()

        x_cont = Signal(12)
        y_cont = Signal(12)

        trigger_start = Signal()
        capture_cmd = Signal()
        capture_cmd_n = Signal()
        trigger_end = Signal()

        sccd_r = Signal(8)
        sccd_g = Signal(8)
        sccd_b = Signal(8)

        dly_rst_0 = Signal()
        dly_rst_1 = Signal()
        dly_rst_2 = Signal()
        
        self.framedone_vga = Signal()

        vga_r = Signal(4)
        vga_g = Signal(4)
        vga_b = Signal(4)

        vga_r_a = Signal(8)
        vga_g_a = Signal(8)
        vga_b_a = Signal(8)
        
        #=======================================================
        #  Structural coding
        #=======================================================
        # D8M

        #------ MIPI BRIGE & CAMERA RESET  --
        self.comb += sensor_pads.cam_pwdn_n.eq(1)
        self.comb += sensor_pads.mipi_cs_n.eq(0)
        self.comb += sensor_pads.mipi_rst_n.eq(mipi_rst_n)
        
        #------ CAMERA MODULE I2C SWITCH  --
        self.comb += i2c_release.eq(cam_mipi_release&mipi_bridge_release)
        self.comb += [
            If(i2c_release==1,
                camera_i2c_scl.eq(camera_i2c_scl_af)
            ).Else(
                camera_i2c_scl.eq(camera_i2c_scl_mipi)
            )
        ]
       
        self.comb += sensor_pads.mipi_ref_clk.eq(mipi_refclk)

        self.comb += led_pads.eq(sw_pads)
        self.comb += vga_pads.r.eq(vga_r)
        self.comb += vga_pads.g.eq(vga_g)
        self.comb += vga_pads.b.eq(vga_b)

        self.comb += self.cd_pixclk.clk.eq(sensor_pads.mipi_clk)
                 
        self.submodules.trigstart = BlindTransfer("sys", "pixclk")
        self.comb += [self.trigstart.i.eq(self.input.fields.Trigger), trigger_start.eq(self.trigstart.o)]

        self.comb += [
            capture_cmd.eq(~(trigger_end | capture_cmd_n)),
            capture_cmd_n.eq(~(trigger_start | capture_cmd)),
            ]

        # Reset module
        self.specials += Instance("RESET_DELAY",
            i_iCLK = sys_clk,
            i_iRST = btn_pads[0],
            o_oRST_0 = dly_rst_0,
            o_oRST_1 = dly_rst_1,
            o_oRST_2 = dly_rst_2,
            o_oREADY = mipi_rst_n
        )

        # Reset module
        self.specials += Instance("MIPI_BRIDGE_CAMERA_Config",
            i_CLK_50 = sys_clk,
            i_RESET_N = mipi_rst_n,
            i_TEST_REG = self.test.fields.Pattern,
            i_WSIZE_REG = self.control.fields.WSize,
            i_HSIZE_REG = self.control.fields.HSize,
            o_MIPI_I2C_SCL = sensor_pads.mipi_scl,
            io_MIPI_I2C_SDA = sensor_pads.mipi_sda,
            o_MIPI_I2C_RELEASE = mipi_bridge_release,
            o_CAMERA_I2C_SCL = sensor_pads.cam_scl,
            io_CAMERA_I2C_SDA = sensor_pads.cam_sda,
            o_CAMERA_I2C_RELAESE = cam_mipi_release
        )

        # D5M image capture
        self.specials += Instance("D8M_SET",
            i_RESET_SYS_N = mipi_rst_n,
            i_CLOCK_50 = sys_clk,
            i_CCD_DATA = sensor_pads.mipi_d,
            i_CCD_FVAL = sensor_pads.mipi_vs,
            i_CCD_LVAL = sensor_pads.mipi_hs,
            i_CCD_PIXCLK = sensor_pads.mipi_clk,
            i_READ_EN = read,
            i_VGA_CLK = vga_ctrl_clk,
            i_VGA_HS = vga_pads.hsync_n,
            i_VGA_VS = vga_pads.vsync_n,
            o_X_Cont = x_cont,
            o_Y_Cont = y_cont,
            o_sCCD_R = sccd_r,
            o_sCCD_G = sccd_g,
            o_sCCD_B = sccd_b        
        )

        self.specials += Instance("VGA_Controller_trig",
            # Host side
            i_iCLK = sensor_pads.mipi_clk,
            i_H_Cont = x_cont,
            i_V_Cont = y_cont,
            i_READ_Request = read,
            i_iRed = sccd_r[4:8],
            i_iGreen = sccd_g[4:8],
            i_iBlue = sccd_b[4:8],
            i_iVideo_W = self.vga.fields.W,
            i_iVideo_H = self.vga.fields.H,
            # VGA side
            o_oVGA_R = vga_r,
            o_oVGA_G = vga_g,
            o_oVGA_B = vga_b,
            o_oVGA_H_SYNC = vga_pads.hsync_n,
            o_oVGA_V_SYNC = vga_pads.vsync_n,
            # Control signal
            o_oVGA_CLOCK = vga_ctrl_clk,
            i_iRST_N = dly_rst_2
        )	  	        

        # counter = Signal(32)
        # fake_read_data = Signal(12)
        # counter.eq(0)

        # self.sync.vga += [
        #     If(read,
        #         counter.eq(counter+1),

        #         If((counter>0) & (counter <= 320),
        #             fake_read_data.eq(3840),
        #         ).Elif(
        #             (counter>320) & (counter <= 640),
        #             fake_read_data.eq(15),
        #         ).Else(
        #             fake_read_data.eq(0),
        #         )
        #     ).Else(
        #         counter.eq(0),
        #     )
        # ]

        # self.comb += [
        #     self.read_en.eq(read),
        #     self.output.eq(read_data[0:4])
        # ]

        platform.add_source_dir(path="../Camera/")
        platform.add_source_dir(path="../Camera/v/")
        platform.add_source_dir(path="../Camera/v/vga")
        platform.add_source_dir(path="../Camera/v/7SEG/")
        platform.add_source_dir(path="../Camera/v/Sdram_Control/")
        platform.add_source_dir(path="../Camera/v/D8M_control/")
        platform.add_source_dir(path="../Camera/v/D8M_control/Auto_Foc/")
        platform.add_source_dir(path="../Camera/v/D8M_control/Capture/")
        platform.add_source_dir(path="../Camera/v/D8M_control/Config/")
        platform.add_source_dir(path="../Camera/v/D8M_control/I2C/")
