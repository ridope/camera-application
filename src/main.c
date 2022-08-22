#include "main.h"

/*-----------------------------------------------------------------------*/
/* Uart                                                                  */
/*-----------------------------------------------------------------------*/

static char *readstr(void)
{
	char c[2];
	static char s[64];
	static int ptr = 0;

	if(readchar_nonblock()) {
		c[0] = getchar();
		c[1] = 0;
		switch(c[0]) {
			case 0x7f:
			case 0x08:
				if(ptr > 0) {
					ptr--;
					fputs("\x08 \x08", stdout);
				}
				break;
			case 0x07:
				break;
			case '\r':
			case '\n':
				s[ptr] = 0x00;
				fputs("\n", stdout);
				ptr = 0;
				return s;
			default:
				if(ptr >= (sizeof(s) - 1))
					break;
				fputs(c, stdout);
				s[ptr] = c[0];
				ptr++;
				break;
		}
	}

	return NULL;
}

static char *get_token(char **str)
{
	char *c, *d;

	c = (char *)strchr(*str, ' ');
	if(c == NULL) {
		d = *str;
		*str = *str+strlen(*str);
		return d;
	}
	*c = 0;
	d = *str;
	*str = c+1;
	return d;
}

static void prompt(void)
{
	printf("\e[92;1mlitex-demo-app\e[0m> ");
}

/*-----------------------------------------------------------------------*/
/* Help                                                                  */
/*-----------------------------------------------------------------------*/

static void help(void)
{
	puts("\nLiteX minimal demo app built "__DATE__" "__TIME__"\n");
	puts("Available commands:");
	puts("help               - Show this command");
	puts("reboot             - Reboot CPU");
	puts("trigger           - Takes a picture");
	puts("reset		        - Reset the camera");
	puts("expo		        - Sets the camera exposure");
	puts("size				- Sets the output image size");
	puts("start				- Sets the readout image start");
	puts("len				- Sets the SDRAM RD/WR length");
	puts("vga				- Sets the VGA output");
	puts("test		        - Sets the test pattern resgister");
	puts("get				- Gets the image from logic");
}

static void reset_camera(void)
{
	camera_input_trigger_write(0);
}
static void set_exposure(uint32_t expo){
	// char *str;
	// char *exposure_str;

	// printf("\e[94;1mInsert the exposure\e[0m> ");
	// do 
	// {
	// 	str = readstr();
	// }while(str == NULL);

	// exposure_str = get_token(&str);
	
	//camera_input_exposure_write(atoi(exposure_str));
	camera_input_exposure_write(expo);
	//camera_test_update_write(0);
}

uint32_t get_avg(uint8_t *img, uint16_t img_width, uint16_t imb_height)
{
	uint32_t sum = 0;
	uint32_t max = 0;
	int i;

	for(i = 0; i < img_width*imb_height; i++)
	{
		sum += img[i];
	}

	return sum/i;
}

void get_next_expo(uint32_t *expo, uint32_t avg)
{
	uint32_t STEP_HIGH = 1000;
	uint32_t STEP_MID = 500;
	uint32_t STEP_LOW = 200;

	uint8_t F_TARGET = 61;

	if(avg > F_TARGET) 
	{
		if ((avg-F_TARGET) >= 64)
		{
			*expo = *expo - STEP_HIGH;
		}
		else if((avg-F_TARGET) >= 32)
		{
			*expo = *expo - STEP_MID;
		}
		else if((avg-F_TARGET) >= 1)
		{
			*expo = *expo - STEP_LOW;
		}
	}
	else{
		if ((F_TARGET-avg) >= 64)
		{
			*expo = *expo + STEP_HIGH;
		}
		else if((F_TARGET-avg) >= 32)
		{
			*expo = *expo + STEP_MID;
		}
		else if((F_TARGET-avg) >= 1)
		{
			*expo = *expo + STEP_LOW;
		}
	}
          

}

static void get_img(uint32_t *expo){
	printf("Got it!\n");
	
	uint32_t avg = get_avg(&(IMG_DRIVER->data[0]), IMG_WIDTH, IMG_HEIGTH);

	get_next_expo(expo, avg);

	set_exposure(*expo);

	COMM_RIDOPE_MSG_t msg;
	msg.msg_data.cmd = CAMERA_EXPO;
	msg.msg_data.data = *expo; 

	comm_ridope_send_cmd(&msg);

	msg.msg_data.cmd = CAMERA_AVG;
	msg.msg_data.data = avg; 
	comm_ridope_send_cmd(&msg);
	
	printf("Sending img!\n");

	comm_ridope_send_img(&(IMG_DRIVER->data[0]),TRANS_PHOTO, IMG_WIDTH, IMG_HEIGTH);
	printf("Done sending!\n");

	
}

static void init_cam(){
	D5M_CONTROL_TypeDef camera;

	/* No test pattern */
	camera_test_pattern_write(0);

	/* VGA output size: 32x32 pixels */
	camera_vga_w_write(32);
	camera_vga_h_write(32);
	
	/* Camera output size: 32x32 pixels */
	uint64_t *reg = (uint64_t *) &camera;
	*reg = camera_control_read();

	// Necessary values to produce a 32x32 image without borders.
	camera.row_size = 34;
	camera.col_size = 38; 

	camera_control_write(*reg);
}

/*-----------------------------------------------------------------------*/
/* Commands                                                              */
/*-----------------------------------------------------------------------*/

static void reboot_cmd(void)
{
	ctrl_reset_write(1);
}

/*-----------------------------------------------------------------------*/
/* Main                                             					 */
/*-----------------------------------------------------------------------*/

int main(void)
{
	#ifdef CONFIG_CPU_HAS_INTERRUPT
		irq_setmask(0);
		irq_setie(1);
	#endif
	uart_init();

	help();
	prompt();

	init_cam();

	COMM_RIDOPE_MSG_t rx_msg;

	uint32_t expo = 11264;

	while(1) {
		comm_ridope_receive_cmd(&rx_msg);

		if(rx_msg.msg_data.cmd == CAMERA_TRIG)
		{	
			get_img(&expo);
		}else if(rx_msg.msg_data.cmd == CAMERA_EXPO)
		{
			set_exposure(crealf(rx_msg.msg_data.data));
		}else if(rx_msg.msg_data.cmd == REBOOT)
		{
			reboot_cmd();
		}
	}

	return 0;
}
