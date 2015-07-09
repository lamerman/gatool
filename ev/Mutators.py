__author__ = 'Alexander Ponomarev'

from pyevolve import Util
from random import randint as rand_randint, gauss as rand_gauss
from pyevolve import Consts


def G1DListMutatorIntegerGaussian(genome, **args):
    """ A gaussian mutator for G1DList of Integers

    Accepts the *rangemin* and *rangemax* genome parameters, both optional. Also
    accepts the parameter *gauss_mu* and the *gauss_sigma* which respectively
    represents the mean and the std. dev. of the random distribution.

    """
    if args["pmut"] <= 0.0: return 0
    listSize = len(genome)
    mutations = args["pmut"] * (listSize)

    mu = genome.getParam("gauss_mu")
    sigma = genome.getParam("gauss_sigma")

    if mu is None:
        mu = Consts.CDefG1DListMutIntMU

    if sigma is None:
        sigma = Consts.CDefG1DListMutIntSIGMA

    if mutations < 1.0:
        mutations = 0
        for it in xrange(listSize):
            if Util.randomFlipCoin(args["pmut"]):
                final_value = genome[it] + int(rand_gauss(mu, sigma))

                final_value = min(final_value, genome.getParam("rangemax")[it])
                final_value = max(final_value, genome.getParam("rangemin")[it])

                genome[it] = final_value
                mutations += 1
    else:
        for it in xrange(int(round(mutations))):
            which_gene = rand_randint(0, listSize - 1)
            final_value = genome[which_gene] + int(rand_gauss(mu, sigma))

            final_value = min(final_value, genome.getParam("rangemax")[which_gene])
            final_value = max(final_value, genome.getParam("rangemin")[which_gene])

            genome[which_gene] = final_value

    return int(mutations)