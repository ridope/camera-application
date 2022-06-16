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
	puts("set-pins           - Turn on a led");
	puts("reset-pins         - Turn off a led");
}

static void set_pin(void){
	char *str;
	char *char_pin;
	uint8_t pin = 0;

	printf("\e[92;1mSelect the pin [0-1]\e[0m> ");
	do 
	{
		str = readstr();
	}while(str == NULL);

	char_pin = get_token(&str);

	if(strcmp(char_pin, "0") == 0)
	{
		pin = 0;
	}else if(strcmp(char_pin, "1") == 0)
	{
		pin = 1;
	}

	uint16_t actual = SPERIPH_DRIVER->leds;

	SPERIPH_DRIVER->leds = actual | 1 << pin;

	printf("written: %d \n", SPERIPH_DRIVER->status);
}

static void reset_pin(void)
{
	char *str;
	char *char_pin;
	uint8_t pin = 0;

	printf("\e[92;1mSelect the pin [0-1]\e[0m> ");
	do 
	{
		str = readstr();
	}while(str == NULL);

	char_pin = get_token(&str);

	if(strcmp(char_pin, "0") == 0)
	{
		pin = 0;
	}else if(strcmp(char_pin, "1") == 0)
	{
		pin = 1;
	}

	uint16_t actual = SPERIPH_DRIVER->leds;

	SPERIPH_DRIVER->leds = actual & ~(1 << pin);

	printf("written: %d \n", SPERIPH_DRIVER->status);
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
	else if(strcmp(token, "set-pins") == 0)
		set_pin();
	else if(strcmp(token, "reset-pins") == 0)
		reset_pin();


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
