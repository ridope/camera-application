/*
 * ridope_sp.c
 *
 *  Created on: 22 août 2022
 *      Author: lucas
 */
#include "ridope_sp.h"

/**
 * @brief Generates the normalized histogram of the image
 * 
 * @param img_in 	Pointer to the input image
 * @param img_size  Size of the image
 * @param hist_out  Pointer to the output histrogram
 * @param hist_max 	Max level of the histogram
 * @return uint8_t  Returns 0 if success
 */
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

	/* Building histogram */
	for(int i = 0; i < img_size; i++)
	{
		uint8_t value = img_in[i];
		hist_out[value] += 1;
	}

	/* Normalizing the histogram */
	for(int i = 0; i <= hist_max; i++)
	{
		hist_out[i] = hist_out[i]/img_size;
	}


	return 0;
}

/**
 * @brief Otsu's method
 * 
 * @param img_in 	Pointer to the input image
 * @param img_out 	Pointer to the output image
 * @param height 	Height of the input image
 * @param width 	Width of the input image	
 * @return uint8_t  Return 0 if success
 */
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

	/* Auxiliary parameters */
	cum_sum[0] = histogram[0];
	mean[0] = 0;

	for(int i = 1; i <= max_intensity; i++)
	{
		cum_sum[i] = cum_sum[i-1] + histogram[i];
		mean[i] = mean[i-1] + i*histogram[i];
	}

	/* Otsu's threshold method */
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

/**
 * @brief Generates a gaussian kernel
 * 
 * @param kernel_out 	Pointer to store the kernel generated
 * @param kernel_size 	Size of the kernel
 * @param sigma 		The standard deviation of the kernel
 * @return uint8_t 		Returns 0 if success
 */
uint8_t ridope_gaussian_kernel(double *kernel_out, size_t kernel_size, float sigma)
{
	if(kernel_out == NULL)
	{
		return 1;
	}
	double sum = 0;

	// Middle of the kernel
	double offset = (kernel_size - 1) / 2.0;

	 for (int i = 0; i < kernel_size; i++)
	 {
		for (int j = 0; j < kernel_size; j++)
		{
			double x = i - offset;
			double y = j - offset;
			kernel_out[kernel_size * i + j] = exp(-(x*x + y*y) / (2 * sigma* sigma ));
			sum += kernel_out[kernel_size * i + j];
		}
	}

	 for (int i = 0; i < kernel_size*kernel_size; i++)
	 {
		 kernel_out[i] /= sum;
	 }

	 for (int i = 0; i < kernel_size; i++)
	 {
		 for (int j = 0; j < kernel_size; j++)
		 {
			 printf("%f ", kernel_out[kernel_size * i + j]);
		 }
		 printf("\n");
	 }

	 return 0;
}

/**
 * @brief Generates a Sobel kernel
 * 
 * @param kernel_out 	Pointer to store the kernel generated
 * @param kernel_size 	Size of the kernel
 * @return uint8_t 		Returns 0 if success
 */
uint8_t ridope_sobel_kernel(double *Gx_out, double *Gy_out , size_t kernel_size)
{
	/* Checking input pointers */
	if(Gx_out == NULL)
	{
		return 1;
	}

	if(Gy_out == NULL)
	{
		return 2;
	}

	// Middle of the kernel
	uint8_t offset = (kernel_size - 1) / 2;

	for (int i = 0; i < kernel_size; i++)
	{
		for (int j = 0; j < kernel_size; j++)
		{
			double x = i - offset;
			double y = j - offset;

			if (x == 0 && y == 0)
			{
				Gy_out[kernel_size * i + j] = 0;
				Gx_out[kernel_size * i + j] = 0;
			}
			else
			{
				Gy_out[kernel_size * i + j] = x / (2*(x*x + y*y));
				Gx_out[kernel_size * i + j] = y / (2*(x*x + y*y));
			}
		}
	}

	printf("##### Gx ######\n");
	for (int i = 0; i < kernel_size; i++)
	{
	 for (int j = 0; j < kernel_size; j++)
	 {
		 printf("%f ", Gx_out[kernel_size * i + j]);
	 }
	 printf("\n");
	}

	printf("##### Gy ######\n");
	for (int i = 0; i < kernel_size; i++)
	 {
		 for (int j = 0; j < kernel_size; j++)
		 {
			 printf("%f ", Gy_out[kernel_size * i + j]);
		 }
		 printf("\n");
	 }

	return 0;
}

/**
 * @brief Makes a convolution of the filter with an image
 * 
 * @param img_in 		Pointer to the input image
 * @param img_out 		Pointer to the output image
 * @param height 		Height of the input image
 * @param width 		Width of the input image
 * @param kernel_in 	Pointer to the filter
 * @param kernel_size 	Filter size
 * @return uint8_t 		Returns 0 if success
 */
uint8_t ridope_conv(const uint8_t *img_in, uint8_t *img_out, size_t height, size_t width, double *kernel_in, size_t kernel_size)
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

	if(kernel_in == NULL)
	{
		return 3;
	}

	// Middle of the kernel
	uint8_t offset = kernel_size / 2;
	double pixel;
	double pixel_result;
	double pixel_mask;

	for(int x = 0; x < height; x++)
	{
		for(int y = 0; y < width; y++)
		{
			pixel_result = 0;

			for(int a = 0; a < kernel_size; a++)
			{
				for(int b = 0; b < kernel_size; b++)
				{
					int x_n = x + a - offset;
					int y_n = y + b - offset;

					if (x_n < 0 || y_n < 0 || x_n == width || y_n == height)
					{
						int x_near = x_n;
						int y_near = y_n;

						if(y_n < 0)
						{
							y_near = abs(y_n) + y_n;
						}

						if(x_n < 0)
						{
							x_near = abs(x_n) + x_n;
						}

						if(x_n == width)
						{
							x_near = width - 1;
						}

						if(y_n == height)
						{
							y_near = height - 1;
						}
						pixel_mask = kernel_in[kernel_size * a + b];
						pixel = img_in[width * x_near + y_near]*pixel_mask;
					}
					else
					{
						pixel_mask = kernel_in[kernel_size * a + b];
						pixel = img_in[width * x_n + y_n]*pixel_mask;
					}
					pixel_result += pixel;
				}
			}
			if (pixel_result < 0){
				pixel_result = pixel_result * -1;
			}
			img_out[width * x + y] = pixel_result;

		}
	}

	return 0;

}

/**
 * @brief Applies the Gaussian filter in a image
 * 
 * @param img_in 		Pointer to the input image
 * @param img_out 		Pointer to the output image
 * @param height 		Height of the input image
 * @param width 		Width of the input image 
 * @param kernel_size 	Filter size
 * @param sigma 		The standard deviation of the kernel
 * @return uint8_t 		Returns 0 if success
 */
uint8_t ridope_gaussian_filter(const uint8_t *img_in, uint8_t *img_out, size_t height, size_t width, size_t kernel_size, float sigma)
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

	double *kernel = (double *)malloc(kernel_size*kernel_size*sizeof(double));

	/* Checking memory allocation */
	if(kernel == NULL)
	{
		return 3;
	}


	ridope_gaussian_kernel(kernel, kernel_size, sigma);

	ridope_conv(img_in, img_out, height, width, kernel, kernel_size);

	free(kernel);

	return 0;
}

/**
 * @brief Applies the Sobel filter in a image
 * 
 * @param img_in 		Pointer to the input image	
 * @param img_x_out 	Pointer to the X component output image
 * @param img_y_out 	Pointer to the Y component output image
 * @param height 		Height of the input image
 * @param width 		Width of the input image 
 * @param kernel_size 	Filter size
 * @return uint8_t 		Returns 0 if success
 */
uint8_t ridope_sobel_filter(const uint8_t *img_in, uint8_t *img_x_out, uint8_t *img_y_out, size_t height, size_t width, size_t kernel_size)
{
	/* Checking input pointers */
	if(img_in == NULL)
	{
		return 1;
	}

	if(img_x_out == NULL)
	{
		return 2;
	}

	if(img_y_out == NULL)
	{
		return 3;
	}

	double *Gx = (double *)malloc(kernel_size*kernel_size*sizeof(double));
	double *Gy = (double *)malloc(kernel_size*kernel_size*sizeof(double));

	/* Checking memory allocation */
	if(Gx == NULL)
	{
		return 4;
	}

	if(Gy == NULL)
	{
		return 5;
	}

	ridope_sobel_kernel(&Gx[0],  &Gy[0], kernel_size);

	ridope_conv(img_in, img_x_out, height, width, &Gx[0], kernel_size);
	ridope_conv(img_in, img_y_out, height, width, &Gy[0], kernel_size);

	free(Gx);
	free(Gy);
	return 0;
}

/**
 * @brief Retrieves the magnitude and angle from the Sobel filter components 
 * 
 * @param img_x_in 		Pointer to the Sobel X component input image
 * @param img_y_in 		Pointer to the Sobel Y component input image
 * @param mag_out 		Pointer to the magnitude output matrix
 * @param ang_out 		Pointer to the angle output matrix
 * @param height 		Height of the input image
 * @param width 		Width of the input image  
 * @return uint8_t 		Returns 0 if success
 */
uint8_t ridope_get_mag_ang(const uint8_t *img_x_in, const uint8_t *img_y_in, uint8_t *mag_out, uint8_t *ang_out, size_t height, size_t width)
{
	/* Checking input pointers */
	if(img_x_in == NULL)
	{
		return 1;
	}

	if(img_y_in == NULL)
	{
		return 2;
	}

	if(mag_out == NULL && ang_out == NULL)
	{
		return 3;
	}

	for(int x = 0; x < width; x++)
	{
		for(int y = 0; y < height; y++)
		{
			if(mag_out != NULL)
			{
				mag_out[width * x + y] = sqrt( img_x_in[width * x + y]*img_x_in[width * x + y] + img_y_in[width * x + y]*img_y_in[width * x + y]);
			}

			if(ang_out != NULL)
			{
				double ang_d = atan2(img_y_in[width * x + y], img_x_in[width * x + y]) * 180/M_PI;

				if((ang_d >= 0 &&  ang_d <= 22.5) || (ang_d > 157.5 &&  ang_d <= 180))
				{
					ang_out[width * x + y] = 0;
				}
				else if(ang_d > 22.5 &&  ang_d <= 67.5)
				{
					ang_out[width * x + y] = 45;
				}
				else if(ang_d > 67.5 &&  ang_d <= 112.5)
				{
					ang_out[width * x + y] = 90;
				}
				else if(ang_d > 112.5 &&  ang_d <= 157.5)
				{
					ang_out[width * x + y] = 135;
				}

			}
		}
	}

	return 0;
}