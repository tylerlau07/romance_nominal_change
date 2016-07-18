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

def smooth(p, suf_to_tup):
    '''
    Error smoothing function
    Takes the vector output by the neural network
    Takes dictionary that converts suffix to relevant tuple
    Converts those partitions to the closest phoneme vectors
    '''
    # Compare to suffix vectors and choose closest one
    dist_from_suffix = {dist(p, suf_to_tup.keys()[i]): suf_to_tup.keys()[i] for i in range(len(suf_to_tup))}

    smoothed_vector = min(dist_from_suffix.keys())
    output_tuple = dist_from_suffix[smoothed_vector]

    print output_tuple

    return output_tuple
