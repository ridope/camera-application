
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
    uint32_t trigger;
    uint32_t reset;
    uint16_t status;
} SPERIPH_TypeDef;

#define SPERIPH_DRIVER      ((SPERIPH_TypeDef *)        CSR_CAMERA_BASE)

#endif
