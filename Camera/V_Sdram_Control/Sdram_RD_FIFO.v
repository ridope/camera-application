// megafunction wizard: %FIFO%
// GENERATION: STANDARD
// VERSION: WM1.0
// MODULE: dcfifo 

// ============================================================
// File Name: Sdram_RD_FIFO.v
// Megafunction Name(s):
// 			dcfifo
//
// Simulation Library Files(s):
// 			
// ============================================================
// ************************************************************
// THIS IS A WIZARD-GENERATED FILE. DO NOT EDIT THIS FILE!
//
// 21.1.0 Build 842 10/21/2021 SJ Lite Edition
// ************************************************************


//Copyright (C) 2021  Intel Corporation. All rights reserved.
//Your use of Intel Corporation's design tools, logic functions 
//and other software and tools, and any partner logic 
//functions, and any output files from any of the foregoing 
//(including device programming or simulation files), and any 
//associated documentation or information are expressly subject 
//to the terms and conditions of the Intel Program License 
//Subscription Agreement, the Intel Quartus Prime License Agreement,
//the Intel FPGA IP License Agreement, or other applicable license
//agreement, including, without limitation, that your use is for
//the sole purpose of programming logic devices manufactured by
//Intel and sold by Intel or its authorized distributors.  Please
//refer to the applicable agreement for further details, at
//https://fpgasoftware.intel.com/eula.


// synopsys translate_off
`timescale 1 ps / 1 ps
// synopsys translate_on
module Sdram_RD_FIFO (
	aclr,
	data,
	rdclk,
	rdreq,
	wrclk,
	wrreq,
	q,
	rdempty,
	rdusedw,
	wrfull,
	wrusedw);

	input	  aclr;
	input	[15:0]  data;
	input	  rdclk;
	input	  rdreq;
	input	  wrclk;
	input	  wrreq;
	output	[15:0]  q;
	output	  rdempty;
	output	[8:0]  rdusedw;
	output	  wrfull;
	output	[8:0]  wrusedw;
`ifndef ALTERA_RESERVED_QIS
// synopsys translate_off
`endif
	tri0	  aclr;
`ifndef ALTERA_RESERVED_QIS
// synopsys translate_on
`endif

	wire [15:0] sub_wire0;
	wire  sub_wire1;
	wire [8:0] sub_wire2;
	wire  sub_wire3;
	wire [8:0] sub_wire4;
	wire [15:0] q = sub_wire0[15:0];
	wire  rdempty = sub_wire1;
	wire [8:0] rdusedw = sub_wire2[8:0];
	wire  wrfull = sub_wire3;
	wire [8:0] wrusedw = sub_wire4[8:0];

	dcfifo	dcfifo_component (
				.aclr (aclr),
				.data (data),
				.rdclk (rdclk),
				.rdreq (rdreq),
				.wrclk (wrclk),
				.wrreq (wrreq),
				.q (sub_wire0),
				.rdempty (sub_wire1),
				.rdusedw (sub_wire2),
				.wrfull (sub_wire3),
				.wrusedw (sub_wire4),
				.eccstatus (),
				.rdfull (),
				.wrempty ());
	defparam
		dcfifo_component.intended_device_family = "MAX 10",
		dcfifo_component.lpm_hint = "RAM_BLOCK_TYPE=M9K",
		dcfifo_component.lpm_numwords = 512,
		dcfifo_component.lpm_showahead = "OFF",
		dcfifo_component.lpm_type = "dcfifo",
		dcfifo_component.lpm_width = 16,
		dcfifo_component.lpm_widthu = 9,
		dcfifo_component.overflow_checking = "ON",
		dcfifo_component.rdsync_delaypipe = 4,
		dcfifo_component.read_aclr_synch = "OFF",
		dcfifo_component.underflow_checking = "ON",
		dcfifo_component.use_eab = "ON",
		dcfifo_component.write_aclr_synch = "OFF",
		dcfifo_component.wrsync_delaypipe = 4;


endmodule

// ============================================================
// CNX file retrieval info
// ============================================================
// Retrieval info: PRIVATE: AlmostEmpty NUMERIC "0"
// Retrieval info: PRIVATE: AlmostEmptyThr NUMERIC "-1"
// Retrieval info: PRIVATE: AlmostFull NUMERIC "0"
// Retrieval info: PRIVATE: AlmostFullThr NUMERIC "-1"
// Retrieval info: PRIVATE: CLOCKS_ARE_SYNCHRONIZED NUMERIC "0"
// Retrieval info: PRIVATE: Clock NUMERIC "4"
// Retrieval info: PRIVATE: Depth NUMERIC "512"
// Retrieval info: PRIVATE: Empty NUMERIC "1"
// Retrieval info: PRIVATE: Full NUMERIC "1"
// Retrieval info: PRIVATE: INTENDED_DEVICE_FAMILY STRING "MAX 10"
// Retrieval info: PRIVATE: LE_BasedFIFO NUMERIC "0"
// Retrieval info: PRIVATE: LegacyRREQ NUMERIC "1"
// Retrieval info: PRIVATE: MAX_DEPTH_BY_9 NUMERIC "0"
// Retrieval info: PRIVATE: OVERFLOW_CHECKING NUMERIC "0"
// Retrieval info: PRIVATE: Optimize NUMERIC "1"
// Retrieval info: PRIVATE: RAM_BLOCK_TYPE NUMERIC "2"
// Retrieval info: PRIVATE: SYNTH_WRAPPER_GEN_POSTFIX STRING "0"
// Retrieval info: PRIVATE: UNDERFLOW_CHECKING NUMERIC "0"
// Retrieval info: PRIVATE: UsedW NUMERIC "1"
// Retrieval info: PRIVATE: Width NUMERIC "16"
// Retrieval info: PRIVATE: dc_aclr NUMERIC "1"
// Retrieval info: PRIVATE: diff_widths NUMERIC "0"
// Retrieval info: PRIVATE: msb_usedw NUMERIC "0"
// Retrieval info: PRIVATE: output_width NUMERIC "16"
// Retrieval info: PRIVATE: rsEmpty NUMERIC "1"
// Retrieval info: PRIVATE: rsFull NUMERIC "0"
// Retrieval info: PRIVATE: rsUsedW NUMERIC "1"
// Retrieval info: PRIVATE: sc_aclr NUMERIC "0"
// Retrieval info: PRIVATE: sc_sclr NUMERIC "0"
// Retrieval info: PRIVATE: wsEmpty NUMERIC "0"
// Retrieval info: PRIVATE: wsFull NUMERIC "1"
// Retrieval info: PRIVATE: wsUsedW NUMERIC "1"
// Retrieval info: LIBRARY: altera_mf altera_mf.altera_mf_components.all
// Retrieval info: CONSTANT: INTENDED_DEVICE_FAMILY STRING "MAX 10"
// Retrieval info: CONSTANT: LPM_HINT STRING "RAM_BLOCK_TYPE=M9K"
// Retrieval info: CONSTANT: LPM_NUMWORDS NUMERIC "512"
// Retrieval info: CONSTANT: LPM_SHOWAHEAD STRING "OFF"
// Retrieval info: CONSTANT: LPM_TYPE STRING "dcfifo"
// Retrieval info: CONSTANT: LPM_WIDTH NUMERIC "16"
// Retrieval info: CONSTANT: LPM_WIDTHU NUMERIC "9"
// Retrieval info: CONSTANT: OVERFLOW_CHECKING STRING "ON"
// Retrieval info: CONSTANT: RDSYNC_DELAYPIPE NUMERIC "4"
// Retrieval info: CONSTANT: READ_ACLR_SYNCH STRING "OFF"
// Retrieval info: CONSTANT: UNDERFLOW_CHECKING STRING "ON"
// Retrieval info: CONSTANT: USE_EAB STRING "ON"
// Retrieval info: CONSTANT: WRITE_ACLR_SYNCH STRING "OFF"
// Retrieval info: CONSTANT: WRSYNC_DELAYPIPE NUMERIC "4"
// Retrieval info: USED_PORT: aclr 0 0 0 0 INPUT GND "aclr"
// Retrieval info: USED_PORT: data 0 0 16 0 INPUT NODEFVAL "data[15..0]"
// Retrieval info: USED_PORT: q 0 0 16 0 OUTPUT NODEFVAL "q[15..0]"
// Retrieval info: USED_PORT: rdclk 0 0 0 0 INPUT NODEFVAL "rdclk"
// Retrieval info: USED_PORT: rdempty 0 0 0 0 OUTPUT NODEFVAL "rdempty"
// Retrieval info: USED_PORT: rdreq 0 0 0 0 INPUT NODEFVAL "rdreq"
// Retrieval info: USED_PORT: rdusedw 0 0 9 0 OUTPUT NODEFVAL "rdusedw[8..0]"
// Retrieval info: USED_PORT: wrclk 0 0 0 0 INPUT NODEFVAL "wrclk"
// Retrieval info: USED_PORT: wrfull 0 0 0 0 OUTPUT NODEFVAL "wrfull"
// Retrieval info: USED_PORT: wrreq 0 0 0 0 INPUT NODEFVAL "wrreq"
// Retrieval info: USED_PORT: wrusedw 0 0 9 0 OUTPUT NODEFVAL "wrusedw[8..0]"
// Retrieval info: CONNECT: @aclr 0 0 0 0 aclr 0 0 0 0
// Retrieval info: CONNECT: @data 0 0 16 0 data 0 0 16 0
// Retrieval info: CONNECT: @rdclk 0 0 0 0 rdclk 0 0 0 0
// Retrieval info: CONNECT: @rdreq 0 0 0 0 rdreq 0 0 0 0
// Retrieval info: CONNECT: @wrclk 0 0 0 0 wrclk 0 0 0 0
// Retrieval info: CONNECT: @wrreq 0 0 0 0 wrreq 0 0 0 0
// Retrieval info: CONNECT: q 0 0 16 0 @q 0 0 16 0
// Retrieval info: CONNECT: rdempty 0 0 0 0 @rdempty 0 0 0 0
// Retrieval info: CONNECT: rdusedw 0 0 9 0 @rdusedw 0 0 9 0
// Retrieval info: CONNECT: wrfull 0 0 0 0 @wrfull 0 0 0 0
// Retrieval info: CONNECT: wrusedw 0 0 9 0 @wrusedw 0 0 9 0
// Retrieval info: GEN_FILE: TYPE_NORMAL Sdram_RD_FIFO.v TRUE
// Retrieval info: GEN_FILE: TYPE_NORMAL Sdram_RD_FIFO.inc FALSE
// Retrieval info: GEN_FILE: TYPE_NORMAL Sdram_RD_FIFO.cmp FALSE
// Retrieval info: GEN_FILE: TYPE_NORMAL Sdram_RD_FIFO.bsf FALSE
// Retrieval info: GEN_FILE: TYPE_NORMAL Sdram_RD_FIFO_inst.v FALSE
// Retrieval info: GEN_FILE: TYPE_NORMAL Sdram_RD_FIFO_bb.v FALSE
// Retrieval info: GEN_FILE: TYPE_NORMAL Sdram_RD_FIFO_waveforms.html TRUE
// Retrieval info: GEN_FILE: TYPE_NORMAL Sdram_RD_FIFO_wave*.jpg FALSE
