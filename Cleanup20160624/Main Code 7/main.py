# -*- coding: utf-8 -*-
# Author: Tyler Lau
# Main Code 7

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

        Inputs
                generation (int) --- the number of the generation
                corpus (array) --- the lemmas and their info from reading the corpus file
                previous_output (dict) --- the output phonology of the previous generation
        Returns the output of the current generation--the expected outputs for the following generation
        '''

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

                        # Add words according to their frequencies
                        training_corpus.addByFreq(constants.token_freq, form, previous_output[form.lemmacase])

        # Construct the training set
        print "--------Generation %s--------" % generation
        print "Constructing the training set"
        training_set = training_corpus.constructTrainingSet()

        # Construct the trainer
        trainer = BackpropTrainer(net, training_set)

        # Train
        print "Training the model"

        error = trainer.trainEpochs(constants.epochs)
        
        print "Number of Tokens in Training Set: %s" % len(training_set)

        results = {}

        # For each word in the test set, calculate output tuple
        print "Running the test set"

        # Counter to count correct
        ncorrect = 0
        tot_phon = 0

        for (form, input_tuple, expected_output) in training_corpus.test:

                # Activate the net, and smooth the output
                result = smooth(tuple(net.activate(input_tuple)))

                # Append output tuple to result
                results[form.lemmacase] = result

                # Hash the output tuple to get the phonological form result
                new_phonology = ''

                # Divide tuple into chunks (each 11 units, representing one phoneme)
                chunked_list = list(chunks(list(result), constants.n_feat))
                # Divide previous output tuple into chunks
                chunked_prev = list(chunks(list(previous_output[form.lemmacase]), constants.n_feat))

                for phon_index in range(len(chunked_list)):
                        phoneme = chunked_list[phon_index]
                        prev_phoneme = chunked_prev[phon_index]

                        new_phonology += constants.feat_to_phon[tuple(phoneme)]
                        # If phoneme matches, add to number correct
                        if prev_phoneme != [0.5]*constants.n_feat:
                                tot_phon += 1
                                if phoneme == prev_phoneme:
                                        ncorrect += 1

                # Output for this generation is new suffix
                new_suf = ''.join(new_phonology)
                for seq in functions.to_revert.keys():
                        if seq in new_suf:
                            new_suf = new_suf.replace(seq, functions.to_revert[seq])
                new_suf = new_suf.replace('-', '')

                form.output_change[generation] = new_suf

                print form.lemmacase, form.root+form.suffix, form.parent.declension, form.parent.gender, form.parent.totfreq, form.root+new_suf, new_suf

        print "Results have been determined"
        print "Percentage correct in test run: %f" % round(float(ncorrect)/float(tot_phon)*100, 2)

        return results

########
# MAIN #
########

# Read in corpus
(corpus, suffixes) = objects.readCorpus(constants.corpus_file)

# Determine corpus size from this
corpus_size = len(corpus)

root_size = int(ceil(log(corpus_size, 2)))

# # Create suffix dictionary
# if constants.vectors == 'binary':
#         suffix_size = int(ceil(log(len(suffixes), 2)))          # 6
#         suffix_dict = functions.binaryDict(suffixes)
# else:
#         suffix_size = len(suffixes)
#         suffix_dict = dict(zip(suffixes, map(tuple, identity(suffix_size))))

# suf_to_tup = functions.invert(suffix_dict)
# suffix_dict.update(functions.invert(suffix_dict))

# TOTAL input bits
#       If binary and casenum separate: 9 + 2 + 3 + 2 + 3 + 1 = 20
#       If binary and casenum together: 9 + 2 + 3 + 2 + 4 = 20
#       If identity and casenum separate: 9 + 3 + 5 + 3 + 5 + 2 = 27
#       If identity and casenum together: 9 + 3 + 5 + 3 + 10 = 30
input_nodes = sum([root_size, constants.human_size, constants.dec_size, constants.gen_size, constants.case_size])
if constants.casenum_sep == True:
        input_nodes += constants.num_size

##########
# OUTPUT #
##########

# # Output layer will be list of potential suffixes, gathered from corpus
# output_nodes = suffix_size

# Print information
print '''Training on %d Epochs
        Number of Input Nodes: %d
        Number of Hidden Nodes: %d
        Number of Output Nodes: %d
        Token Frequency taken into account: %s\n''' % ( 
                constants.epochs, 
                input_nodes,
                constants.hidden_nodes,
                constants.output_nodes,
                constants.token_freq,
                )

# Initialize dictionary mapping from forms to Latin noun info, to be updated each generation
expected_outputs = {}

# Iterate over tokens
for lemma in corpus:
        # Iterate over cases
        for case, form in lemma.cases.iteritems():
                # Create the input tuple, which is constant across generation
                form.createInputTuple(input_nodes, root_size)
                phon_suf = functions.reworkSuffix(form.suffix)

                # Convert phonemes to features
                suf_feat = ()
                for phoneme in ''.join(phon_suf):
                        suf_feat += constants.phon_to_feat[phoneme]

                expected_outputs[form.lemmacase] = suf_feat

                # Keep track of output change per generation
                # Revert to diphthongs and long vowels to print
                new_suf = ''.join(phon_suf)
                for seq in functions.to_revert.keys():
                        if seq in new_suf:
                            new_suf = new_suf.replace(seq, functions.to_revert[seq])
                new_suf = new_suf.replace('-', '')

                form.output_change[0] = new_suf

# For each generation to conduct
while generation <= constants.total_generations:
        # Conduct the generation
        expected_outputs = conductGeneration(generation, corpus, expected_outputs)
        # Increment the generation counter
        generation += 1
        # Print time it took for generation to finish
        print 'Time so far: %s' % functions.getTime(time.time() - start) 

# Write output to stats
with open(constants.out_file, mode = 'wb') as f:
        stats = csv.writer(f, delimiter = '\t')
        stats.writerow(['Word', 'Declension', 'Gender', 'Case', 'TotFreq', 'Declined'] + range(0, constants.total_generations+1))

        for lemma in corpus:
                for case, form in lemma.cases.iteritems():
                        to_write = [form.lemmacase, form.parent.declension, form.parent.orig_gender, form.casenum, form.parent.totfreq]
                        if form.suffix == 'NULL':
                                to_write.append(form.root)
                        else:
                                to_write.append(form.root + form.suffix)
                        for generation in sorted(form.output_change.keys()):
                                to_write.append(form.output_change[generation])
 
                        stats.writerow(to_write)

# End time count
end = time.time()
print '\nTime taken to run simulation: %s' % functions.getTime(end - start)
