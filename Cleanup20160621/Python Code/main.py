# Standard Library Imports
from decimal import *
from collections import defaultdict
import time
import csv

# Our files
import constants

print '''-----------------------------
Trial %d:
''' % constants.trial

import objects
from objects import readCorpus
from smooth import smooth

# Pybrain package dependencies
from pybrain.tools.shortcuts import buildNetwork
from pybrain.datasets import SupervisedDataSet
from pybrain.supervised.trainers import BackpropTrainer

# Track time from start to finish
start = time.time()

# Initialize generation counter
generation = 1

def conductGeneration(generation, corpus, previous_output):
        '''
        Conducts a generation of learning and testing on the input data

        inputs
                generation (int) --- the number of the generation
                corpus (array) --- the lemmas and their info from reading the corpus file
                previous_output (dict) --- the output (gender, declension, case, number) of the previous generation
        Returns the output of the current generation--the expected outputs for the following generation

        '''

        # Build the right size network
        net = buildNetwork(constants.input_nodes, constants.hidden_nodes, constants.output_nodes)

        # Build the right size training set
        emptytraining_set = SupervisedDataSet(constants.input_nodes, constants.output_nodes)

        # Initialize corpus object and expected output dictionary
        training_corpus = objects.Corpus(emptytraining_set)

        # Iterate through tokens and convert to binary
        for lemma in corpus:
                # JUST SKIP THOSE THAT ARE DEFECTIVE
                if len(lemma.cases.keys()) < 6:
                        continue

                # Iterate through cases
                for case, form in lemma.cases.iteritems():
                        # Get new input from previous output
                        new_gender, new_dec, new_case, new_num, prev_output = form.output_change[generation - 1]

                        # Use new input as new syllables
                        new_syllables = lemma.cases[new_case+new_num].syllables

                        # Append to input change
                        form.input_change[generation] = (new_case+new_num, ''.join(new_syllables).replace('-', ''))

                        # print form.lemmacase, form.input_change[generation]

                        # Create the input tuple
                        form.createInputTuple(new_syllables)

                        # Add words according to their frequencies
                        training_corpus.addByFreq(constants.token_freq, form, expected_outputs[form.lemmacase])

        # Print information
        print "--------Generation %s--------" % generation
        if generation >= constants.gnvdrop_generation:
                print "Genitive Case Dropped"

        # Construct the training set
        print "Constructing the training set"
        training_set = training_corpus.constructTrainingSet()

        # Construct the trainer
        trainer = BackpropTrainer(net, training_set)

        # Train
        print "Training the model"
        if constants.epochs == 1:
                error = trainer.train()
        else:
                error = trainer.trainEpochs(constants.epochs)
        print "Number of Tokens in Training Set: %s" % len(training_set)
        print "Training Error: %s" % error

        results = {}

        # For each word in the test set
        print "Running the test set"
        for (form, input_tuple, expected_output) in training_corpus.test:                 

                # Determine if we should drop the genitive
                drop_gen = generation >= constants.gnvdrop_generation

                # Activate the net, and smooth the output
                result = smooth(tuple(net.activate(input_tuple)), gendrop=drop_gen, hierarchy=constants.hierarchy)  

                # Append output tuple to result
                results[form.lemmacase] = result

                # Hash the output tuple to get the result
                gender = constants.tup_to_gen[tuple(result[constants.gen_b:constants.dec_b])]
                dec = constants.tup_to_dec[tuple(result[constants.dec_b:constants.case_b])]
                case = constants.tup_to_case[tuple(result[constants.case_b:constants.num_b])]
                num = constants.tup_to_num[tuple(result[constants.num_b:])]
                output = form.parent_lemma.cases[case+num].phonology

                # Set input change once we figure out how to deal with the phonology
                form.output_change[generation] = (gender, dec, case, num, output)

        print "Results have been determined"

        return results

########
# MAIN #
########

# Read in corpus
corpus = readCorpus(constants.corpus_file)

print '''Training on %d Epochs
        Token Frequency taken into account: %s
        Case Hierarchy taken into account: %s
        Genitive Case to be dropped: %s \n''' % ( 
                constants.epochs, 
                constants.token_freq, 
                constants.hierarchy, 
                constants.gnvdrop_generation < constants.total_generations
                )

# Initialize dictionary mapping from forms to Latin noun info, to be updated each generation
expected_outputs = {}

# Iterate over tokens
for lemma in corpus:
        # Iterate over cases
        for case, form in lemma.cases.iteritems():
                # Take Latin outputs as first set of expected outputs
                expected_outputs[form.lemmacase] = (
                        constants.outputs[form.parent_lemma.latin_gender] + 
                        constants.outputs[form.parent_lemma.declension] + 
                        constants.outputs[form.case] + 
                        constants.outputs[form.num]
                )
                # Keep track of input phonological change per generation
                form.input_change[0] = "N/A"
                # Keep track of output change per generation
                form.output_change[0] = (form.parent_lemma.latin_gender, 
                        form.parent_lemma.declension, 
                        form.case, 
                        form.num,
                        form.phonology)

# For each generation to conduct
while generation <= constants.total_generations:
        # Conduct the generation
        expected_outputs = conductGeneration(generation, corpus, expected_outputs)
        # Increment the generation counter
        generation += 1

# Write output to stats
with open(constants.out_file, mode = 'wb') as f:
        stats = csv.writer(f, delimiter = '\t')
        stats.writerow(['Declined Noun'] + range(0, constants.total_generations+1))

        # for generation in range(0, constants.total_generations+1):
        #         stats.write('\t' + str(generation))

        for lemma in corpus:
                if len(lemma.cases.keys()) < 6:
                        continue
                for case, form in lemma.cases.iteritems():
                        to_write = [form.lemmacase]
                        for generation in sorted(form.output_change.keys()):
                                to_write.append(",".join(form.output_change[generation]))
 
                        stats.writerow(to_write)

# End time count
end = time.time()
print '\nTime taken to run simulation: %f' % (end - start)
