# -*- coding: utf-8 -*-

# Author: Tyler Lau
# This program prepares the corpus in the necessary format for the simulation

from collections import defaultdict
from collections import OrderedDict
import codecs

#############
# Constants #
#############

def invert(d):
    '''
    Invert a dictionary
    '''
    return dict((value, key) for key, value in d.iteritems())

# Also replace diphthongs with single letter
spec_seq = {'ph':'p', 'th':'t', 'ch':'k', 'qu':'kw',
			'y':'i', 'c':'k', 'x':'ks', 'h':'-', 'v':'w',
			'gn':'Nn', 'ng':'Ng', 'nk':'Nk', u'iū':u'jū'}

vowels = {'a':'a', 'e':'e', 'i':'i', 'o':'o', 'u':'u'} 

diphthongs = {'ui':'1', 'ei':'2', 'eu':'3', 'oe':'4', 'ou':'5', 'ae':'6', 'au':'7'}

revert_to_diph = invert(diphthongs) 

lv = {u'ā':'aa', u'ē':'ee', u'ī':'ii', u'ō':'oo', u'ū':'uu', u'ȳ':'yy'}

consonant_clusters = ['pr','br','tr','dr','kr','gr','fr',
                      'pl','bl','kl','gl','fl',
                      'ps','kw']

triple_clusters = ['spr', 'str', 'skr']

# Combine vowels, diphthongs, and long vowels
all_v = {}
all_v.update(vowels)
all_v.update(revert_to_diph)
all_v.update(lv)

# Combine sequences to be replaced
to_replace = {}
to_replace.update(spec_seq)
to_replace.update(diphthongs)

cases = ['NomSg', 'NomPl', 'AccSg', 'AccPl', 'GenSg', 'GenPl',
		'DatSg', 'DatPl', 'AblSg', 'AblPl', 'VocSg', 'VocPl']

#############
# Functions #
#############

def replace(word):
	'''
	Replace phonemic sounds with phonetic
	'''
	# First replace phonemic consonants with phonetic and diphthongs with symbols
	for seq in to_replace.keys():
		if seq in word:
			word = word.replace(seq, to_replace[seq])
	# Replace initial 'iu' with 'yu'
	if word[0:2] == 'iu':
		word = 'j' + word[1:]
	return word

def syllabify(word):
	'''
	Treat syllables as CV so that relevant information in ending will line up
	'''
	new_word = ''
	for i in range(0, len(word)):
		letter = word[i]
		# If a vowel, marks the end of a syllable
		if letter in all_v.keys():
			new_word += all_v[letter] + '.'
		else:
			new_word += letter
	return new_word

def realign(word):
	'''
	Realign codas to onsets
	'''
	word = word.strip('.').split('.')

	# If monosyllabic ignore
	if len(word) == 1:
		return word

	# Leave first one alone
	for i in range(1, len(word)):
		syllable = word[i]
		# If more complicated than CV
		while len(word[i]) > 2:
			# Ex. 'ees', 'stra', 'tra'
			if syllable[0:3] not in triple_clusters and syllable[0:2] not in consonant_clusters:
				# Move onset to coda of previous
				if syllable[0] not in vowels and syllable[1] not in vowels:
					word[i-1] = word[i-1] + syllable[0]
					word[i] = syllable[1:]
			# Ex. 'taa'
			if len(syllable) == 3 and syllable[1:] in lv.values(): break
			else: break

	# If last syllable is one or two consonants, realign
	if len(word[-1]) == 1 and word[-1] not in vowels:
		word[-2] = word[-2] + word[-1]
		del(word[-1])
	elif len(word[-1]) == 2 and word[-1][0] not in vowels and word[-1][1] not in vowels:
		word[-2] = word[-2] + word[-1]
		del(word[-1])
	return word

def addDashes(word):
	'''
	Add dashes in appropriate places
	'''
	for syllable in word:
		# New syllable
		new_syll = syllable
		
		# First get rid of codas
		if syllable[-1] not in vowels:
			

		# Possibility of str
		# if len(syllable) >= 4:


########
# Main #
########

reader = codecs.open('noun_paradigms_rev.txt', encoding='utf-8', mode='rU')

row_order = reader.readline().strip('\r\n').split('\t')

corpus = defaultdict(dict)

for row in reader.readlines():
	row = row.strip("\r\n").split("\t")
	# There are some homophones
	if row[0] not in corpus.keys():
		for i in range(1, len(row)):
			corpus[row[0]][row_order[i]] = row[i]
	# Dictionary mapping word to each of its features
	else:
		for i in range(1, len(row)):
			corpus[row[0]+'2'][row_order[i]] = row[i]

for word in corpus.keys():
	for case in cases:
		if corpus[word][case] != '-':
			mod_word = replace(corpus[word][case])
			# If alternate forms, only use first one
			if '/' in mod_word:
				mod_word = mod_word[:mod_word.index('/')]
			syll_word = syllabify(mod_word)
			print realign(syll_word)

# with open('latin_corpus.txt', mode = 'wb') as f:
# 	out = csv.writer(f, delimiter = '\t')

	