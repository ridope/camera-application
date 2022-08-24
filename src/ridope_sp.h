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
uint8_t ridope_histogram(const uint8_t *img_in, size_t img_size, float *hist_out, uint16_t hist_max);
uint8_t ridope_gaussian_kernel(double *kernel_out, size_t kernel_size, float sigma);
uint8_t ridope_sobel_kernel(double *Gx_out, double *Gy_out , size_t kernel_size);
uint8_t ridope_conv(const uint8_t *img_in, uint8_t *img_out, size_t height, size_t width, double *kernel_in, size_t kernel_size);
uint8_t ridope_gaussian_filter(const uint8_t *img_in, uint8_t *img_out, size_t height, size_t width, size_t kernel_size, float sigma);
uint8_t ridope_sobel_filter(const uint8_t *img_in, uint8_t *img_x_out, uint8_t *img_y_out, size_t height, size_t width, size_t kernel_size);


#endif /* RIDOPE_SP_H_ */
