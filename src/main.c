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
	puts("test		        - Sets the test control resgister");
}

static void trigger_camera(void){
	camera_input_trigger_write(1);
}

static void reset_camera(void)
{
	camera_input_trigger_write(0);
}

static void set_exposure(void){
	char *str;
	char *exposure_str;

	printf("\e[94;1mInsert the exposure\e[0m> ");
	do 
	{
		str = readstr();
	}while(str == NULL);

	exposure_str = get_token(&str);
	
	camera_input_exposure_write(atoi(exposure_str));
}

static void set_test(void){
	char *str;
	char *test_str;

	printf("\e[94;1mInsert the test register value\e[0m> ");
	do 
	{
		str = readstr();
	}while(str == NULL);

	test_str = get_token(&str);
	
	camera_input_exposure_write(atoi(test_str));
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
		set_exposure();
	else if(strcmp(token, "test") == 0)
		set_test();


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

	while(1) {
		console_service();
	}

	return 0;
}
