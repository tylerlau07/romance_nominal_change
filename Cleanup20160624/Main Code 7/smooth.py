# -*- coding: utf-8 -*- 
# Author: Tyler Lau

import numpy
from constants import phon_to_feat

# Using numpy, determine the Euclidean distance between the vectors, float
def dist(p, q):
    '''Takes in the actual vector (determined by neural net) and determines distance from output vectors'''
    return numpy.linalg.norm(numpy.array(p) - numpy.array(q))

def chunks(l, n):
    '''
    Yield successive n-sized chunks from list.
    Apply list function to return list
    '''
    for i in range(0, len(l), n):
        yield l[i:i+n]

def smooth(p):
    '''
    Error smoothing function
    Takes the vector output by the neural network
    Takes dictionary that converts suffix to relevant tuple
    Converts those partitions to the closest phoneme vectors
    '''
    # Partition the input vector into individual phonemes
    chunked_list = list(chunks(p, 12))

    # Get list of phoneme tuples
    phoneme_tuples = phon_to_feat.values()

    output_tuple = ()

    # For potential phoneme in tuple, find closest phoneme to it using dictionary keying distance to phoneme
    for phoneme in chunked_list:
        dist_from_realphon = {dist(phoneme, phoneme_tuples[i]): phoneme_tuples[i] for i in range(len(phoneme_tuples))}
        smoothed_vector = min(dist_from_realphon.keys())
        output_tuple += dist_from_realphon[smoothed_vector]

    return output_tuple
