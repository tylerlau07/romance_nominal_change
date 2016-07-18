# -*- coding: utf-8 -*-
# Main Code 5
# Author: Tyler Lau

# This code will take in as the input the root as binary, root phonology
# Human feature, declension, gender, case, number
# Output will map input to suffix, coded by feature tuple

# Standard Library Imports
from math import ceil
from math import log
from numpy import identity

import time
import unicodecsv as csv

# Our files
import constants

print '''-----------------------------
Trial %d:
''' % constants.trial

import objects
import functions

from smooth import chunks
from smooth import smooth

# Pybrain package dependencies
from pybrain.datasets                   import ClassificationDataSet
from pybrain.datasets                   import SupervisedDataSet
from pybrain.utilities                  import percentError
from pybrain.tools.shortcuts            import buildNetwork
from pybrain.supervised.trainers        import BackpropTrainer
from pybrain.structure.modules          import SoftmaxLayer

from scipy import diag
from numpy.random import multivariate_normal

# Track time from start to finish
start = time.time()

# Initialize generation counter
generation = 1

def conductGeneration(generation, corpus):
        '''
        Conducts a generation of learning and testing on the input data
                generation (int) --- the number of the generation
                corpus (object) --- corpus object containing info needed
        '''
        # Set up the dataset skeleton
        alldata = ClassificationDataSet(2, 1, nb_classes=3, class_labels=['a', 'b', 'c'])

        # means = [(-1,0),(2,4),(3,1)]
        # cov = [diag([1,1]), diag([0.5,1.2]), diag([1.5,0.7])]

        # alldata = ClassificationDataSet(2, 1, nb_classes=3)
        # for n in xrange(400):
        #     for klass in range(3):
        #         input = multivariate_normal(means[klass],cov[klass])
        #         print type(input)
        #         alldata.addSample(input, [klass])

        alldata.addSample((0, 1), (1))
        alldata.addSample((1, 0), (0))
        alldata.addSample((0, 0), (2))
        alldata.addSample((1, 1), (0))

        trndata, partdata = alldata.splitWithProportion(0.5)

        return alldata

        # print trndata
        # print partdata
        # trndata._convertToOneOfMany()

        # print trndata['class']

        # return alldata

        # Add samples  

print conductGeneration(1, 1)

#         '''
#         Conducts a generation of learning and testing on the input data

#         Inputs
#                 generation (int) --- the number of the generation
#                 corpus (array) --- the lemmas and their info from reading the corpus file
#                 previous_output (dict) --- the output phonology of the previous generation
#         Returns the output of the current generation--the expected outputs for the following generation
#         '''

#         # Build the right size network
#         net = buildNetwork(constants.input_nodes, constants.hidden_nodes, output_nodes)

#         # Build the right size training set
#         emptytraining_set = ClassificationDataSet(constants.input_nodes, output_nodes)

#         # Initialize corpus object and expected output dictionary
#         training_corpus = objects.Corpus(emptytraining_set)

#         # Iterate through tokens and convert to binary
#         for lemma in corpus:

#                 # Input phonologies in case dictionary and feed to realign function
#                 case_dict = {case: form.input_phon[generation] for case, form in lemma.cases.iteritems()}
#                 new_phon = lemma.realign(case_dict)

#                 # Iterate through cases
#                 for case, phonology in new_phon.iteritems():

#                         form = lemma.cases[case]

#                         # Create the input tuple
#                         form.createInputTuple(phonology, constants.input_nodes)

#                         # Add words according to their frequencies
#                         training_corpus.addByFreq(constants.token_freq, form, previous_output[form.lemmacase])

#         # Construct the training set
#         print "--------Generation %s--------" % generation
#         print "Constructing the training set"
#         training_set = training_corpus.constructTrainingSet()

#         # Construct the trainer
#         trainer = BackpropTrainer(net, training_set)

#         # Train
#         print "Training the model"

#         error = trainer.trainEpochs(constants.epochs)
        
#         print "Number of Tokens in Training Set: %s" % len(training_set)

#         results = {}

#         # For each word in the test set, calculate output tuple
#         print "Running the test set"

#         # Counter to count correct
#         ncorrect = 0

#         for (form, input_tuple, expected_output) in training_corpus.test:

#                 # Activate the net, and smooth the output
#                 result = smooth(tuple(net.activate(input_tuple)), suf_to_tup)

#                 # Append output tuple to result
#                 results[form.lemmacase] = result

#                 # Add to ncorrect if matches previous
#                 if result == previous_output[form.lemmacase]: ncorrect += 1

#                 # Hash the output tuple to get the suffix result
#                 new_suffix = suffix_dict[result]

#                 print form.lemmacase, form.root+form.suffix, form.parent.declension, form.parent.gender, form.parent.totfreq, form.root+new_suffix, new_suffix

#                 # Output for this generation and input for next
#                 # Combine new suffix with root to get new phonological form for next generation
#                 form.input_phon[generation+1] = form.root + new_suffix
#                 form.output_change[generation] = new_suffix

#         print "Results have been determined"
#         print "Percentage correct in test run: %f" % round(float(ncorrect)/float(len(previous_output))*100, 2)

#         return results

# ########
# # MAIN #
# ########

# # Read in corpus
# (corpus, suffixes) = objects.readCorpus(constants.corpus_file)
# # Determine corpus size from this
# corpus_size = len(corpus)

# # Create suffix dictionary
# if constants.vectors == 'binary':
#         suffix_size = int(ceil(log(len(suffixes), 2)))          # 6
#         suffix_dict = functions.binaryDict(suffixes)
# else:
#         suffix_size = len(suffixes)
#         suffix_dict = dict(zip(suffixes, map(tuple, identity(suffix_size))))

# suf_to_tup = functions.invert(suffix_dict)
# suffix_dict.update(functions.invert(suffix_dict))

# ##########
# # OUTPUT #
# ##########

# # Output layer will be list of potential suffixes, gathered from corpus
# output_nodes = suffix_size

# # Print information
# print '''Training on %d Epochs
#         Number of Input Nodes: %d
#         Number of Hidden Nodes: %d
#         Number of Output Nodes: %d
#         Token Frequency taken into account: %s\n''' % ( 
#                 constants.epochs, 
#                 constants.input_nodes,
#                 constants.hidden_nodes,
#                 output_nodes,
#                 constants.token_freq,
#                 )

# # Initialize dictionary mapping from forms to Latin noun info, to be updated each generation
# expected_outputs = {}

# # Iterate over tokens
# for lemma in corpus:
#         # Iterate over cases
#         for case, form in lemma.cases.iteritems():

#                 # Take suffix as first set of expected outputs
#                 expected_outputs[form.lemmacase] = suffix_dict[form.suffix]
#                 # print form.lemmacase, form.suffix, expected_outputs[form.lemmacase]

#                 # Keep track of input change and output change per generation
#                 form.input_phon[1] = form.root + form.suffix
#                 form.output_change[0] = form.suffix

# # For each generation to conduct
# while generation <= constants.total_generations:
#         # Conduct the generation
#         expected_outputs = conductGeneration(generation, corpus, expected_outputs)
#         # Increment the generation counter
#         generation += 1
#         # Print time it took for generation to finish
#         print 'Time so far: %s' % functions.getTime(time.time() - start) 

# # Write output to stats
# with open(constants.out_file, mode = 'wb') as f:
#         stats = csv.writer(f, delimiter = '\t')
#         stats.writerow(['Word', 'Declension', 'Gender', 'TotFreq', 'Declined'] + range(0, constants.total_generations+1))

#         for lemma in corpus:
#                 for case, form in lemma.cases.iteritems():
#                         to_write = [form.lemmacase, form.parent.declension, form.parent.gender, form.parent.totfreq]
#                         if form.suffix == 'NULL':
#                                 to_write.append(form.root)
#                         else:
#                                 to_write.append(form.root + form.suffix)
#                         for generation in sorted(form.output_change.keys()):
#                                 to_write.append(form.output_change[generation])
 
#                         stats.writerow(to_write)

# # End time count
# end = time.time()
# print '\nTime taken to run simulation: %s' % functions.getTime(end - start)
