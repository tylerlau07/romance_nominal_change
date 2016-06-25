# -*- coding: utf-8 -*-

# Author: Tyler Lau
# This program will determine the root and case endings of each word
# We use the lemmatizer at http://www.ilc.cnr.it/lemlat/

import urllib
import time
import re
import csv

from bs4 import BeautifulSoup
import codecs

start = time.time()

cases = ['nomsg', 
		'nompl', 
		'gensg', 
		'genpl', 
		'accsg', 
		'accpl']

LV = {u'ā':'a',u'ē':'e',u'ī':'i',u'ō':'o',u'ū':'u',u'ȳ':'y'}

#############
# Functions #
#############

def findIndices(word):
	'''
	Finds the indices for the long vowels and v's for replacement to search
	Returns rewritten word, dictionary mapping LV indices to long vowels, and list of v indices
	'''
	LV_indices = {}
	v_indices = []
	for i in range(0, len(word)):
		# Find indices of long vowels and replace with short
		if word[i] in LV.keys():
			LV_indices[i] = word[i]
			word = word[:i] + LV[word[i]] + word[i+1:]
		# Get v indices
		elif word[i] == 'v':
			v_indices.append(i)
	return word, LV_indices, v_indices

def segmentWord(word):
	'''
	Looks up a word in the Latin lemmatizer
	Returns root and suffix
	'''
	soup = urllib.urlopen("http://www.ilc.cnr.it/lemlat/cgi-bin/LemLat_cgi.cgi?World+Form="+word)
	htmlSource = soup.read()                            
	soup.close() 

	parsed_html = BeautifulSoup(htmlSource)

	# Create flag for whether segmentation has been found or not
	segment_found = False
	relevant = parsed_html.body.find('td', attrs={'valign':'top'})

	# Search through "analyses" until proper segmentation is found
	while segment_found == False:
		# If there is a root and suffix(es)
		if len(re.findall("\S+", relevant.text)) >= 2:
			segment_found = True
		# Otherwise, find the next one
		else:
			# Search next for analysis
			if relevant.find_next('td', attrs={'valign':'top'}) != None:
				relevant = relevant.find_next('td', attrs={'valign':'top'})
			# If out of analyses, determine the root is null
			else: 
				segment_found = True

	root_suf = re.findall("\S+", relevant.text)

	root = root_suf[0]

	# Collapse if multiple suffixes
	if len(root_suf) >= 2:
		suf = ''.join(root_suf[1:]).strip('-')

	# Suffix null if only 1
	else:
		suf = 'NULL'

	return root, suf

def restoreLVV(root, suffix, LV_indices, v_indices):
	'''
	Re-replace vowels with long vowels in root/suffix
	Takes in the root, suffix, and dictionary and list of indices
	'''
	for index, vowel in LV_indices.iteritems():
		# If index smaller than length of root, then in root
		if index < len(root):
			root = root[:index] + vowel + root[index+1:]
		# Else it is in the suffix
		else:
			suf_index = index - len(root)
			suffix = suffix[:suf_index] + vowel + suffix[suf_index+1:]

	# Re-replace 'u' with 'v'
	for index in v_indices:
		root = root[:index] + 'v' + root[index+1:]

	return root, suffix

########
# Main #
########

reader = codecs.open('declinedforms.txt', encoding='utf-8', mode='rU')

with open('rootending.txt', mode = 'ab') as f:
	out = csv.writer(f, delimiter = '\t')
	out.writerow(["Form", "Root", "Suffix", "Case", "Gender", "Declension"])
	# Each row is a word's case forms
	for row in reader.readlines():
		row = row.strip("\r").split("\t")
		# First and second elements are gender and declension
		gender = row[0]
		dec = row[1]
		
		# Each element in the row is a word
		for i in range(2, len(row)):
			if "/" in row[i]:
				word = row[i][:row[i].index("/")].strip("*") 
			else:
				word = row[i]
			case = cases[i-2]

			try:
				searchword, LV_indices, v_indices = findIndices(word)
				root, suffix = segmentWord(searchword)
				re_root, re_suffix = restoreLVV(root, suffix, LV_indices, v_indices)

			# If there is no breakdown
			except AttributeError:
				re_root, re_suffix = ('N/A', 'N/A')

			# Write out the word and case
			to_write = unicode(word).encode('utf-8'), unicode(re_root).encode('utf-8'), unicode(re_suffix).encode('utf-8'), case, gender, dec
			print to_write
			out.writerow(to_write)
		