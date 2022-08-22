/*
 * ridope_sp.c
 *
 *  Created on: 22 août 2022
 *      Author: lucas
 */
#include "ridope_sp.h"

uint8_t ridope_histogram(const uint8_t *img_in, size_t img_size, float *hist_out, uint16_t hist_max)
{
	/* Checking input pointers */
	if(img_in == NULL)
	{
		return 1;
	}

	if(hist_out == NULL)
	{
		return 2;
	}

	for (int i = 0; i <= hist_max; i++)
	{
		hist_out[i] = 0;
	}


	for(int i = 0; i < img_size; i++)
	{
		uint8_t value = img_in[i];
		hist_out[value] += 1;
	}

	for(int i = 0; i <= hist_max; i++)
	{
		hist_out[i] = hist_out[i]/img_size;
	}


	return 0;
}

uint8_t ridope_otsu(const uint8_t *img_in, uint8_t *img_out, size_t height, size_t width)
{
	/* Checking input pointers */
	if(img_in == NULL)
	{
		return 1;
	}

	if(img_out == NULL)
	{
		return 2;
	}

	/* Variable initialization */
	int N = height*width;
	uint16_t max_intensity = 255;
	double w0, w1, u0, u1, max_var, class_var = 0;
	uint16_t threshold;
	float histogram[max_intensity+1];
	float cum_sum[max_intensity+1];
	float mean[max_intensity+1];

	/* Image histogram */
	ridope_histogram(img_in, N, &histogram[0], max_intensity);

	cum_sum[0] = histogram[0];
	mean[0] = 0;

	for(int i = 1; i <= max_intensity; i++)
	{
		cum_sum[i] = cum_sum[i-1] + histogram[i];
		mean[i] = mean[i-1] + i*histogram[i];
	}

	for(int i = 0; i <= max_intensity; i++)
	{
		w0 = cum_sum[i];
		w1 = 1 - cum_sum[i];

		u0 = mean[i]/cum_sum[i];
		u1 = (mean[max_intensity] - mean[i])/(1 - cum_sum[i]);

		if(cum_sum[i] != 0.0 && cum_sum[i] != 1.0)
		{
			class_var = ((mean[max_intensity]*w0 - mean[i])*(mean[max_intensity]*w0 - mean[i]))/(w0*w1);
		}
		else
		{
			class_var = 0;
		}


		if(class_var > max_var)
		{
			max_var = class_var;
			threshold = i;
		}
	}

	/* Applying Threshold */
	for(int i = 0; i < N; i++)
	{
		if (img_in[i] > threshold)
		{
			img_out[i] = 255;
		}
		else
		{
			img_out[i] = 0;
		}
	}

	return 0;
}
