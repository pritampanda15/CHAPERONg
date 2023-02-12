
# CHAP_kernel_density_estimation.py -- A python script to estimate probability
#   density function using the kernel density estimator with the Gaussian kernel
# Part of the CHAPERONg suite of scripts
# Input parameters are generated by other scripts in CHAPERONg and are read
#   by this script
# CHAPERONg -- An automation program for GROMACS md simulation
# Author -- Abeeb A. Yekeen
# Contact -- abeeb.yekeen@hotmail.com
# Date: 2023.01.16


import math
import sys
import time
missingLib = []
try:
	import matplotlib
except ModuleNotFoundError:
	print("The matplotlib library has not been installed!\n")
	missingLib.append("matplotlib")
else:
	# Configure the non-interactive backend
	matplotlib.use('AGG')
	import matplotlib.pyplot as plt
try:
	import numpy as np
except ModuleNotFoundError:
	print(" The numpy library has not been installed!\n")
	missingLib.append("numpy")
try:
	import pandas as pd
except ModuleNotFoundError:
	print(" The pandas library has not been installed!\n")
	missingLib.append("pandas")
try:
	import scipy.stats as st
except ModuleNotFoundError:
	print(" The scipy library has not been installed!\n")
	missingLib.append("scipy")

if len(missingLib) >= 1 :
	print('\n\n#================================= CHAPERONg =================================#\n')
	print(" One or more required libraries have not been installed\n")
	if len(missingLib) == 1 :
		print(" Missing library:\n")
	elif len(missingLib) > 1 :
		print(" Missing libraries:\n")
	for lib in missingLib:
		print(f"  {lib}\n")
		print(" See https://www.abeebyekeen.com/chaperong-online-documentation/")
	sys.exit(0)
			

# lineNo=0
# Read in the data for PDF estimation
print (" Reading in parameters for density estimation\n")
with open("CHAP_kde_dataset_list.dat") as in_par:
	alldatasets = in_par.readlines()
	for lineNo, line in enumerate(alldatasets):
		if int(lineNo) == 0:
			dataName_raw = str(line).rstrip("\n").split(" ")
			dataName = str(dataName_raw[2])
			continue
		if int(lineNo) > 0:
			# input_data_raw = str(line).rstrip("\n")
			input_data= str(line).rstrip("\n")
			
			data_in = []
			with open(f"{input_data}_Data.dat") as alldata:
				alldata_lines = alldata.readlines()
				for line in alldata_lines:
					data_point = str(line).split("\n")
					data_in.append(float(data_point[0]))

			# Create a new figure
			plt.figure()
			# Determine the number of bins automatically
			print (f" Estimating the optimal number of histogram bins for {input_data}\n")
			time.sleep(2)
			# Determine the number of bins using the Freedman-Diaconis (1981) method
			dist = pd.Series(data_in)
			data_max, data_min = dist.max(), dist.min()
			data_range = data_max - data_min
			qt1 = dist.quantile(0.25)
			qt3 = dist.quantile(0.75)
			iqr = qt3 - qt1
			bin_width = (2 * iqr) / (len(dist) ** (1 / 3))
			bin_count = int(np.ceil((data_range) / bin_width))
			print(f'  Number of bins deduced using the Freedman-Diaconis (1981) rule')
			time.sleep(2)
			print(f'\n    bin_count = {bin_count}')

			if int(lineNo) == 1 :
				with open("CHAP_kde_Par.in", "w") as in_par:
					in_par.write(f"{input_data}\n")
					in_par.write(f'bin_count,{bin_count}\n')
			elif int(lineNo) > 1 :
				with open("CHAP_kde_Par.in", "a") as in_par:
					in_par.write(f"{input_data}\n")
					in_par.write(f'bin_count,{bin_count}\n')				

			# Scott (1979) method
			stdev = dist.std()
			bin_width_scott = (3.5 * stdev) / (len(dist) ** (1 / 3))
			bin_count_scott = int(np.ceil((data_range) / bin_width_scott))
			time.sleep(1)

			# Determine the number of bins using the sqrt method
			num_of_bins_sqrt = int(np.ceil(math.sqrt(len(dist))))
			num_of_bins_rice = int(np.ceil( 2 * (len(dist) ** (1 / 3))))

			if int(lineNo) == 1:
				with open("kde_bins_estimated_summary.dat", "w") as bin_summary:
					bin_summary.write(f"=> {input_data}\n"
									   "----------------------------------\n"					
									   "Binning Method\t  | Number of bins\n"
									   "------------------+---------------\n"
									  f"Freedman-Diaconis | {bin_count}\t(*)\n"
									  f"Square root\t\t  | {num_of_bins_sqrt}\n"
									  f"Rice\t\t\t  | {num_of_bins_rice}\n"
									  f"Scott\t\t\t  | {bin_count_scott}\n\n\n")
			elif int(lineNo) > 1:
				with open("kde_bins_estimated_summary.dat", "a") as bin_summary:
					bin_summary.write(f"=> {input_data}\n"
									   "----------------------------------\n"					
									   "Binning Method\t  | Number of bins\n"
									   "------------------+---------------\n"
									  f"Freedman-Diaconis | {bin_count}\t(*)\n"
									  f"Square root\t\t  | {num_of_bins_sqrt}\n"
									  f"Rice\t\t\t  | {num_of_bins_rice}\n"
									  f"Scott\t\t\t  | {bin_count_scott}\n\n\n")

			print("\n Optimal binning parameters have been estimated."
				  "\n These parameters have been written to file (CHAP_kde_Par.in)."
				  "\n\n  Do you want to proceed?\n   (1) Yes\n   (2) No\n")

			prmpt = "  Enter a response here (1 or 2): "
			response = int(input(prmpt))

			while response != 1 and response != 2:
				print("\n ENTRY REJECTED!\
					\n **Please enter the appropriate option (1 or 2)\n")
				response = int(input(prmpt))

			if response == 2:
				sys.exit(0)
			elif response == 1:
				print ("\n Updating input parameters for density estimation\n")
				time.sleep(2)
				with open("CHAP_kde_Par.in" , 'r') as in_par:
					for parameter in in_par.readlines():
						if "bin_count" in parameter:
							para_data = parameter.rstrip('\n').split(",")
							bin_custom = int(para_data[1])
				bin_set = bin_custom

			print (f" Generating and plotting the histogram of the {input_data}\n")
			time.sleep(2)

			# Generate and plot the histogram of the data
			plt.hist(data_in, bins=bin_set, label=input_data, color='#4CE418', alpha=0.9)
			plt.xlabel(input_data + r' ($\AA$)')
			plt.ylabel('Count')
			plt.title("Histogram of the "+input_data)
			figname = input_data + "_histogram.png"
			plt.savefig(figname, dpi=600)

			# Create a new figure for the KDE
			plt.figure()

			# Assign histogram to a value
			a = plt.hist(data_in, density=True, bins=bin_set,
						label=input_data, color='#4CE418', alpha=0.9)

			# The first elements are the ys, the second are the xs.
			ys = a[0]; xs = a[1]

			# The x-axis values are boundaries, starting with the lower bound of the first 
			# and ending with the upper bound of the last.
			# So, length of the x-axis > length of the y-axis by 1.

			# Get the upper bounds and write out the histogram
			print (f" Writing out the histogram data of the {input_data}\n")
			time.sleep(2)
			out_hist = input_data+"_histogram.xvg"
			if "RMSD" in input_data: histLabel = r'RMSD (\cE\C)'
			elif "Rg" in input_data: histLabel = r'Radius of gyration (\cE\C)'
			elif "Hbond" in input_data: histLabel = "Number of hydrogen bonds"
			elif "SASA" in input_data: histLabel = r'SASA (nm\S2\N)'

			with open (out_hist, 'w') as outfile:
				outfile.write('# This file contains the histogram values of '
							f'the {input_data} data calculated by CHAPERONg'
							 '\n# from the output of GROMACS'
							 '\n#\n'
							f'@    title "Histogram of {input_data}"\n'
							f'@    xaxis  label "{histLabel}"\n'
							 '@    yaxis  label "Count"\n'
							 '@TYPE bar\n'
							f'@ s0 legend "{dataName}_{input_data}"\n')
			pd.DataFrame({'x_upper':a[1][1:], 'y': a[0]}).to_csv(out_hist,
							header=False, index=False, sep="\t", mode='a')

			print (f" Estimating the probability density function for {input_data}\n")
			time.sleep(2)
			kde_xs = np.linspace(min(data_in), max(data_in), 300)
			kde = st.gaussian_kde(data_in)
			kde_ys = kde.pdf(kde_xs)
			out_kde = input_data+"_KDEdata.xvg"
			with open (out_kde, 'w') as outdkefile:
				outdkefile.write('# This file contains the KDE-estimated PDF values of '
							f'the {input_data} data calculated by CHAPERONg'
							 '\n# from the output of GROMACS'
							 '\n#\n'
							 '@    title "KDE-estimated Probability Density'
							f' Function of {input_data}"\n'
							f'@    xaxis  label "{histLabel}"\n'
							 '@    yaxis  label "Density"\n'
							 '@TYPE xy\n'
							f'@ s0 legend "{dataName}_{input_data}"\n')
			pd.DataFrame({'x':kde_xs, 'y': kde_ys}).to_csv(out_kde,
							header=False, index=False, sep="\t", mode='a')
			kdeLabel = input_data + "_PDF"
			plt.plot(kde_xs, kde.pdf(kde_xs), label=kdeLabel, color='r')
			plt.legend()
			plt.ylabel("Density")
			plt.xlabel(input_data + r' ($\AA$)')
			plt.title(f'Kernel Density Estimation Plot of the {input_data}')
			figname = input_data + "_KDE_plot.png"
			plt.savefig(figname, dpi=600)
			print (f" Estimate the probability density function for {input_data}...DONE\n"
				    "#=============================================================================#\n")
			
