from math import log
from math import ceil

##########
# Corpus #
##########

corpus_file = "../Corpus Preparation/latin_toy.txt"

##############
# Parameters #
##############

# Trial number
trial = 1

# Generations to run simulation
total_generations = 2

# Generation to drop the genitive: set above total_generations if no genitive drop
gnvdrop_generation = 16  

# Are cases equidistant or is distance determined by semantics?
hierarchy = False                             

# Make false to test with no token frequency
token_freq = True

# Number of times to introduce training set: P&VE uses 3, HareEllman uses 10
epochs = 10

#############
# Functions #
#############

def binaryDict(category):
    '''Create dictionary of each item to binary'''
    # Pad with 0's up to size (log base 2 of number of items)
    fill_size = int(ceil(log(len(category), 2)))
    bin_list = [tuple(map(int, bin(num)[2:].zfill(fill_size))) for num in range(len(category))]
    return dict(zip(category, bin_list))

def invert(d):
    '''
    Invert a dictionary
    '''
    return dict((value, key) for key, value in d.iteritems())

#####################
# Layer Information #
#####################

#########
# INPUT #
#########

# Input layer will contain:
#   1) Unique identifier of root (9 bits IF 500)
#   2) Human identifier (male, female, non-human) (2 bits)
#   3) Declension, Gender?, Case, Number (3 bits, 2 bits, 3 bits, 1 bit)
# TOTAL input bits = 20

human = ['nh', 'mh', 'fh']
declensions = [str(i) for i in range(1, 6)]
genders = ['m', 'f', 'n']
# cases = ['Nom', 'Acc', 'Gen', 'Dat', 'Abl', 'Voc']
cases = ['Nom', 'Acc', 'Gen', 'Dat', 'Abl']
numbers = ['Sg', 'Pl']

# Take log base 2 to figure out how many bits we need for each
human_size = int(ceil(log(len(human), 2))) # 2
dec_size = int(ceil(log(len(declensions), 2))) # 3
gen_size = int(ceil(log(len(genders), 2))) # 2
case_size = int(ceil(log(len(cases), 2))) # 3
num_size = int(ceil(log(len(numbers), 2))) # 1

# Now make two way dictionary with bit vectors
human_dict = binaryDict(human)
dec_dict = binaryDict(declensions)
dec_dict.update(invert(dec_dict))
gen_dict = binaryDict(genders)
gen_dict.update(invert(gen_dict))
case_dict = binaryDict(cases)
case_dict.update(invert(case_dict))
num_dict = binaryDict(numbers)
num_dict.update(invert(num_dict))

##########
# HIDDEN #
##########

# Number of hidden layers: P&VE uses 30, HareEllman uses 10 for the first layer
# P&VE suggest 60
hidden_nodes = 295

##########
# OUTPUT #
##########

# Output layer will be phonological form
#   Compute by multiplying syllables (6) by max phonemes per syllable (8) by features (12) 
#   Features from (Chomsky & Halle 1968): see below
n_syll = 6
n_phon = 8
n_feat = 12

# Determine the length of the input
output_nodes = n_syll * n_phon * n_feat

##########################
# Coding the output file #
##########################

# Number of generations
out_file = 'stats_Gens%s' % str(total_generations)

# Do we drop the genitive or not?
if token_freq == False:
    out_file += '_TokFreqF'
if gnvdrop_generation <= total_generations:
    out_file += '_GnvT%s' % str(gnvdrop_generation)

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
    "N": (1.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0),    # engma
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

feat_to_phon = invert(phon_to_feat)