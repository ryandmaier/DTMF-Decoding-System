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

#from cpe367_wav import cpe367_wav
from cpe367_sig_analyzer import cpe367_sig_analyzer



#----DTMF Tone Frequencies (Hz) [row, column]----#
f1 = [697, 1209]
f2 = [697, 1336]
f3 = [697, 1477]
fA = [697, 1633]
f4 = [770, 1209]
f5 = [770, 1336]
f6 = [770, 1477]
fB = [770, 1633]
f7 = [853, 1209]
f8 = [852, 1336]
f9 = [852, 1477]
fC = [852, 1633]
fstar = [941, 1209]	#f*
f0 = [941, 1336]
fpound = [941, 1477]
fD = [941, 1633]




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
	bk = 1 / M #Average LPF

	# process input	
	xin = 0
	for n_curr in range(s2.get_len()):
		xin = s2.get('xin',n_curr)
		
		########################
		# evaluate each filter
		
			# update history and store newest input
			
			# evaluate difference equations
						
			# update history and store current output
					
		########################
		# combine results from filtering stages
		symbol_val_det = 0

		# save intermediate signals as needed, for plotting
		#  add signals to this list, as desired!
		s2.set('sig_1',n_curr,xin)
		s2.set('sig_2',n_curr,2 * xin)

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
