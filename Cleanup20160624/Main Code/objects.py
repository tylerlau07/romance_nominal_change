from math import log
from decimal import *
import re
import random
import constants

###
# Class for each Latin lemma.
# - Initialized with information from the Latin corpus
# - Contains a list of Case objects, one for each of its cases
# - Contains frequency, taken from the log of the total frequency
###

class Lemma:
    def __init__(self, *args, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)

        # Some nouns have more than one gender
        if ',' in self.gender:
            self.gender = self.gender[:self.gender.index(',')]

        # Modify humanness, gender, and frequency
        if self.gender[-1] == "h":
            self.human = self.gender
        else: 
            self.human = "nh"

        # Now simplify gender
        self.gender = self.gender[0]

        # Get rid of human part
        self.latin = self.latin[0]

        # Log frequency to account for Weber's Rule
        self.logfreq = Decimal(log(float(self.totfreq)))

        # Initialize dictionary to store info for each case
        self.cases = {}

    def addCase(self, case, case_info):
        '''
        Adds the case information
        Case info should be a Case object
        '''
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
    def __init__(self, parent_lemma, **kwargs):
        self.parent = parent_lemma

        for key, value in kwargs.iteritems():
            setattr(self, key, value)

        self.syllables = self.form.split(' ')
        self.phonology = ''.join(self.syllables).replace('-', '')

        # Split case and number
        splitpoint = re.search('[SP]', self.casenum).start()
        self.case = self.casenum[:splitpoint]
        self.num = self.casenum[splitpoint:]

        # Unique identifying form
        self.lemmacase = self.parent.latin + ':' + self.case + self.num

        # Keep track of output change for each generation (phonology)
        self.output_change = {}

    def createInputTuple(self):
        '''Create the input tuple off the root identifier, human value, declension, gender, case, number'''
        
        # Turn identifier into binary
        self.rootbin = tuple(bin(self.parent.rootid)[2:].zfill(constants.root_size))
        self.humanbin = constants.human_dict[self.parent.human]
        self.decbin = constants.dec_dict[self.parent.declension]
        self.genbin = constants.gen_dict[self.parent.gender]
        self.casebin = constants.case_dict[self.case]
        self.numbin = constants.num_dict[self.num]

        self.input_tuple = self.phonology, self.rootbin + self.humanbin + self.decbin + self.genbin + self.casebin + self.numbin

        # Sanity check
        if len(self.input_tuple) != constants.input_nodes:
            print "You screwed up the size of the input"
            print len(self.input_tuple), constants.input_nodes
            raise SystemExit

    # def createInputTuple(self, syllables):
    #     self.input_tuple = tuple([syllable for word in map(constants.convertToFeatures, syllables) for syllable in word])

    #     # Add tuple for animacy
    #     self.input_tuple += constants.input_human[self.parent_lemma.latin_gender + self.parent_lemma.human]

    #     self.sanityCheck(self.input_tuple)

    # def sanityCheck(self, input_tuple):
    #     if len(self.input_tuple) != constants.input_nodes:
    #         print "You screwed up the size of the input"
    #         print len(self.input_tuple), constants.input_nodes
    #         raise SystemExit

###
# Class to preprocess data for the neural network
# - Contains a training set ("corpus", entries appear by frequency) and a test set (unique entries)
# - Passes words (Case instances) and their current gender, adds them to the sets in appropriate proportion.
###
class Corpus:
    def __init__(self, training_set):
        self.train = []
        self.test = []
        self.training_set = training_set

    def addByFreq(self, token_freq, token, expected_output):
        '''Adds the current token to the list training set a number of times based off frequency.'''
        
        # Multiply token frequency (or 1) by type frequency and then floor
        if token_freq == True:
            frequency = float(token.parent.totfreq)
        else:
            frequency = 1
        
        frequency *= constants.case_freqs[token.case + token.num]
        frequency = int(frequency)

        # Add one of each form to test set and add by frequency to training set
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
        '''Reads the corpus file and creates the Lemma and Case objects'''
        corpus = []

        reader = open(f, 'rU')

        # Headings: Latin, English, Declension, Gender, TotFreq, ProseFreq, PoetFreq
        heading = reader.readline().strip('\n').lower().split("\t")[1:]

        # For each specific case form
        form_info = ['form', 'casenum', 'root', 'suffix']

        # Create counter to assign each lemma a unique identifying number
        root_counter = 0

        for row in reader.readlines():
                # If this is the start of a new word
                if row[0] == "_":

                    # Ignore "_"
                    row_arr = row.strip('\n').split('\t')[1:]

                    # Create dictionary of labels to values
                    row_dict = {heading[i]: value for i, value in enumerate(row_arr)}

                    # Create Lemma object and add it as a word in the corpus
                    lemma = Lemma(**row_dict)

                    # Add counter identifier to attributes and then increase counter
                    lemma.rootid = root_counter

                    root_counter += 1

                    # Corpus with each lemma and their case form information
                    corpus.append(lemma)

                # Else, it is information for the word, and we can create a Case object pointing to the parent Lemma
                else:

                    # Set up the keys
                    case_row = row.strip('\n').split('\t')

                    # Key and attributes to feed into Case object
                    case_dict = {form_info[i]: value for i, value in enumerate(case_row)}

                    # Create Case object and add
                    case_info = Case(lemma, **case_dict)
                    lemma.addCase(case_dict['casenum'], case_info)

        return corpus

print readCorpus()[10].cases['NomSg'].createInputTuple()
print constants.input_nodes