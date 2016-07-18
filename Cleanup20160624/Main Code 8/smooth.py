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

def smooth(p, suf_dict):
    '''
    Error smoothing function
    Takes the vector output by the neural network
    Takes dictionary that converts suffix to relevant tuple
    Converts those partitions to the closest phoneme vectors
    '''

    # Find closest suffix to tuple representation using dictionary keying distance to suffix
    dist_from_realsuf = {dist(p, suf_dict.values()[i]): suf_dict.values()[i] for i in range(len(suf_dict.values()))}
    smoothed_vector = min(dist_from_realsuf.keys())
    output_tuple = dist_from_realsuf[smoothed_vector]

    return output_tuple
