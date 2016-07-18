# -*- coding: utf-8 -*-
# Main Code 8
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
total_generations = 1

# Make false to test with no token frequency
token_freq = True

# Number of times to introduce training set: P&VE uses 3, HareEllman uses 10
epochs = 8

# Case and number treated separately or together?
casenum_sep = True

# Binary or identity vectors
vectors = 'binary'

#####################
# Layer Information #
#####################

#########
# INPUT #
#########

# Input layer will contain:
#   1) Root identifier (9 bits = log_2(500))
#   2) Human identifier (male, female, non-human) (2 bits)
#   3) Declension, Gender?, Case, Number (3 bits, 2 bits, 3 bits, 1 bit)

# n_insyll = 4
# n_phon = 8
# n_feat = 12

human = ['nh', 'mh', 'fh']
declensions = [str(i) for i in range(1, 6)]
genders = ['m', 'f', 'n']

if casenum_sep == True:
    cases = ['Nom', 'Acc', 'Gen', 'Dat', 'Abl', 'Voc']
    numbers = ['Sg', 'Pl']
else:
    cases = ['Nom.Sg', 'Acc.Sg', 'Gen.Sg', 'Dat.Sg', 'Abl.Sg', 'Nom.Pl', 'Acc.Pl', 'Gen.Pl', 'Dat.Pl', 'Abl.Pl']

if vectors == 'binary':
    # Take log base 2 to figure out how many bits we need for each
    human_size = int(ceil(log(len(human), 2))) # 2
    dec_size = int(ceil(log(len(declensions), 2))) # 3
    gen_size = int(ceil(log(len(genders), 2))) # 2
    case_size = int(ceil(log(len(cases), 2))) # 3
    if casenum_sep == True:
        num_size = int(ceil(log(len(numbers), 2))) # 1

    # Now make two way dictionary with bit vectors
    human_dict = functions.binaryDict(human)
    dec_dict = functions.binaryDict(declensions)
    dec_dict.update(functions.invert(dec_dict))
    gen_dict = functions.binaryDict(genders)
    gen_dict.update(functions.invert(gen_dict))
    case_dict = functions.binaryDict(cases)
    case_dict.update(functions.invert(case_dict))
    if casenum_sep == True:
        num_dict = functions.binaryDict(numbers)
        num_dict.update(functions.invert(num_dict))
# Identity vectors
else:
    human_size = len(human)
    dec_size = len(declensions)
    gen_size = len(genders)
    case_size = len(cases)
    if casenum_sep == True:
        num_size = len(numbers)

    human_dict = dict(zip(human, map(tuple, identity(human_size))))
    dec_dict = dict(zip(declensions, map(tuple, identity(dec_size))))
    gen_dict = dict(zip(genders, map(tuple, identity(gen_size))))
    case_dict = dict(zip(cases, map(tuple, identity(case_size))))
    if casenum_sep == True:
        num_dict = dict(zip(numbers, map(tuple, identity(num_size))))

##########
# HIDDEN #
##########

# Number of hidden layers: P&VE uses 30, HareEllman uses 10 for the first layer
# P&VE suggest 60
# Arithmetic mean between inputs (20) and outputs (84) is 52
# Geometric mean is 41
# IF IDENTITY
#   Arithmetic mean between 30 and 84 is 57
#   Geometric mean is 50
if vectors == 'binary':
    hidden_nodes = 40
else:
    hidden_nodes = 50

##########
# OUTPUT #
##########

# Max suffix VVC CVVC
n_sufphon = 7
n_feat = 12

output_nodes = n_sufphon*n_feat

##########################
# Coding the output file #
##########################

# Number of generations
out_file = 'stats_ Epochs%s_Gens%s' % (str(epochs), str(total_generations))

# Token Frequency?
if token_freq == False:
    out_file += '_TokFreqF'
else:
    out_file += '_TokFreqT'
# Case and number separate or together?
if casenum_sep == True:
    out_file += '_CaseNumSepT'
else:
    out_file += '_CaseNumSepF'
# Binary or Identity Vectors?
if vectors == 'binary':
    out_file += '_BinVec'
else:
    out_file += '_IdVec'


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
    "l": (1.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0),
    "w": (1.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 1.0, 1.0, 1.0),
    "j": (1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0), # y
    "i": (1.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0),   
    "u": (1.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 1.0, 1.0),  
    "e": (1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0),  
    "o": (1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 1.0, 1.0),  
    "a": (1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 1.0), 
    "-": (0.5,) * 12
}

feat_to_phon = functions.invert(phon_to_feat)