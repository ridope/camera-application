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

static void trigger_camera(void){
	camera_input_trigger_write(1);
}

static void reset_camera(void)
{
	camera_input_trigger_write(0);
}

static void set_size(void){
	char *str;
	char *row_str;
	char *col_str;
	D5M_CONTROL_TypeDef camera;
	
	uint64_t *reg = (uint64_t *) &camera;
	*reg = camera_control_read();

	printf("\e[94;1mInsert the row size\e[0m> ");
	do 
	{
		str = readstr();
	}while(str == NULL);

	row_str = get_token(&str);

	camera.row_size = atoi(row_str);
	
	printf("\e[94;1mInsert the column size\e[0m> ");
	do 
	{
		str = readstr();
	}while(str == NULL);

	col_str = get_token(&str);

	camera.col_size = atoi(col_str);
	
	camera_control_write(*reg);
	printf("Row size: %d\n", camera.row_size);
	printf("Col size: %d\n", camera.col_size);
	printf("Row start: %d\n", camera.row_start);
	printf("Col start: %d\n", camera.col_start);
	//camera_test_update_write(0);
}

static void set_start(void){
	char *str;
	char *row_str;
	char *col_str;

	D5M_CONTROL_TypeDef camera;
	
	uint64_t *reg = (uint64_t *) &camera;
	*reg = camera_control_read();

	printf("\e[94;1mInsert the row start\e[0m> ");
	do 
	{
		str = readstr();
	}while(str == NULL);

	row_str = get_token(&str);

	camera.row_start = atoi(row_str);
	
	printf("\e[94;1mInsert the column start\e[0m> ");
	do 
	{
		str = readstr();
	}while(str == NULL);

	col_str = get_token(&str);

	camera.col_start = atoi(col_str);

	camera_control_write(*reg);
	printf("Row size: %d\n", camera.row_size);
	printf("Col size: %d\n", camera.col_size);
	printf("Row start: %d\n", camera.row_start);
	printf("Col start: %d\n", camera.col_start);

}

static void set_length(void){
	char *str;
	char *row_str;
	char *col_str;

	printf("\e[94;1mInsert the Read length \e[0m> ");
	do 
	{
		str = readstr();
	}while(str == NULL);

	row_str = get_token(&str);

	int read_l = atoi(row_str);
	
	printf("\e[94;1mInsert the Write length\e[0m> ");
	do 
	{
		str = readstr();
	}while(str == NULL);

	col_str = get_token(&str);

	int write_l = atoi(col_str);

	camera_sram_rd_l_write(read_l);
	camera_sram_wr_l_write(write_l);
}


static void set_vga(void){
	char *str;
	char *row_str;
	char *col_str;

	printf("\e[94;1mInsert the VGA Width \e[0m> ");
	do 
	{
		str = readstr();
	}while(str == NULL);

	row_str = get_token(&str);

	int vga_w = atoi(row_str);
	
	printf("\e[94;1mInsert the Write length\e[0m> ");
	do 
	{
		str = readstr();
	}while(str == NULL);

	col_str = get_token(&str);

	int vga_h = atoi(col_str);

	camera_vga_w_write(vga_w);
	camera_vga_h_write(vga_h);
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

static void set_test(void){
	char *str;
	char *test_str;

	printf("\e[94;1mInsert the test pattern value\e[0m> ");
	do 
	{
		str = readstr();
	}while(str == NULL);

	test_str = get_token(&str);
	
	camera_test_pattern_write(atoi(test_str));
	//camera_test_update_write(0);
}

static void get_img(void){
	printf("Got it!\n");
	camera_input_trigger_write(1);

	
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

	/* Exposure : 1000 */
	//camera_input_exposure_write(3000);
	
	/* Camera output size: 32x32 pixels */
	uint64_t *reg = (uint64_t *) &camera;
	*reg = camera_control_read();

	camera.row_size = 32;
	camera.col_size = 32;

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
/* Console service / Main                                                */
/*-----------------------------------------------------------------------*/

static void console_service(void)
{
	char *str;
	char *token;

	str = readstr();
	if(str == NULL) return;
	token = get_token(&str);
	if(strcmp(token, "help") == 0)
		help();
	else if(strcmp(token, "reboot") == 0)
		reboot_cmd();
	else if(strcmp(token, "trigger") == 0)
		trigger_camera();
	else if(strcmp(token, "reset") == 0)
		reset_camera();
	else if(strcmp(token, "expo") == 0)
		set_exposure(2500);
	else if(strcmp(token, "test") == 0)
		set_test();
	else if(strcmp(token, "size") == 0)
		set_size();
	else if(strcmp(token, "start") == 0)
		set_start();
	else if(strcmp(token, "get") == 0)
		get_img();
	else if(strcmp(token, "len") == 0)
		set_length();
	else if(strcmp(token, "vga") == 0)
		set_vga();

	prompt();
}


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

	while(1) {
		comm_ridope_receive_cmd(&rx_msg);


		if(rx_msg.msg_data.cmd == CAMERA_TRIG)
		{
			get_img();
		}else if(rx_msg.msg_data.cmd == CAMERA_EXPO)
		{
			set_exposure(crealf(rx_msg.msg_data.data));
		}
	}

	return 0;
}
