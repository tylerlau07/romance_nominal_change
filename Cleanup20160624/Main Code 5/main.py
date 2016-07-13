# Standard Library Imports
from math import ceil
from math import log
import time
import unicodecsv as csv
from random import seed

# Our files
import constants

print '''-----------------------------
Trial %d:
''' % constants.trial

import objects
from smooth import chunks
from smooth import smooth

# Pybrain package dependencies
from pybrain.tools.shortcuts import buildNetwork
from pybrain.datasets import SupervisedDataSet
from pybrain.supervised.trainers import BackpropTrainer

# Track time from start to finish
start = time.time()

# Initialize generation counter
generation = 1

seed(0)

def conductGeneration(generation, corpus, previous_output):
        '''
        Conducts a generation of learning and testing on the input data

        Inputs
                generation (int) --- the number of the generation
                corpus (array) --- the lemmas and their info from reading the corpus file
                previous_output (dict) --- the output phonology of the previous generation
        Returns the output of the current generation--the expected outputs for the following generation
        '''

        # Determine how long the root vector should be based on the length of the corpus
        root_size = len(root_to_tuple)

        # Total size of input layer determined here
        input_nodes = sum([root_size, constants.human_size, constants.dec_size, constants.gen_size, constants.case_size, constants.num_size])

        # Build the right size network
        net = buildNetwork(input_nodes, constants.hidden_nodes, constants.output_nodes)

        # Build the right size training set
        emptytraining_set = SupervisedDataSet(input_nodes, constants.output_nodes)

        # Initialize corpus object and expected output dictionary
        training_corpus = objects.Corpus(emptytraining_set)

        # Iterate through tokens and convert to binary
        for lemma in corpus:

                # Iterate through cases
                for case, form in lemma.cases.iteritems():

                        # Create the input tuple
                        form.createInputTuple(input_nodes, root_to_tuple)

                        # Add words according to their frequencies
                        training_corpus.addByFreq(constants.token_freq, form, expected_outputs[form.lemmacase])

        # Print information
        print "--------Generation %s--------" % generation
        # if generation >= constants.gnvdrop_generation:
        #         print "Genitive Case Dropped"

        # Construct the training set
        print "Constructing the training set"
        training_set = training_corpus.constructTrainingSet()

        # Construct the trainer
        trainer = BackpropTrainer(net, training_set)

        # Train
        print "Training the model"
        
        error = trainer.trainEpochs(constants.epochs)
        
        print "Number of Tokens in Training Set: %s" % len(training_set)
        print "Training Error: %s" % error

        results = {}

        # For each word in the test set, calculate output tuple
        print "Running the test set"
        for (form, input_tuple, expected_output) in training_corpus.test:             

                # # Determine if we should drop the genitive
                drop_gen = generation >= constants.gnvdrop_generation

                # Activate the net, and smooth the output
                result = smooth(tuple(net.activate(input_tuple)), gendrop=drop_gen, hierarchy=constants.hierarchy)  

                # Append output tuple to result
                results[form.lemmacase] = result

                # Hash the output tuple to get the phonological form result
                new_phonology = ''
                # Divide tuple into chunks (each 12 units, representing one phoneme)
                chunked_list = list(chunks(list(result), 12))
                for phoneme in chunked_list:
                        new_phonology += constants.feat_to_phon[tuple(phoneme)]

                print form.parent.rootid, form.lemmacase, new_phonology

                # Set input change once we figure out how to deal with the phonology
                form.output_change[generation] = new_phonology.replace('-', '')

        print "Results have been determined"

        return results

########
# MAIN #
########

print '''Training on %d Epochs
        Token Frequency taken into account: %s
        Case Hierarchy taken into account: %s
        Genitive Case to be dropped: %s \n''' % ( 
                constants.epochs, 
                constants.token_freq, 
                constants.hierarchy, 
                constants.gnvdrop_generation < constants.total_generations
                )

# Read in corpus
(corpus, root_to_tuple) = objects.readCorpus(constants.corpus_file)
# Determine corpus size from this
corpus_size = len(corpus)

# Initialize dictionary mapping from forms to Latin noun info, to be updated each generation
expected_outputs = {}

# Iterate over tokens
for lemma in corpus:
        # Iterate over cases
        for case, form in lemma.cases.iteritems():
                # Take Latin phonology as first set of expected outputs
                word = ''.join(form.syllables)
                
                expected_output = ()
                for phoneme in word:
                        expected_output += objects.convertToFeatures(phoneme)
                expected_outputs[form.lemmacase] = expected_output

                # Keep track of output change per generation
                form.output_change[0] = word.replace('-', '')

# For each generation to conduct
while generation <= constants.total_generations:
        # Conduct the generation
        expected_outputs = conductGeneration(generation, corpus, expected_outputs)
        # Increment the generation counter
        generation += 1

# Write output to stats
with open(constants.out_file, mode = 'wb') as f:
        stats = csv.writer(f, delimiter = '\t')
        stats.writerow(['Declined Noun'] + range(0, constants.total_generations))

        # for generation in range(0, constants.total_generations+1):
        #         stats.write('\t' + str(generation))

        for lemma in corpus:
                for case, form in lemma.cases.iteritems():
                        to_write = []
                        for generation in sorted(form.output_change.keys()):
                                to_write.append(form.output_change[generation])
 
                        stats.writerow(to_write)

# End time count
end = time.time()
print '\nTime taken to run simulation: %f' % (end - start)
