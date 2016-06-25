import numpy
import random
import constants

# Using numpy, determine the Euclidean distance between the vectors, float
def dist(p, q):
    '''Takes in the actual vector (determined by neural net) and determines distance from output vectors'''
    return numpy.linalg.norm(numpy.array(p) - numpy.array(q))

def identity_tuples(n):
    # Identity matrix as a list of tuples
    return map(tuple, numpy.identity(n, int))

def smooth(p, gendrop=False, hierarchy=False):
    '''
    Error smoothing function
    Takes the vector output by the neural network
    Partitions it into the relevant datasets
    Converts those partitions to the closest unit vectors
    '''
    # partition the input vector into gender, declension, case, and number
    gender = p[constants.gen_b:constants.dec_b]
    declension = p[constants.dec_b:constants.casenum_b]
    case = p[constants.casenum_b:]

    # Determine the dimension of the vectors
    gender_dimension = len(gender)
    declension_dimension = len(declension)
    case_dimension = len(case)

    # Identity matrices based on 
    gender_space = identity_tuples(gender_dimension)
    declension_space = identity_tuples(declension_dimension)
    case_space = identity_tuples(case_dimension)

    # Dictionaries keyed by the distance from the given value to the closest unit vector, valued by those unit vectors
    genders = {dist(gender, gender_space[i]): gender_space[i] for i in range(gender_dimension)}
    decs = {dist(declension, declension_space[i]): declension_space[i] for i in range(declension_dimension)}

    # Change case identity vectors if hierarchy in play
    if hierarchy:
        case_space = [
            # nom
            (1, 0, 0),
            # acc
            (1, 1, 0),
            # gen
            (1, 1, 1)
        ]

    cases = {dist(case, case_space[i]): case_space[i] for i in range(case_dimension)}

    if gendrop:
        # Delete the genitive
        cases = {key: value for key, value in cases.iteritems() if value not in [(1, 1, 1), (0, 0, 1)]}

    smoothed_vectors = [
        genders[min(genders.keys())],
        decs[min(decs.keys())],
        cases[min(cases.keys())],
    ]
    # print smoothed_vectors

    # Flatten to one list
    return [item for vector in smoothed_vectors for item in vector]
