__author__ = 'Alexander Ponomarev'

from random import randint as rand_randint


def G1DListInitializatorInteger(genome, **args):
    """ Integer initialization function of G1DList

    This initializator accepts the *rangemin* and *rangemax* genome parameters.

    """
    range_min = genome.getParam("rangemin")
    range_max = genome.getParam("rangemax")

    genome.genomeList = [rand_randint(range_min[i], range_max[i])
                         for i in xrange(genome.getListSize())]
