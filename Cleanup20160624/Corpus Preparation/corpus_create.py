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

###########
# Objects #
###########

class Lemma:
	'''Takes in dictionary containing information for each word form'''
	def __init__(self, *args, **kwargs):
		for key, value in kwargs.iteritems():
			setattr(self, key, value)

		# Initialize dictionary to store info for each case
		self.cases = {}

	def addCase(self, case, case_info):
		'''Adds the case information'''
		self.cases[case] = case_info

	def realign(self):
		for case in self.cases:
			# Determine the case with most syllables
			self.cases[case].dashed

class Case:
    def __init__(self, parent_lemma, case, phonology):
		self.parent_lemma = parent_lemma
		if '/' in phonology:
			self.mod_phon = phonology[:phonology.index('/')]
		else:
			self.mod_phon = phonology

		self.phonetic = replace(self.mod_phon)
		self.syllabified = syllabify(self.phonetic)
		self.coda_moved = codaToOnset(self.syllabified)
		self.dashed = addDashes(self.coda_moved)


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

def codaToOnset(word):
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
	Max of six syllables, max of 7 spots CCCVVCC
	'''
	fixed_word = []

	for i in range(0, len(word)):
		syllable = word[i]
		syll_len = len(syllable)
		
		# If only one letter in syllable it is a vowel
		if syll_len == 1:
			new_syll = '-'*3 + syllable + '-'*4

		# Could be VV, CV, or VC
		elif syll_len == 2:
			# If VV
			if syllable[0] in vowels and syllable[1] in vowels:
				new_syll = '-'*3 + syllable + '-'*3
			# If CV
			elif syllable[0] not in vowels:
				new_syll = '-' + syllable[0] + '-' + syllable[1] + '-'*4
			# If VC
			else:
				new_syll = '-'*3 + syllable[0] + '-'*2 + syllable[1] + '-'

		# If 3 or more
		else:
			# FIRST DEAL WITH ONSETS	
			# No onset ---V
			if syllable[0] in vowels:
				onset_done = '-'*3 + syllable
			# One onset -C-
			elif syllable[0] not in vowels and syllable[1] in vowels:
				onset_done = '-' + syllable[0] + '-' + syllable[1:]
			# Two onsets -CC
			elif syllable[0] not in vowels and syllable[1] not in vowels:
				onset_done = '-' + syllable
			# Three onsets CCC
			else:
				onset_done = syllable 

			# NOW DEAL WITH NUCLEUS
			# Minimum is CCCV
			if len(onset_done) == 4:
				new_syll = onset_done + '-'*4
			else:
				# If CCCVV
				if onset_done[4] in vowels:
					nuc_done = onset_done
				# If CCCVC
				else:
					nuc_done = onset_done[:4] + '-' + onset_done[4:]

				# NOW DEAL WITH CODA(S)
				# No coda
				if len(nuc_done) == 5:
					new_syll = nuc_done + '-'*3
				# One coda
				elif len(nuc_done) == 6:
					new_syll = nuc_done[:-1] + '-' + nuc_done[-1] + '-'
				# Two codas
				elif len(nuc_done) == 7:
					new_syll = nuc_done[:-2] + '-' + nuc_done[-2:]
				# Three codas
				else:
					new_syll = nuc_done

		# SANITY CHECK
		if len(new_syll) != 8:
			print "You screwed up the size of the syllable"
			print word, len(new_syll), new_syll
			raise SystemExit
		else:
			fixed_word.append(new_syll)

	return fixed_word

########
# Main #
########

reader = codecs.open('noun_paradigms_rev.txt', encoding='utf-8', mode='rU')

row_order = reader.readline().strip('\r\n').split('\t')

corpus = []

for row in reader.readlines():
	row = row.strip("\r\n").split("\t")

	# There are some homophones
	# if lemma not in corpus.keys():
	row_dict = {row_order[i]: value for i, value in enumerate(row)}
	lemma = Lemma(**row_dict)
	corpus.append(lemma)

	for case in cases:
		declined = Case(lemma, case, getattr(lemma, case))
		lemma.addCase(case, declined)
		print declined.dashed


	# lemma.alignPhon
	# print lemma.phonetic
	# # Dictionary mapping word to each of its features
	# else:
	# 	for i in range(1, len(row)):
	# 		corpus[row[0]+'2'][row_order[i]] = row[i]

# for word in corpus.keys():
# 	for case in cases:
# 		if corpus[word][case] != '-':
# 			mod_word = replace(corpus[word][case])
# 			# If alternate forms, only use first one
# 			if '/' in mod_word:
# 				mod_word = mod_word[:mod_word.index('/')]
# 			syll_word = syllabify(mod_word)
# 			realigned_word = realign(syll_word)
# 			dashed_word = addDashes(realigned_word)
# 			print dashed_word
# with open('latin_corpus.txt', mode = 'wb') as f:
# 	out = csv.writer(f, delimiter = '\t')

	