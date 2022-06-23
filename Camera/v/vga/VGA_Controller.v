module	VGA_Controller(	//	Host Side
						iRed,
						iGreen,
						iBlue,
						oRequest,
						//	VGA Side
						oVGA_R,
						oVGA_G,
						oVGA_B,
						oVGA_H_SYNC,
						oVGA_V_SYNC,

						//	Control Signal
						iVGA_CLK,
						iRST_n	);


//	Host Side
input		[3:0]	iRed;
input		[3:0]	iGreen;
input		[3:0]	iBlue;
output	reg			oRequest;
//	VGA Side
output		[3:0]	oVGA_R;
output		[3:0]	oVGA_G;
output		[3:0]	oVGA_B;
output	reg			oVGA_H_SYNC;
output	reg			oVGA_V_SYNC;

//	Control Signal
input				iVGA_CLK;
input				iRST_n;

///////// ////                     
reg [18:0] ADDR ;
wire VGA_CLK_n;
wire [7:0] index;
wire [23:0] bgr_data_raw;
wire cBLANK_n,cHS,cVS,rst;
reg [18:0] H_Cont/*synthesis noprune*/;
reg [18:0] V_Cont/*synthesis noprune*/;
////
assign rst = ~iRST_n;

video_sync_generator LTM_ins (.vga_clk(iVGA_CLK),
                              .reset(rst),
                              .blank_n(cBLANK_n),
                              .HS(cHS),
                              .VS(cVS)
										);

////Addresss generator
always@(posedge iVGA_CLK,negedge iRST_n)
begin
  if (!iRST_n) begin
     ADDR<=19'd0;
	  oRequest<=0;
  end
  else if (cBLANK_n==1'b1) begin
     ADDR<=ADDR+1;
	  oRequest<=1;
  end
	  else begin
	    ADDR<=19'd0;
		 oRequest<=0;
	 end
end
										
reg [11:0] bgr_data;

parameter VIDEO_W	= 640;
parameter VIDEO_H	= 480;


always@(posedge iVGA_CLK)
begin
  if (~iRST_n)
  begin
     bgr_data<=12'h000;
  end
    else
    begin
//      if (0<ADDR && ADDR <= VIDEO_W/3)
//					bgr_data <= {8'hff, 8'h00, 8'h00}; // blue
//		else if (ADDR > VIDEO_W/3 && ADDR <= VIDEO_W*2/3)
//			bgr_data <= {8'h00,8'hff, 8'h00};  // green
//		else if(ADDR > VIDEO_W*2/3 && ADDR <=VIDEO_W)
//			bgr_data <= {8'h00, 8'h00, 8'hff}; // red
//		else bgr_data <= 24'h0000; 
		if (0<ADDR && ADDR <= VIDEO_W)
			bgr_data <= {iBlue, iGreen, iRed};
		else bgr_data <= 12'h000; 
    end
end

assign oVGA_B=bgr_data[11:8];
assign oVGA_G=bgr_data[7:4]; 
assign oVGA_R=bgr_data[3:0];
///////////////////
//////Delay the iHD, iVD,iDEN for one clock cycle;
reg mHS, mVS, mBLANK_n;
always@(posedge iVGA_CLK)
begin
  mHS<=cHS;
  mVS<=cVS;
  mBLANK_n<=cBLANK_n;
  oVGA_H_SYNC<=mHS;
  oVGA_V_SYNC<=mVS;
end


////for signaltap ii/////////////
always@(posedge iVGA_CLK,negedge iRST_n)
begin
  if (!iRST_n)
     H_Cont<=19'd0;
  else if (mHS==1'b1)
     H_Cont<=H_Cont+1;
  else
	  H_Cont<=19'd0;
end


//	V_Sync Generator, Ref. H_Sync
always@(posedge mHS,negedge iRST_n)
begin
  if (!iRST_n)
     V_Cont<=19'd0;
  else if (mVS==1'b1 && H_Cont==0)
     V_Cont<=V_Cont+1;
  else
	  V_Cont<=19'd0;
end

endmodule