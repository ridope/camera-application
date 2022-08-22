/*
 * ridope_sp.h
 *
 *  Created on: 22 août 2022
 *      Author: lucas
 */

#ifndef RIDOPE_SP_H_
#define RIDOPE_SP_H_

#include "stdint.h"
#include "stdio.h"

uint8_t ridope_otsu(const uint8_t *img_in, uint8_t *img_out, size_t height, size_t width);

#endif /* RIDOPE_SP_H_ */
