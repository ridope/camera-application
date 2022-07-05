
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

typedef struct {
    uint16_t data;
} COUNTER_TypeDef;

typedef struct {
    uint16_t row_size;
    uint16_t col_size;
    uint16_t row_start;
    uint16_t col_start;
} D5M_CONTROL_TypeDef;

#define SPERIPH_DRIVER      ((SPERIPH_TypeDef *)        CSR_CAMERA_BASE)
#define COUNTER_DRIVER      ((COUNTER_TypeDef *)        LOGIC_MEMORY_BASE)

#endif
