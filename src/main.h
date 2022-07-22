
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
#include "comm_ridope.h"

typedef struct  {
    uint32_t trigger;
    uint32_t reset;
    uint16_t status;
} SPERIPH_TypeDef;

#define IMG_WIDTH 32
#define IMG_HEIGTH 32

typedef struct {
    uint8_t data[IMG_WIDTH*IMG_HEIGTH];
} Img_TypeDef;

typedef struct {
    uint16_t row_size;
    uint16_t col_size;
    uint16_t row_start;
    uint16_t col_start;
} D5M_CONTROL_TypeDef;

#define SPERIPH_DRIVER      ((SPERIPH_TypeDef *)        CSR_CAMERA_BASE)
#define IMG_DRIVER      ((Img_TypeDef *)        LOGIC_MEMORY_BASE)

#endif
