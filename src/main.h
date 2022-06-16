
#ifndef MAIN_H
#define MAIN_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <irq.h>
#include <libbase/uart.h>
#include <libbase/console.h>
#include <generated/csr.h>

#include <generated/mem.h>

typedef struct  {
    uint16_t trigger;
    uint16_t leds;
    uint16_t status;
} SPERIPH_TypeDef;

#define SPERIPH_DRIVER      ((SPERIPH_TypeDef *)        CSR_SPERIPH_BASE)

#endif
