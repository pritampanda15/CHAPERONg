
# CHAP_kernel_density_estimation.py -- A python script to estimate probability
#   density function using the kernel density estimator with the Gaussian kernel
# Part of the CHAPERONg suite of scripts
# Input parameters are generated by other scripts in CHAPERONg and are read
#   by this script
# CHAPERONg -- An automation program for GROMACS md simulation
# Author -- Abeeb A. Yekeen
# Contact -- yekeenaa@mail.ustc.edu.cn, abeeb.yekeen@hotmail.com
# Date: 2023.01.16

import matplotlib
# Configure the non-interactive backend
matplotlib.use('AGG')
import matplotlib.pyplot as plt
import math
import time
import numpy as np
import pd as pd
import sys
import scipy.stats as st


lineNo=0
# Read in the data for PDF estimation
# print (" Reading in parameters for FES calculations"+"\n")
# with open("CHAP_kde_dataset_list.dat") as in_par:
# 	alldatasets = in_par.readlines()
#	for lineNo, line in enumerate(alldatasets):

order_p2 = []

input_data="Rg"
with open("RgData.dat") as alldata:
	alldata_lines = alldata.readlines()
	for line in alldata_lines:
		data_point = str(line).split("\n")
		order_p2.append(float(data_point[0]))

# Create a new figure
plt.figure()
# Determine the number of bins automatically
print (" Estimating the optimal number of bins"+"\n")
time.sleep(2)
# Determine the number of bins using the Freedman-Diaconis (1981) method
dist = pd.Series(order_p2)
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

# Scott (1979) method
stdev = dist.std()
bin_width_scott = (3.5 * stdev) / (len(dist) ** (1 / 3))
bin_count_scott = int(np.ceil((data_range) / bin_width_scott))
time.sleep(1)

# with open("CHAP_kde_Par.in", "a") as in_par:
# 	in_par.write(f'bin_count,{bin_count}')

# Determine the number of bins using the sqrt method
num_of_bins_sqrt = int(np.ceil(math.sqrt(len(dist))))
num_of_bins_rice = int(np.ceil( 2 * (len(dist) ** (1 / 3))))

print(f"\n Optimal binning parameters have been estimated.\
	\n These parameters have been written to file (CHAP_kde_Par.in).\
	\n\n Do you want to proceed?\n  (1) Yes\n  (2) No\n")

prmpt = " Enter a response here (1 or 2): "
response = int(input(prmpt))

while response != 1 and response != 2:
	print("\n ENTRY REJECTED!\n **Please enter the appropriate option (1 or 2)\n")
	response = int(input(prmpt))

if int(lineNo) == 0:
	with open("kde_bins_estimated_summary.dat", "w") as bin_summary:
		bin_summary.write(f"{input_data}\n")
		bin_summary.write(f"Binning Method\t  | Number of bins\n")
		bin_summary.write(f"------------------|---------------\n")
		bin_summary.write(f"Freedman-Diaconis | {bin_count}\t(*)\n")
		bin_summary.write(f"Square root\t\t  | {num_of_bins_sqrt}\n")
		bin_summary.write(f"Rice\t\t\t  | {num_of_bins_rice}\n")
		bin_summary.write(f"Scott\t\t\t  | {bin_count_scott}\n")
elif int(lineNo) > 0:
	with open("kde_bins_estimated_summary.dat", "a") as bin_summary:
		bin_summary.write(f"{input_data}\n")
		bin_summary.write(f"Binning Method\t  | Number of bins\n")
		bin_summary.write(f"------------------|---------------\n")
		bin_summary.write(f"Freedman-Diaconis | {bin_count}\t(*)\n")
		bin_summary.write(f"Square root\t\t  | {num_of_bins_sqrt}\n")
		bin_summary.write(f"Rice\t\t\t  | {num_of_bins_rice}\n")
		bin_summary.write(f"Scott\t\t\t  | {bin_count_scott}\n")

if response == 2:
	sys.exit(0)
elif response == 1:
	print (f"\n Updating input parameters for FES calculations\n")
	with open("CHAP_kde_Par.in") as in_par:
		for parameter in in_par.readlines():
			if "plotTitle" in parameter:
				para_data = parameter.rstrip('\n').split(",")
				plotTitle = str(para_data[1])+str(" Free Energy Surface")
			elif "bin_count" in parameter:
				para_data = parameter.rstrip('\n').split(",")
				bin_custom = int(para_data[1])
	bin_set = bin_custom

print (f" Generating and plotting the histogram of the {input_data}\n")
time.sleep(2)

# Generate and plot the histogram of the data
plt.hist(order_p2, bins=bin_set, label=input_data, color='#4CE418', alpha=0.9)
plt.xlabel(input_data + r'$\AA$')
plt.ylabel('Count')
plt.title("Histogram of the "+input_data)
figname = input_data + "histogram.png"
plt.savefig(figname, dpi=600)
# plt.savefig(input_data + "_histogram.png", dpi=300)

# Create a new figure for the KDE
plt.figure()

# Assign histogram to a value
a = plt.hist(order_p2, density=True, bins=bin_set, label=input_data, color='#4CE418', alpha=0.9)

# The first elements are the ys, the second are the xs.
ys = a[0]; xs = a[1]

# The x-axis values are boundaries, starting with the lower bound of the first 
# and ending with the upper bound of the last.
# So, length of the x-axis > length of the y-axis by 1.

# Get the upper bounds and write out the histogram
print (f" Writing out the histogram data of the {input_data}\n")
time.sleep(2)
out_hist = input_data+"_histogram.dat"
pd.DataFrame({'x_upper':a[1][1:], 'y': a[0]}).to_csv(out_hist, index=False, sep="\t")

print (f" Estimating the probability density function with KDE\n")
time.sleep(2)
kde_xs = np.linspace(min(order_p2), max(order_p2), 300)
kde = st.gaussian_kde(order_p2)
kde_ys = kde.pdf(kde_xs)
out_kde = input_data+"_KDEdata.dat"
pd.DataFrame({'x':kde_xs, 'y': kde_ys}).to_csv(out_kde, index=False, sep="\t")
kdeLabel = input_data + "_PDF"
plt.plot(kde_xs, kde.pdf(kde_xs), label=kdeLabel, color='r')
plt.legend()
plt.ylabel("Density")
plt.xlabel(input_data + r'($\AA$)')
plt.title("Kernel Density Estimation Plot of the "+input_data)
figname = input_data + "kde.png"
plt.savefig(figname, dpi=600)
