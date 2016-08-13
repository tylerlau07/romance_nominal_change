# -*- coding: utf-8 -*-
# Author: Tyler Lau

from math import log
from decimal import *
from random import shuffle

import codecs

import constants
import functions

class Lemma:
    '''
    Class for each Latin lemma.
    - Initialized with information from the Latin corpus
    - Contains a list of Case objects, one for each of its cases
    - Contains frequency, taken from the log of the total frequency
    '''
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

        # Now simplify gender by ridding of human part
        self.orig_gender = self.gender
        self.gender = self.gender[0]

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

    def realign(self, case_dict):
        '''
        Take the case dictionary, which has the string form of the word
        Phonemicize and realign the word such that roots line up
        '''
        replaced = map(functions.replace, case_dict.values())
        syllabified = map(functions.syllabify, replaced)
        CtoO = map(functions.codaToOnset, syllabified)
        dashes = map(functions.addDashes, CtoO)

        final_forms = []

        # List of lengths and max
        lengths = []
        len_list = map(len, dashes)

        max_len = max(len_list)
        # Check if all elements equal. If they are, build one forward
        len_equal = functions.checkEqual(len_list)

        for form in dashes:
            # Determine form length 
            form_len = len(form)
            # Length difference tells us how many to build forward
            len_diff = max_len - form_len
            # Difference from 6 tells us how many to build back
            diff_from_six = 6 - max_len

            # Now build
            if len_equal:
                final_form = ['-'*8]*(diff_from_six-1) + form + ['-'*8]
            else:
                final_form = ['-'*8]*diff_from_six + form + ['-'*8]*len_diff

            # Sanity check
            if len(final_form) != 6:
                print 'The word is misaligned'
                raise SystemExit
            else:
                final_forms.append(final_form)

        return dict(zip(case_dict.keys(), final_forms))

class Case:
    '''
    Class for each case of a token
    - Initialized from the Latin corpus
    - Contains a pointer to its parent Lemma object
    - Once its syllables have been set it will manipulate them depending on the generation
    and construct its own input tuple.
    '''
    def __init__(self, parent_lemma, **kwargs):
        self.parent = parent_lemma

        for key, value in kwargs.iteritems():
            setattr(self, key, value)

        # Convert N/A and NULL into nothing
        if self.root == 'N/A': self.root = u''
        else: self.root = self.root

        if self.suffix in ['N/A', 'NULL']: self.suffix = u''
        else: self.suffix = self.suffix

        # Split case and number
        splitpoint = self.casenum.index('.')
        self.case = self.casenum[:splitpoint]
        self.num = self.casenum[splitpoint+1:]

        # Unique identifying form
        self.lemmacase = self.parent.latin + ':' + self.case + '.' + self.num

        # Keep track of output change (suffix) and input change (phonology) for each generation
        self.output_change = {}
        self.input_phon = {}

    def createInputTuple(self, input_nodes, root_size):
        '''Create the input tuple off the phonology, human value, declension, gender, case, number'''
        
        # Convert phonemes into binary features
        self.rootbin = tuple(map(int, bin(self.parent.rootid)[2:].zfill(root_size)))
        self.humanbin = constants.human_dict[self.parent.human]
        self.decbin = constants.dec_dict[self.parent.declension]
        self.genbin = constants.gen_dict[self.parent.gender]
        if constants.casenum_sep == True:
            self.casebin = constants.case_dict[self.case]
            self.numbin = constants.num_dict[self.num]
        else:
            self.casebin = constants.case_dict[self.casenum]

        input_tuple = self.rootbin + self.humanbin + self.decbin + self.genbin + self.casebin
        if constants.casenum_sep == True:
            input_tuple += self.numbin

        # Sanity check
        if len(input_tuple) != input_nodes:
            print "You screwed up the size of the input"
            print len(input_tuple), input_nodes
            raise SystemExit

        else: self.input_tuple = input_tuple

###

def readCorpus(f):
    '''Reads the corpus file and creates the Lemma and Case objects'''
    corpus = []
    suffixes = []

    reader = codecs.open(f, encoding = 'utf-8', mode = 'rU')

    # Headings: Latin, English, Declension, Gender, TotFreq, ProseFreq, PoetFreq
    heading = reader.readline().strip('\n').lower().split("\t")[1:]

    # For each specific case form
    form_info = ['form', 'casenum', 'root', 'suffix', 'phonsuf', 'lasttwo']

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

                # Gather suffixes into list of suffixes
                suffix = case_dict['suffix']
                if suffix in ['N/A', 'NULL']: suffix = ''
                if suffix not in suffixes:
                    suffixes.append(suffix)

                # Remove cases that are not in simulation
                if case_dict['casenum'] not in constants.case_freqs.keys():
                    continue

                # Create Case object and add
                case_info = Case(lemma, **case_dict)
                lemma.addCase(case_dict['casenum'], case_info)

    return corpus, suffixes

###
class Corpus:
    ''' 
    Class to preprocess data for the neural network
    - Contains a training set ("corpus", entries appear by frequency) and a test set (unique entries)
    - Passes words (Case instances) and their current gender, adds them to the sets in appropriate proportion.
    '''
    def __init__(self, training_set):
        self.train = []
        self.test = []
        self.training_set = training_set

    def addByFreq(self, token_freq, token, expected_output):
        '''Adds the current token object to the list training set a number of times based off frequency.'''

        # Multiply log of token frequency by type frequency and then floor
        if token_freq == True:
            frequency = log(float(token.parent.totfreq), 10)
        else:
            frequency = 1

        frequency *= constants.case_freqs[token.case + '.' + token.num]
        frequency = int(frequency)

        # Add one of each form to test set and add by frequency to training set
        self.test.append((token, token.input_tuple, expected_output))                        
        for x in xrange(frequency):
            self.train.append((token, token.input_tuple, expected_output))

    def constructTrainingSet(self):
        '''Add each token to the actual training set in a random order to be passed to the neural net.'''
        shuffle(self.train)

        for token in self.train:
            (form, form.input_tuple, expected_output) = token
            self.training_set.addSample(form.input_tuple, expected_output)

        return self.training_set