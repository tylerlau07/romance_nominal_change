# Standard Library Imports
from math import ceil
from math import log
import time
import unicodecsv as csv

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

                        # Create the input tuple
                        form.createInputTuple(input_nodes, root_size)

                        # Add words according to their frequencies
                        training_corpus.addByFreq(constants.token_freq, form, previous_output[form.lemmacase])

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

        # Counter to count correct. Exclude -'s from total phonemes
        ncorrect = 0
        tot_phon = 0

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
                # Divide previous output tuple into chunks
                chunked_prev = list(chunks(list(previous_output[form.lemmacase]), 12))

                for phon_index in range(len(chunked_list)):
                        phoneme = chunked_list[phon_index]
                        prev_phoneme = chunked_prev[phon_index]

                        new_phonology += constants.feat_to_phon[tuple(phoneme)]
                        # If phoneme matches, add to number correct
                        if prev_phoneme != [0.5]*12:
                                tot_phon += 1
                                if phoneme == prev_phoneme: 
                                        ncorrect += 1

                print form.lemmacase, form.parent.declension, form.parent.gender, new_phonology

                # Set input change once we figure out how to deal with the phonology
                form.output_change[generation] = new_phonology.replace('-', '')

        print "Results have been determined"

        print "Percentage correct in test run: {:.2f}".format(float(ncorrect)/float(tot_phon)*100)

        return results

########
# MAIN #
########

# Read in corpus
corpus = objects.readCorpus(constants.corpus_file)
# Determine corpus size from this
corpus_size = len(corpus)

# Determine how long the root vector should be based on the length of the corpus
root_size = int(ceil(log(corpus_size, 2)))

# Total size of input layer determined here
input_nodes = sum([root_size, constants.human_size, constants.dec_size, constants.gen_size, constants.case_size, constants.num_size])

print '''Training on %d Epochs
        Number of Input Nodes: %d
        Number of Hidden Nodes: %d
        Number of Output Nodes: %d
        Token Frequency taken into account: %s
        Case Hierarchy taken into account: %s
        Genitive Case to be dropped: %s \n''' % ( 
                constants.epochs, 
                input_nodes,
                constants.hidden_nodes,
                constants.output_nodes,
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
        # Print time it took for generation to finish
        print 'Time so far: %s' % constants.getTime(time.time() - start) 

# Write output to stats
with open(constants.out_file, mode = 'wb') as f:
        stats = csv.writer(f, delimiter = '\t')
        stats.writerow(['Word', 'Declension', 'Gender', 'TotFreq', 'Declined'] + range(0, constants.total_generations+1))

        for lemma in corpus:
                for case, form in lemma.cases.iteritems():
                        to_write = [form.lemmacase, form.parent.declension, form.parent.gender, form.parent.totfreq]
                        if form.suffix == 'NULL':
                                to_write.append(form.root)
                        else:
                                to_write.append(form.root + form.suffix)
                        for generation in sorted(form.output_change.keys()):
                                to_write.append(form.output_change[generation])
 
                        stats.writerow(to_write)

# End time count
end = time.time()
print '\nTime taken to run simulation: %s' % constants.getTime(end - start)