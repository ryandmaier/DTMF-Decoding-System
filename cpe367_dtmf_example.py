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

# Dictionary maps detected frequency array to corresponding symbol
# detected frequency array = 1 where [697, 770, 1209, 1336] is detected in the input
f_dict = {
	'1010' : 1,
	'1001' : 2,
	'0110' : 4,
	'0101' : 5
}

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
	td_sig_list = ['sig_1','sig_2','sig_3','sig_4']
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
	r = 0.78
	g = round(1 - r,6) #Gain factor (from doc)
	

	#Converting Bk coeffecients to be Integer-Based
	C = 9 				#Accuracy Constant (2^C)
	b0 = int(round(g * (2 ** C)))
		#a1 is variable so done in loop
	a2 = int( round((r**2) * (2**C)) )
	
	# y[n] = b0 * x[n] + a1 * y[n-1] + a2 * y[n-2] (Next Step)
	# y[n] = g * x[n] + 2r*cos(w) * y[n-1] - r^2 * y[n-2]


	# process input
	xin = 0
	for n_curr in range(s2.get_len()):
		xin = s2.get('xin',n_curr)
		fifo_in.update(xin)

		determined_freqs = [0, 0, 0, 0]	#Determined outputs of filters

		# loop for each frequency - Applies BPF, abs(), LPF w avg, and determines if each freq is present
		for i in range(len(w0)):
			w = w0[i]
			
			#Round Bk coefficients for Integer-Based Digital Filter
			a1 = int( round(2*r*math.cos(w)*(2 ** C)) )

			print("i =",i," , f_bp =",round(w * 2000/math.pi,5))
			print("fvtool([",g,"],[1,-",2*r*math.cos(w),",",r*r,"],'Fs',4000)")
			# y[n] = g * x[n] + 2r*cos(w) * y[n-1] - r^2 * y[n-2]
			
			yout = b0*fifo_in.get(0) + a1 *fifo_outs[i].get(0) - a2*fifo_outs[i].get(1)
			yout = int(round(yout >> C)) #Right shift by C again

			fifo_outs[i].update(yout)
			avg_prev = 0
			n_avg = 20
			for j in range(n_avg): # takes average of last n_avg youts, similar effect to Low Pass Filter
				avg_prev += abs(fifo_outs[i].get(j))
			avg_prev = avg_prev/n_avg
			determined_freqs[i] = avg_prev

		if determined_freqs[0] > determined_freqs[1]:
			determined_freqs[0] = 1
			determined_freqs[1] = 0
		else:
			determined_freqs[0] = 0
			determined_freqs[1] = 1
		
		if determined_freqs[2] > determined_freqs[3]:
			determined_freqs[2] = 1
			determined_freqs[3] = 0
		else:
			determined_freqs[2] = 0
			determined_freqs[3] = 1
		
		for i in range(len(w0)):
			sig = 'sig_' + str(i+1) # sig_1 through sig_4 - plots of the guesses for each w
			s2.set(sig,n_curr,determined_freqs[i]) # record sig_i plot of frequency guess

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
		symbol_val_det = get_symbol_from_freqs_detected(determined_freqs)
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



def get_symbol_from_freqs_detected(detected_freqs):
	key = ''
	for bin in detected_freqs:
		key += str(bin)
	print(key)
	if key in f_dict.keys():
		return f_dict.get(key)
	return 1


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
	#fpath_sig_in = 'dtmf_signals_slow.txt'
	fpath_sig_in = 'dtmf_signals_fast.txt'


	# let's do it!
	return process_wav(fpath_sig_in)




############################################
############################################
# call main function
if __name__ == '__main__':

	main()
	quit()
