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

def smooth(p, inv_suffix, gendrop=False, hierarchy=False):
    '''
    Error smoothing function
    Takes the vector output by the neural network
    Partitions it into vectors each representing a potential phoneme
    Converts those partitions to the closest phoneme vectors
    '''
    # Compare to suffix vectors and choose closest one
    dist_from_suffix = {dist(p, inv_suffix.keys()[i]): inv_suffix.keys()[i] for i in range(len(inv_suffix))}

    smoothed_vector = min(dist_from_suffix.keys())
    output_tuple = dist_from_suffix[smoothed_vector]

    return output_tuple