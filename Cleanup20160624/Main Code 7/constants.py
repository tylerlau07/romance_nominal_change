# -*- coding: utf-8 -*-
# Main Code 7
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
trial = 5

# Generations to run simulation
total_generations = 10

# Make false to test with no token frequency
token_freq = True

# Number of times to introduce training set: P&VE uses 3, HareEllman uses 10
epochs = 3

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
# Arithmetic mean between inputs (20) and outputs (77) is 48.5
# Geometric mean is 39.24
# IF IDENTITY
#   Arithmetic mean between 30 and 77 is 57
#   Geometric mean is 50
# MINIMAL FEATURES
#   Arithmetic mean between 20 and 42 is 31
#   Geometric mean between 20 and 42 is 28.98
hidden_nodes = 30

##########################
# Coding the output file #
##########################

# Number of generations
out_file = 'stats_NoSoundChange_Epochs%s_Gens%s' % (str(epochs), str(total_generations))

# Token Frequency?
if token_freq == False:
    out_file += '_TokFreqF'
else:
    out_file += '_TokFreqT'
# # Case and number separate or together?
# if casenum_sep == True:
#     out_file += '_CaseNumSepT'
# else:
#     out_file += '_CaseNumSepF'
# # Binary or Identity Vectors?
# if vectors == 'binary':
#     out_file += '_BinVec'
# else:
#     out_file += '_IdVec'


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

# Map phonemes to Chomsky and Halle values (1968) --> Hayes 2009:
cns = son = cor = nas = cnt = voi = vow = hgh = low = frt = bck = (0.0, 1.0, -1.0)

# phon_to_feat = {
#     # "p": (cns[1],  son[-1], cor[-1], nas[-1], cnt[-1], voi[-1], vow[-1], hgh[0],  low[0],  frt[0],  bck[0]), # rnd[-1]), 
#     # "t": (cns[1],  son[-1], cor[1],  nas[-1], cnt[-1], voi[-1], vow[-1], hgh[0],  low[0],  frt[0],  bck[0]), # rnd[-1]),
#     # "k": (cns[1],  son[-1], cor[-1], nas[-1], cnt[-1], voi[-1], vow[-1], hgh[1],  low[-1], frt[0],  bck[0]), # rnd[-1]),
#     "b": (cns[1],  son[-1], cor[-1], nas[-1], cnt[-1], voi[1],  vow[-1], hgh[0],  low[0],  frt[0],  bck[0]), # rnd[-1]), # RELEVANT
#     # "d": (cns[1],  son[-1], cor[1],  nas[-1], cnt[-1], voi[1],  vow[-1], hgh[0],  low[0],  frt[0],  bck[0]), # rnd[-1]),
#     # "g": (cns[1],  son[-1], cor[-1], nas[-1], cnt[-1], voi[1],  vow[-1], hgh[1],  low[-1], frt[0],  bck[0]), # rnd[-1]),
#     # "f": (cns[1],  son[-1], cor[-1], nas[-1], cnt[1],  voi[-1], vow[-1], hgh[0],  low[0],  frt[0],  bck[0]), # rnd[-1]), 
#     # "v": (cns[1],  son[-1], cor[-1], nas[-1], cnt[1],  voi[1],  vow[-1], hgh[0],  low[0],  frt[0],  bck[0]), # rnd[-1]),
#     "s": (cns[1],  son[-1], cor[1],  nas[-1], cnt[1],  voi[-1], vow[-1], hgh[0],  low[0],  frt[0],  bck[0]), # rnd[-1]), # RELEVANT
#     # "z": (cns[1],  son[-1], cor[1],  nas[-1], cnt[1],  voi[1],  vow[-1], hgh[0],  low[0],  frt[0],  bck[0]), # rnd[-1]),
#     # "h": (cns[1],  son[-1], cor[-1], nas[-1], cnt[1],  voi[-1], vow[-1], hgh[0],  low[0],  frt[0],  bck[0]), # rnd[-1]),
#     "m": (cns[1],  son[1],  cor[-1], nas[1],  cnt[-1], voi[1],  vow[-1], hgh[0],  low[0],  frt[0],  bck[0]), # rnd[-1]), # RELEVANT
#     # "n": (cns[1],  son[1],  cor[1],  nas[1],  cnt[-1], voi[1],  vow[-1], hgh[0],  low[0],  frt[0],  bck[0]), # rnd[-1]),
#     # "N": (cns[1],  son[1],  cor[-1], nas[1],  cnt[-1], voi[1],  vow[-1], hgh[1],  low[-1], frt[0],  bck[0]), # rnd[-1]), # engma
#     "r": (cns[1],  son[1],  cor[1],  nas[-1], cnt[1],  voi[1],  vow[-1], hgh[0],  low[0],  frt[0],  bck[0]), # rnd[-1]), # RELEVANT
#     # "l": (cns[1],  son[1],  cor[1],  nas[-1], cnt[1],  voi[1],  vow[-1], hgh[0],  low[0],  frt[0],  bck[0]), # rnd[-1]),
#     # "w": (cns[-1], son[1],  cor[-1], nas[-1], cnt[1],  voi[1],  vow[-1], hgh[1],  low[-1], frt[-1], bck[1]), # rnd[1]),
#     # "j": (cns[-1], son[1],  cor[-1], nas[-1], cnt[1],  voi[1],  vow[-1], hgh[1],  low[-1], frt[1], bck[-1]), # rnd[-1]), # y
#     "i": (cns[-1], son[1],  cor[-1], nas[-1], cnt[1],  voi[1],  vow[1],  hgh[1],  low[-1], frt[1], bck[-1]), # rnd[-1]), # RELEVANT
#     "u": (cns[-1], son[1],  cor[-1], nas[-1], cnt[1],  voi[1],  vow[1],  hgh[1],  low[-1], frt[-1], bck[1]), # rnd[1]),  # RELEVANT
#     "e": (cns[-1], son[1],  cor[-1], nas[-1], cnt[1],  voi[1],  vow[1],  hgh[-1], low[-1], frt[1], bck[-1]), # rnd[-1]), # RELEVANT
#     "o": (cns[-1], son[1],  cor[-1], nas[-1], cnt[1],  voi[1],  vow[1],  hgh[-1], low[-1], frt[-1], bck[1]), # rnd[1]),  # RELEVANT
#     "a": (cns[-1], son[1],  cor[-1], nas[-1], cnt[1],  voi[1],  vow[1],  hgh[-1], low[1],  frt[-1], bck[-1]), # rnd[-1]), # RELEVANT
#     "-": (0.0,) * n_feat
# }

# MINIMALLY DISTINGUISHING FEATURES
phon_to_feat = {
    # "p": (cns[1],  son[-1], cor[-1], nas[-1], cnt[-1], voi[-1], vow[-1], hgh[0],  low[0],  frt[0],  bck[0]), # rnd[-1]), 
    # "t": (cns[1],  son[-1], cor[1],  nas[-1], cnt[-1], voi[-1], vow[-1], hgh[0],  low[0],  frt[0],  bck[0]), # rnd[-1]),
    # "k": (cns[1],  son[-1], cor[-1], nas[-1], cnt[-1], voi[-1], vow[-1], hgh[1],  low[-1], frt[0],  bck[0]), # rnd[-1]),
    "b": (son[-1], cnt[-1], hgh[0],  frt[0], low[0],  bck[0]), # rnd[-1]), # RELEVANT
    # "d": (cns[1],  son[-1], cor[1],  nas[-1], cnt[-1], voi[1],  vow[-1], hgh[0],  low[0],  frt[0],  bck[0]), # rnd[-1]),
    # "g": (cns[1],  son[-1], cor[-1], nas[-1], cnt[-1], voi[1],  vow[-1], hgh[1],  low[-1], frt[0],  bck[0]), # rnd[-1]),
    # "f": (cns[1],  son[-1], cor[-1], nas[-1], cnt[1],  voi[-1], vow[-1], hgh[0],  low[0],  frt[0],  bck[0]), # rnd[-1]), 
    # "v": (cns[1],  son[-1], cor[-1], nas[-1], cnt[1],  voi[1],  vow[-1], hgh[0],  low[0],  frt[0],  bck[0]), # rnd[-1]),
    "s": (son[-1], cnt[1],  hgh[0],  frt[0], low[0],  bck[0]), # rnd[-1]), # RELEVANT
    # "z": (cns[1],  son[-1], cor[1],  nas[-1], cnt[1],  voi[1],  vow[-1], hgh[0],  low[0],  frt[0],  bck[0]), # rnd[-1]),
    # "h": (cns[1],  son[-1], cor[-1], nas[-1], cnt[1],  voi[-1], vow[-1], hgh[0],  low[0],  frt[0],  bck[0]), # rnd[-1]),
    "m": (son[1],  cnt[-1], hgh[0],  frt[0], low[0],  bck[0]), # rnd[-1]), # RELEVANT
    # "n": (cns[1],  son[1],  cor[1],  nas[1],  cnt[-1], voi[1],  vow[-1], hgh[0],  low[0],  frt[0],  bck[0]), # rnd[-1]),
    # "N": (cns[1],  son[1],  cor[-1], nas[1],  cnt[-1], voi[1],  vow[-1], hgh[1],  low[-1], frt[0],  bck[0]), # rnd[-1]), # engma
    "r": (son[1],  cnt[1],  hgh[0],  frt[0], low[0],  bck[0]), # rnd[-1]), # RELEVANT
    # "l": (cns[1],  son[1],  cor[1],  nas[-1], cnt[1],  voi[1],  vow[-1], hgh[0],  low[0],  frt[0],  bck[0]), # rnd[-1]),
    # "w": (cns[-1], son[1],  cor[-1], nas[-1], cnt[1],  voi[1],  vow[-1], hgh[1],  low[-1], frt[-1], bck[1]), # rnd[1]),
    # "j": (cns[-1], son[1],  cor[-1], nas[-1], cnt[1],  voi[1],  vow[-1], hgh[1],  low[-1], frt[1], bck[-1]), # rnd[-1]), # y
    "i": (son[0],  cnt[0],  hgh[1],  frt[1],  low[-1], bck[-1]), # rnd[-1]), # RELEVANT
    "u": (son[0],  cnt[0],  hgh[1],  frt[-1], low[-1], bck[1]), # rnd[1]),  # RELEVANT
    "e": (son[0],  cnt[0],  hgh[-1], frt[1],  low[-1], bck[-1]), # rnd[-1]), # RELEVANT
    "o": (son[0],  cnt[0],  hgh[-1], frt[-1], low[-1], bck[1]), # rnd[1]),  # RELEVANT
    "a": (son[0],  cnt[0],  hgh[-1], frt[-1], low[1],  bck[-1]), # rnd[-1]), # RELEVANT
}

##########
# OUTPUT #
##########

# Max suffix VVC CVVC
n_sufphon = 7
# Arbitrarily take length of first feature matrix (all equal) to determine number of features
n_feat = len(phon_to_feat.values()[0])
# Tuple of 0 length of features for "-"
phon_to_feat["-"] = (0.0,) * n_feat

# Get number of output nodes
output_nodes = n_sufphon*n_feat

# Invert dictionary
feat_to_phon = functions.invert(phon_to_feat)