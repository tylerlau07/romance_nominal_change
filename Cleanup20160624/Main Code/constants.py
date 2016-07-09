from math import log
from math import ceil

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

# Generation to drop the genitive: set above total_generations if no genitive drop
gnvdrop_generation = 16  

# Are cases equidistant or is distance determined by semantics?
hierarchy = False                             

# Make false to test with no token frequency
token_freq = False

# Number of times to introduce training set: P&VE uses 3, HareEllman uses 10
epochs = 3

#############
# Functions #
#############

def binaryDict(category):
    '''Create dictionary of each item to binary'''
    # Pad with 0's up to size (log base 2 of number of items)
    fill_size = int(ceil(log(len(category), 2)))
    bin_list = [tuple(bin(num)[2:].zfill(fill_size)) for num in range(0, len(category))]
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
#   1) Unique identifier of root (9 bits)
#   2) Human identifier (male, female, non-human) (2 bits)
#   3) Declension, Gender?, Case, Number (3 bits, 2 bits, 3 bits, 1 bit)
# TOTAL input bits = 20

# We know the corpus size beforehand
corpus_size = 500

# Take log base 2 to figure out how many bits we need (9)
root_size = int(ceil(log(corpus_size, 2)))

human = ['nh', 'mh', 'fh']
declensions = [str(i) for i in range(1, 6)]
genders = ['m', 'f', 'n']
cases = ['Nom', 'Acc', 'Gen', 'Dat', 'Abl', 'Voc']
numbers = ['Sg', 'Pl']

# Total size of input layer
input_nodes = sum([root_size, len(human), len(declensions), len(genders), len(cases), len(numbers)])

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
hidden_nodes = 30

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
case_freqs = {
    'NomSg': 129.23, 'NomPl': 41.94,
    'AccSg': 159.68, 'AccPl': 85.27,
    'GenSg': 75.41, 'GenPl': 41.96,
    'DatSg': 28.96, 'DatPl': 16.41,
    'AblSg': 135.64, 'AblPl': 49.74,
    'VocSg': 1.88, 'VocPl': 1
}

#############################################
# Organize data to make it easier to handle #
#############################################

# Map phonemes to Chomsky and Halle values (1968) --> need to update 
phonemes = {
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

# Turn a syllable into its featural representation
# Takes a six tuple--a syllable with six phonemes
def convertToFeatures(syllable):
    ''' Turn a syllable (six tuple of phonemes) into its featural representation. '''
    feature_matrix = [phonemes[phoneme] for phoneme in syllable]
    # Flatten
    return tuple(feature for phoneme in feature_matrix for feature in phoneme)