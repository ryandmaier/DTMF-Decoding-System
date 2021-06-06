#!/usr/bin/env python

############################################
# this EMPTY python fifo class was written by dr fred depiero at cal poly
# distribution is unrestricted provided it is without charge and includes attribution

import sys
import json

class my_fifo:
	
	############################################
	# constructor for signal history object
	def __init__(self,buff_len):
			
		self.buff_len = buff_len
		self.buff = [0] * self.buff_len	#Creates an array of size buff_len full of 0s
		self.index = 0		#Variable to keep track of current index in the array

	############################################
	# update history with newest input and advance head / tail
	def update(self,current_in):
		"""
		:current_in: a new input value to add to recent history
		:return: T/F with any error message
		"""
		#Reset Index to Beginning if at the end of the List
		if ( self.index == self.buff_len):
			self.index = 0
		
		#Adds the current input at the given index
		self.buff[self.index] = current_in

		#Increases size tracker and index
		self.index += 1
		
		return True

	############################################
	# get value in history at a given age, specified by age_indx
	#  age_indx == 0  ->  most recent
	#  age_indx == 1  ->  
	def get(self,age_indx):
		"""
		:indx: an index in the history
			age_indx == 0    ->  most recent historical value
			age_indx == 1    ->  next most recent historical value
			age_indx == M-1  ->  oldest historical value
		:return: value stored in the list of historical values, as requested by indx 
		"""
		#Computes the index of the value to be retrieved
		retrieve_index = self.index - age_indx - 1

		#If ret_index is negative, need to loop to back of list
		if retrieve_index < 0:
			retrieve_index = self.buff_len + retrieve_index	#ret_index is negative
		
		#Finds the value from the accurate index
		val = self.buff[retrieve_index]
		
		return val
