from __future__ import division
from math import log
from decimal import *
import random
import constants

###
# Class for each Latin lemma.
# - Initialized with information from the Latin corpus
# - Contains a list of Case objects, one for each of its cases
# - Contains frequency, taken from the logged max frequency (or log 2 if frequency = 0 or 1), as well as Latin, Slavic, and Romanian genders
###
class Lemma:
    def __init__(self, *args, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)

        # Modify humanness, gender, and frequency
        if self.latin_gender[-1] == "h":
            self.human = "h"
        else: 
            self.human = ""

        self.latin_gender = self.latin_gender[0]

        if self.log_max not in ["?", "1"]:
            self.freq = Decimal(self.log_max)
        else:
            self.freq = Decimal(log(2))

        # Initialize dictionary to store info for each case
        self.cases = {}

    def addCase(self, case, case_info):
        '''Adds the case information'''
        self.cases[case] = case_info


###
# Class for each case of a token
# - Initialized from the Latin corpus
# - Contains a pointer to its parent Lemma object
# - Once its syllables have been set it will manipulate them depending on the generation
#   and construct its own input tuple.
# - Will ideally implement sanity checks
###
class Case:
    def __init__(self, parent_lemma, syllables, case):
        self.parent_lemma = parent_lemma
        self.syllables = syllables
        self.phonology = ''.join(syllables).replace('-', '')
        self.case = case[0:3]
        self.num = case[3:]
        self.lemmacase = self.parent_lemma.word + ':' + self.case + self.num

        # Keep track of input and expected outputs for each generation
        self.input_change = {}      # Should have generation mapping to case, num, and syllables
        self.output_change = {}     # Should have generation mapping to gender, declension, case, and number

    def createInputTuple(self, syllables):
        self.input_tuple = tuple([syllable for word in map(constants.convertToFeatures, syllables) for syllable in word])

        # Add tuple for animacy
        self.input_tuple += constants.input_human[self.parent_lemma.latin_gender + self.parent_lemma.human]

        self.sanityCheck(self.input_tuple)

    def sanityCheck(self, input_tuple):
        if len(self.input_tuple) != constants.input_nodes:
            print "You screwed up the size of the input"
            print len(self.input_tuple), constants.input_nodes
            raise SystemExit

###
# Class to preprocess data for the neural network
# - Contains a training set ("corpus", entries appear by frequency) and a test set (unique entries)
# - Passes- words (Case instances) and their current gender, adds them to the sets in appropriate proportion.
###
class Corpus:
    def __init__(self, training_set):
        self.train = []
        self.test = []
        self.training_set = training_set

    def addByFreq(self, token_freq, token, expected_output):
        '''Adds the current token to the list training set a number of times based off frequency.'''
        if token_freq == True:
            frequency = float(token.parent_lemma.freq)
            frequency *= constants.nhuman_case_freq[token.case+token.num]
        else:
            frequency = 1
            # Multiply by non-human constants. If token frequency turned off, multiply by human constants
            if token.parent_lemma.human == "h":
                frequency *= constants.human_case_freq[token.case+token.num]
            else:
                frequency *= constants.nhuman_case_freq[token.case+token.num]

        frequency = int(frequency)

        # Add one of each form to the test set and add by frequency to the training set
        self.test.append((token, token.input_tuple, expected_output))                        
        for x in xrange(frequency):
            self.train.append((token, token.input_tuple, expected_output))

    def constructTrainingSet(self):
        '''Add each token to the actual training set in a random order to be passed to the neural net.'''
        random.shuffle(self.train)

        for token in self.train:
            (form, form.input_tuple, expected_output) = token
            self.training_set.addSample(form.input_tuple, expected_output)

        return self.training_set

def readCorpus(f = constants.corpus_file):
        ''' Reads the corpus file and creates the Lemma and Case objects. '''
        corpus = []

        reader = open(f, 'rU')

        for row in reader.readlines():
                # If this is the start of a new word
                if row[0] == "_":

                        # Ignore "_"
                        row_arr = row.strip('\n').split("\t")[1:]

                        # Create dictionary of labels to values
                        row_dict = {constants.row_order[i]: value for i, value in enumerate(row_arr)}

                        # Create Lemma object and add it as a word in the corpus
                        current_lemma = Lemma(**row_dict)

                        # REMOVE THIS LINE ONCE WE MAKE THE CORPUS ONLY WORDS WITH LATIN GENDER
                        if current_lemma.latin_gender != "N":        
                                corpus.append(current_lemma)

                # Else, it is information for the word, and we can create a Case object pointing to the parent Lemma
                else:
                        [s1, s2, s3, s4, s5, s6, case, suf, dem, adj] = row.split("\t")
                        syllables = (s1, s2, s3, s4, s5, s6)
                        current_lemma.addCase(case, Case(current_lemma, syllables, case))

        return corpus