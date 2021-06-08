#!/usr/bin/python

import sys
import time

import base64
import random as random

import datetime
import time
import math

import matplotlib.pyplot as plt
import numpy as np
from fifo import my_fifo

#from cpe367_wav import cpe367_wav
from cpe367_sig_analyzer import cpe367_sig_analyzer



#----DTMF Tone Frequencies (Hz) [row, column]----#
f1 = [697, 1209]
f2 = [697, 1336]
f4 = [770, 1209]
f5 = [770, 1336]
#Only testing for these 4 freq.


############################################
############################################
# define routine for implementing a digital filter
def process_wav(fpath_sig_in):
	"""
	: read a WAV file and filter, pre-subsample
	: return: DFT
	"""


	###############################
	# setup signal info and analyzer
	td_sig_list = ['sig_1','sig_2']
	fs = 4000

	s2 = cpe367_sig_analyzer(td_sig_list,fs)
	s2.load(fpath_sig_in)
	s2.print_desc()

	# to do: setup filters
	m = 10
	bk = 1 / m #Average LPF

	#----------BPF Set Up--------------#
	#w0 for dif frequencies
	w697 = 0.3485 * math.pi
	w770 = 0.385 * math.pi
	w1209 = 0.6045 * math.pi
	w1336 = 0.668 * math.pi
	w0 = [w697, w770, w1209, w1336] #Array w/ each filter phase

	#----------FIFO Set Up-------------#
	fifo_in = my_fifo(m)
	fifo_outs = [0] * len(w0) # Output Fifo for each of the 4 BPFs
	for i in range(len(w0)):
		ff = my_fifo(m)
		fifo_outs[i] = ff

	#Radius Value 0.9 <= r < 1.0
	r = 0.95
	g = round(1 - r,6) #Gain factor (from doc)

	#Constant Coefficients
	b0 = g
	a2 = -(r ** 2)
	#loop through w0 for dif bandpass filters
	a1 = 2 * r * math.cos(w0[0]) #varies with phase

	# y[n] = b0 * x[n] + a1 * y[n-1] + a2 * y[n-2] (Next Step)
	# y[n] = g * x[n] + 2r*cos(w) * y[n-1] - r^2 * y[n-2]

	# process input
	xin = 0
	for n_curr in range(s2.get_len()):
		xin = s2.get('xin',n_curr)
		fifo_in.update(xin)

		symbol_val_det = 0

		for i in range(len(w0)): # for each frequency
			w = w0[i]
			print("i =",i," , f_bp =",round(w * 2000/math.pi,5))
			print("fvtool([",g,"],[1,-",2*r*math.cos(w),",",r*r,"],'Fs',4000)")
			# y[n] = g * x[n] + 2r*cos(w) * y[n-1] - r^2 * y[n-2]
			yout = g*fifo_in.get(0) + 2*r*math.cos(w)*fifo_outs[i].get(0) - r*r*fifo_outs[i].get(1)
			yout = int(round(yout))
			fifo_outs[i].update(yout)
			avg_prev = 0
			n_avg = 3
			for j in range(n_avg):
				avg_prev += abs(fifo_outs[i].get(j))
			avg_prev = avg_prev/n_avg
			guess = 0
			if avg_prev>16:
				guess = 1
			s2.set('sig_1',n_curr,guess)
			s2.set('sig_2',n_curr,avg_prev) # record yout in sig_2 to check the plot


		########################
		# evaluate each filter

			# update history and store newest input

			# evaluate difference equations

			# update history and store current output

		########################
		# combine results from filtering stages

		# save intermediate signals as needed, for plotting
		#  add signals to this list, as desired!
		# s2.set('sig_1',n_curr,xin)
		# s2.set('sig_2',n_curr,2 * xin)


		# save detector symbol
		s2.set('symbol_det',n_curr,symbol_val_det)

		# get correct symbol
		symbol_val = s2.get('symbol_val',n_curr)

		# compare detected signal to correct signal
		symbol_val_err = 0
		if symbol_val != symbol_val_det: symbol_val_err = 1

		# save error signal
		s2.set('error',n_curr,symbol_val_err)


	# display mean of error signal
	err_mean = s2.get_mean('error')
	print('mean error = '+str( round(100 * err_mean,1) )+'%')

	# plot results
	plot_sig_list = ['symbol_val','symbol_det','error']
	plot_sig_list.extend(td_sig_list)

	s2.plot(plot_sig_list)

	return True






############################################
############################################
# define main program
def main():

	# check python version!
	major_version = int(sys.version[0])
	if major_version < 3:
		print('Sorry! must be run using python3.')
		print('Current version: ')
		print(sys.version)
		return False

	# check args
	if len(sys.argv) != 1:
		print('usage: python cpe367_dtmf_example.py')
		return False

	# assign file name
	fpath_sig_in = 'dtmf_signals_slow.txt'
	# fpath_sig_in = 'dtmf_signals_fast.txt'


	# let's do it!
	return process_wav(fpath_sig_in)




############################################
############################################
# call main function
if __name__ == '__main__':

	main()
	quit()
