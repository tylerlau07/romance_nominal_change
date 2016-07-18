# -*- coding: utf-8 -*-
# Author: Tyler Lau

from math import log
from math import ceil
from numpy import identity

import functions

##########
# Corpus #
##########

corpus_file = "../Corpus Preparation/latin_corpus.txt"

##############
# Parameters #
##############

# Trial number
trial = 1

# Generations to run simulation
total_generations = 15

# Make false to test with no token frequency
token_freq = True

# Number of times to introduce training set: P&VE uses 3, HareEllman uses 10
epochs = 8

# Binary or identity vectors
vectors = 'binary'

#####################
# Layer Information #
#####################

#########
# INPUT #
#########

# Input layer will contain:
#   1) Phonological form
#       Compute by multiplying syllables (6) by max phonemes per syllable (8) by features (12) = 576
#       Features from (Chomsky & Halle 1968): see below
#   2) Human identifier (male, female, non-human) (2 bits)
#   3) Declension, Gender?, Case, Number (3 bits, 2 bits, 3 bits, 1 bit)

n_insyll = 6
n_phon = 8
n_feat = 12

human = ['nh', 'mh', 'fh']
declensions = [str(i) for i in range(1, 6)]
genders = ['m', 'f', 'n']
# cases = ['Nom', 'Acc', 'Gen', 'Dat', 'Abl', 'Voc']
cases = ['Nom', 'Acc', 'Gen', 'Dat', 'Abl']
numbers = ['Sg', 'Pl']

if vectors == 'binary':
    # Take log base 2 to figure out how many bits we need for each
    human_size = int(ceil(log(len(human), 2))) # 2
    dec_size = int(ceil(log(len(declensions), 2))) # 3
    gen_size = int(ceil(log(len(genders), 2))) # 2
    case_size = int(ceil(log(len(cases), 2))) # 3
    num_size = int(ceil(log(len(numbers), 2))) # 1

    # Now make two way dictionary with bit vectors
    human_dict = functions.binaryDict(human)
    dec_dict = functions.binaryDict(declensions)
    dec_dict.update(functions.invert(dec_dict))
    gen_dict = functions.binaryDict(genders)
    gen_dict.update(functions.invert(gen_dict))
    case_dict = functions.binaryDict(cases)
    case_dict.update(functions.invert(case_dict))
    num_dict = functions.binaryDict(numbers)
    num_dict.update(functions.invert(num_dict))
# Identity vectors
else:
    human_size = len(human)
    dec_size = len(declensions)
    gen_size = len(genders)
    case_size = len(cases)
    num_size = len(numbers)

    human_dict = dict(zip(human, map(tuple, identity(human_size))))
    dec_dict = dict(zip(declensions, map(tuple, identity(dec_size))))
    gen_dict = dict(zip(genders, map(tuple, identity(gen_size))))
    case_dict = dict(zip(cases, map(tuple, identity(case_size))))
    num_dict = dict(zip(numbers, map(tuple, identity(num_size))))

# TOTAL input bits = 587
input_nodes = sum([n_insyll*n_phon*n_feat, human_size, dec_size, gen_size, case_size, num_size])

##########
# HIDDEN #
##########

# Number of hidden layers: P&VE uses 30, HareEllman uses 10 for the first layer
# P&VE suggest 60
# Mean between inputs (587) and outputs (6) is 296.5
# Geometric mean: sqrt(587*6) = 59.3
hidden_nodes = 60

##########################
# Coding the output file #
##########################

# Number of generations
out_file = 'stats_Gens%s' % str(total_generations)

# Do we drop the genitive or not?
if token_freq == False:
    out_file += '_TokFreqF'

# Number of epochs, number of hidden nodes, trial number
out_file += '_Trial%s.txt' % str(trial)                   

########################
# Frequency Adjustment #
########################

# Adjust type frequencies depending on case and human/nonhuman

# New case frequencies using Delatte et al 1981
# # WITH VOCATIVE
# case_freqs = {
#     'Nom.Sg': 68.11, 'Nom.Pl': 20.85,
#     'Acc.Sg': 69.90, 'Acc.Pl': 49.63,
#     'Gen.Sg': 35.42, 'Gen.Pl': 17.13,
#     'Dat.Sg': 13.46, 'Dat.Pl': 8.27,
#     'Abl.Sg': 64.39, 'Abl.Pl': 23.63,
#     'Voc.Sg': 3.67, 'Voc.Pl': 1
# }

# WITHOUT VOCATIVE
case_freqs = {
    'Nom.Sg': 8.23, 'Nom.Pl': 2.52,
    'Acc.Sg': 8.45, 'Acc.Pl': 6.00,
    'Gen.Sg': 4.28, 'Gen.Pl': 2.07,
    'Dat.Sg': 1.63, 'Dat.Pl': 1,
    'Abl.Sg': 7.78, 'Abl.Pl': 2.86
}

#############################################
# Organize data to make it easier to handle #
#############################################

# Map phonemes to Chomsky and Halle values (1968):
phon_to_feat = {
    "p": (0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
    "t": (0.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
    "k": (0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0),
    "b": (0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0),
    "d": (0.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0),
    "g": (0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0),
    "f": (0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0),
    "v": (0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0),
    "s": (0.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0),
    "z": (0.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0),
    "h": (0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0),
    "m": (1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0),
    "n": (1.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0),
    "N": (1.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0), # engma
    "r": (1.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0),
    "l": (1.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0),
    "w": (1.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0),
    "j": (1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0), # y
    "i": (1.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0),   
    "u": (1.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0),  
    "e": (1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0),  
    "o": (1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0),  
    "a": (1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 1.0), 
    "-": (0.5,) * 12
}

feat_to_phon = functions.invert(phon_to_feat)