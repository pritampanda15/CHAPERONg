
# CHAP_kde_single_plot.py -- A python script to estimate probability
#   density function using the kernel density estimator with the Gaussian kernel
# Part of the CHAPERONg suite of scripts
# Input parameters are generated by other scripts in CHAPERONg and are read
#   by this script
# CHAPERONg -- An automation program for GROMACS md simulation
# Author -- Abeeb A. Yekeen
# Contact -- abeeb.yekeen@hotmail.com
# Date: 2023.01.16


import math
import os
import shutil
import sys
import time

# def check_and_import_lib
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
	# if len(missingLib) == 1 : print(" Missing library:\n")
	# elif len(missingLib) > 1 : print(" Missing libraries:\n")
	# Ternary Operator
	# print(" Missing library:\n") if len(missingLib) == 1 else print(" Missing libraries:\n")
	print(" Missing library:\n" if len(missingLib) == 1 else " Missing libraries:\n")
	suggestmsg = "pip install "
	for lib in missingLib:
		print(f"  {lib}\n")
		if lib == "numpy" : lib = "numpy==1.23.4"
		suggestmsg = suggestmsg + f'{lib} '
	print(
		f' {suggestmsg}\n\n or\n\n'
		' See https://www.abeebyekeen.com/chaperong-online-documentation/'
		)
	sys.exit(0)

def make_dir_for_KDE(motherDir='Kernel_Density_Estimation'):
	if os.path.exists(motherDir):
		backup_count = 1
		backupDir=f'#{motherDir}.backup.{backup_count}'
		while os.path.exists(backupDir):
			backup_count += 1
			backupDir = f'#{motherDir}.backup.{backup_count}'			
		shutil.move(motherDir, backupDir)
	os.mkdir(motherDir)

# output_dict = {'files_to_move': [], 'files_to_copy': []}

def estimate_PDF_with_KDE():
# Read in the data for PDF estimation
	print (" Reading in parameters for density estimation\n")
	with open("CHAP_kde_dataset_list.dat") as in_par:
		alldatasets = in_par.readlines()
		for lineNo, line in enumerate(alldatasets):
			output_and_para_files = []
			if int(lineNo) == 0 and "auto mode" in line:
				global auto_mode
				auto_mode_raw = str(line).rstrip("\n").split(",")
				auto_mode = auto_mode_raw[1]	
				print(f'auto_mode is {auto_mode}')
				print(f'auto_mode is {auto_mode}')
				print(f'auto_mode is {auto_mode}')
				continue
			if int(lineNo) == 1: continue
			if int(lineNo) == 2:
				dataName_raw = str(line).rstrip("\n").split(" ")
				dataName = str(dataName_raw[2])
				continue	
			if int(lineNo) >= 3:
				# input_data_raw = str(line).rstrip("\n")
				input_data = str(line).rstrip("\n")
				
				data_in = []
				extracted_data = f"{input_data}_Data.dat"
				with open(extracted_data) as alldata:
					alldata_lines = alldata.readlines()
					for line in alldata_lines:
						data_point = str(line).rstrip("\n")
						data_in.append(float(data_point))

				# Create a new figure
				plt.figure()
				# Determine the number of bins automatically
				print (
					"#=============================================================================#\n"
					f"\n Estimating the optimal number of histogram bins for {input_data}\n"
					)
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

				def writeOut_parameters():
					in_par.write(f'{input_data}\n'
								f'bin_count,{bin_count}\n'
								"bandwidth_method,silverman\n\n\n")					

				if int(lineNo) == 1 :
					with open("CHAP_kde_Par.in", "w") as in_par:
						writeOut_parameters()

				elif int(lineNo) > 1 :
					with open("CHAP_kde_Par.in", "a") as in_par:
						writeOut_parameters()
								
				with open(f'CHAP_kde_Par_{input_data}.in', "w") as in_par:
					writeOut_parameters()				

				output_and_para_files.append(f'CHAP_kde_Par_{input_data}.in')

				# Scott (1979) method
				stdev = dist.std()
				bin_width_scott = (3.5 * stdev) / (len(dist) ** (1 / 3))
				bin_count_scott = int(np.ceil((data_range) / bin_width_scott))
				time.sleep(1)

				# Determine the number of bins using the sqrt method
				num_of_bins_sqrt = int(np.ceil(math.sqrt(len(dist))))
				num_of_bins_rice = int(np.ceil( 2 * (len(dist) ** (1 / 3))))

				def write_binning_parameters():
					bin_summary.write(
						f'=> {input_data}\n'
						"----------------------------------\n"
						"Binning Method\t  | Number of bins\n"
						"------------------+---------------\n"
						f'Freedman-Diaconis | {bin_count}\t(*)\n'
						f'Square root\t\t  | {num_of_bins_sqrt}\n'
						f'Rice\t\t\t  | {num_of_bins_rice}\n'
						f'Scott\t\t\t  | {bin_count_scott}\n'
						"----------------------------------\n\n\n"
						)
				
				if int(lineNo) == 1:
					with open("kde_bins_estimated_summary.dat", "w") as bin_summary:
						write_binning_parameters()

				elif int(lineNo) > 1:
					with open("kde_bins_estimated_summary.dat", "a") as bin_summary:
						write_binning_parameters()
						
				with open(f"kde_bins_estimated_{input_data}.dat", "w") as bin_summary:
					write_binning_parameters()

				output_and_para_files.append(f"kde_bins_estimated_{input_data}.dat")

				if auto_mode == 'full':
					response = 1
					print(f'response is {response}')
					print(f'response is {response}')
					print(f'response is {response}')
					print(f'response is {response}')
					time.sleep(3)
				elif auto_mode == 'semi':
					print(
						"\n  Optimal binning parameters have been estimated."
						'\n  Parameters have been written to the file "CHAP_kde_Par.in".'
						'\n\n  You can modify the parameters if required.'
						'\n   Enter "Yes" below when you are ready.'
						"\n\n   Do you want to proceed?\n    (1) Yes\n    (2) No\n"
						)

					prmpt = "  Enter a response here (1 or 2): "
					response = int(input(prmpt))

					while response != 1 and response != 2:
						print(
							"\n ENTRY REJECTED!"
							"\n **Please enter the appropriate option (1 or 2)\n"
							)
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
								bin_custom = int(para_data[1].strip())
							elif "bandwidth_method" in parameter:
								para_data = parameter.rstrip(' \n').split(",")
								bandwt = para_data[1].strip()
								if (bandwt.isalpha()) == True :
									bandwidth = bandwt
								elif (bandwt.isalpha()) == False :
									bandwidth = float(bandwt)
					bin_set = bin_custom

				print (f" Generating and plotting the histogram of the {input_data}\n")
				time.sleep(2)

				# Generate and plot the histogram of the data
				out_hist = input_data+"_histogram.xvg"
				if "RMSD" in input_data: 
					XaxisLabelXVG = r'RMSD (\cE\C)' 
					XaxisLabelPNG = 'RMSD' + r' ($\AA$)' # Using Latex in matplotlib
				elif "Rg" in input_data:
					XaxisLabelXVG = r'Radius of gyration (\cE\C)'
					XaxisLabelPNG = 'Radius of gyration' + r' ($\AA$)'
				elif "Hbond" in input_data:
					XaxisLabelXVG = "Number of hydrogen bonds"
					XaxisLabelPNG = XaxisLabelXVG
				elif "SASA" in input_data:
					XaxisLabelXVG = r'SASA (nm\S2\N)'
					XaxisLabelPNG = 'SASA' + r' ($nm^{2}$)'

				plt.hist(data_in, bins=bin_set, label=input_data, color='#4CE418', alpha=0.9)
				plt.xlabel(XaxisLabelPNG) # using Latex expression in matplotlib
				plt.ylabel('Count')
				plt.title("Histogram of the "+input_data)
				figname = input_data + "_histogram.png"
				plt.savefig(figname, dpi=600)
				
				output_and_para_files.append(figname)

				# Create a new figure for the KDE
				plt.figure()

				# Assign histogram to a value
				a = plt.hist(data_in, density=True, bins=bin_set,
							label=input_data, color='#4CE418', alpha=0.9)

				# The first elements are the ys, the second are the xs.
				# ys = a[0]; xs = a[1]

				# The x-axis values are boundaries, starting with the lower bound of the first 
				# and ending with the upper bound of the last.
				# So, length of the x-axis > length of the y-axis by 1.

				# Get the upper bounds and write out the histogram
				print (f" Writing out the histogram data of the {input_data}\n")
				time.sleep(2)

				def write_out_plot_files(
					outfile, Keycontent, title, XaxisLabel, YaxisLabel, graphType, lineSetting
					):
					outfile.write(
						f'# This file contains the {Keycontent} values of the {input_data}'
						'\n# data calculated by CHAPERONg from the output of GROMACS\n#\n'
						f'@    title "{title} of {input_data}"\n'
						f'@    xaxis  label "{XaxisLabel}"\n'
						f'@    yaxis  label "{YaxisLabel}"\n'
						f'@TYPE {graphType}\n'
						f'@ s0 legend "{dataName}_{input_data}"{lineSetting}\n'
						)

				with open (out_hist, 'w') as out_his_file:
					lineSet = '\n@    s0 symbol size 0.200000\n''@    s0 line type 0'					
					write_out_plot_files(
						out_his_file, 'histogram', 'Histogram', XaxisLabelXVG, 'Count', 'bar', lineSet
						)
				
				pd.DataFrame(
					{'x_upper':a[1][1:], 'y': a[0]}).to_csv(out_hist,
					header=False, index=False, sep="\t", mode='a'
					)
				
				output_and_para_files.append(out_hist)

				print (f" Estimating the probability density function for {input_data}\n")
				time.sleep(2)
				kde_xs = np.linspace(min(data_in), max(data_in), 300)
				kde = st.gaussian_kde(data_in, bw_method=bandwidth)
				kde_ys = kde.pdf(kde_xs)
				out_kde = input_data+"_KDEdata.xvg"
				with open (out_kde, 'w') as out_kde_file:
					write_out_plot_files(
						out_kde_file, 'KDE-estimated PDF', 'KDE-estimated Probability Density',
						XaxisLabelXVG, 'Density', 'xy', ''
						)					
					
				pd.DataFrame({'x':kde_xs, 'y': kde_ys}).to_csv(out_kde,
								header=False, index=False, sep="\t", mode='a')
				
				output_and_para_files.append(out_kde)

				kdeLabel = input_data + "_PDF"
				plt.plot(kde_xs, kde.pdf(kde_xs), label=kdeLabel, color='r')
				plt.legend()
				plt.ylabel("Density")
				plt.xlabel(XaxisLabelPNG)
				plt.title(f'Kernel Density Estimation Plot of the {input_data}')
				figname = input_data + "_KDE_plot.png"
				plt.savefig(figname, dpi=600)

				output_and_para_files.append(figname)

				print (f" Estimate probability density function for {input_data}...DONE\n"
						"#=============================================================================#\n")
			
			output_and_para_files.append(extracted_data)
			dataOutPath=f'Kernel_Density_Estimation/{input_data}'
			# dataOutPath_old=f'{motherDir}/{input_data}'
			make_dir_for_KDE(dataOutPath)
			for file in output_and_para_files:
				try: shutil.move(file, dataOutPath)
				except FileNotFoundError: pass
			# for file in output_dict['files_to_copy']:
			# 	try: shutil.copy2(file, dataOutPath)
			# 	except FileNotFoundError: pass				

make_dir_for_KDE()			
estimate_PDF_with_KDE()
para_summary = ['CHAP_kde_Par.in', 'kde_bins_estimated_summary.dat', 'CHAP_kde_dataset_list.dat']

for file in para_summary:
	try: shutil.move(file, 'Kernel_Density_Estimation')
	except FileNotFoundError: pass