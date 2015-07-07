#!/usr/bin/env python

__author__ = 'Alexander Ponomarev'

import sys
import re
import os
import subprocess
import tempfile
import pickle
import hashlib
from os import path
from ev import Mutators, Initializators
from optparse import OptionParser, OptionGroup
from pyevolve import G1DList, GSimpleGA, Consts, Selectors


RANGE_TEMPLATE = '{{(-?\d+),(-?\d+)}}'


class TempFsCache:
    def __init__(self):
        self.tempdir = path.join(tempfile.gettempdir(), 'gatool')

        if not path.exists(self.tempdir):
            os.makedirs(self.tempdir)

    def get(self, key):
        hash_key = hashlib.md5(key).hexdigest()
        filename = path.join(self.tempdir, hash_key)
        if not path.exists(filename):
            raise KeyError("No such key in cache")

        with open(filename, 'rb') as f:
            return pickle.load(f)

    def put(self, key, value):
        hash_key = hashlib.md5(key).hexdigest()
        filename = path.join(self.tempdir, hash_key)
        with open(filename, 'wb') as f:
            return pickle.dump(value, f)


class FakeCache:
    def get(self, key): raise KeyError()

    def put(self, key, value): pass


cache = FakeCache()


def vararg_callback(option, opt_str, value, parser):
    assert value is None
    value = []

    for arg in parser.rargs:
        if arg[:2] == "--" and len(arg) > 2:
            break

        if arg[:1] == "-" and len(arg) > 1:
            break
        value.append(arg)

    del parser.rargs[:len(value)]
    setattr(parser.values, option.dest, value)


def get_options():
    parser = OptionParser(
        usage="\nImagine we need to choose values for equation 2*X+4*Y^2=32"
              "\nLet's solve it with python. Roughly it will look like:"
              "\n\npython -c \"print 2*X+4*pow(Y,2)\""
              "\n\nReplace those X and Y with syntaxis acceptable by gatool:"
              "\n\npython -c \"print 2*{-3,6}+4*pow({1,10},2)\""
              "\n\nHere {-3,6} is a range that X can accept, the same for Y"
              "\nThe final command that will choose variables with genetic algorithm is:"
              "\n\ngatool.py --cmd \"python -c \\\"print 2*{-3,6}+4*pow({1,10},2)\\\"\" --target-value 32"
              "\nSee other parameters to set up genetic algorithm")

    group_general = OptionGroup(parser, "General options")

    group_general.add_option("--cmd", dest="cmd",
                             help="[REQUIRED] Command pattern to be executed. "
                                  "[default: %default]")
    group_general.add_option("--target-value", type="float", dest="target_value",
                             help="[REQUIRED] The value that function will "
                                  "attempt to reach. [default: %default]")
    group_general.add_option("--initial-values", dest="initial_values",
                             action="callback",
                             callback=vararg_callback,
                             help="[NOT SUPPORTED YET] Initial arguments values. "
                                  "[default: %default]")
    group_general.add_option("--multithreading", type="int", dest="multithreading",
                             default=0,
                             help="Enables multithreading (1 or 0). [default: "
                                  "%default]")

    parser.add_option_group(group_general)

    group_ga = OptionGroup(parser, "Genetic algorithm common")

    group_ga.add_option("--generations", type="int", dest="generations",
                        default=Consts.CDefGAGenerations,
                        help="Maximum number of generations. Range: 1-inf. "
                             "[default: %default]")
    group_ga.add_option("--population", type="int", dest="population",
                        default=Consts.CDefGAPopulationSize,
                        help="Size of population. Range: 2-inf. [default: "
                             "%default]", )
    group_ga.add_option("--mutation-rate", type="float", dest="mutation_rate",
                        default=Consts.CDefGAMutationRate,
                        help="Mutation rate. Range: 0.0-1.0. [default: %default]")
    group_ga.add_option("--crossover-rate", type="float", dest="crossover_rate",
                        default=Consts.CDefGACrossoverRate,
                        help="Crossover rate. Range: 0.0-1.0. [default: %default]")
    group_ga.add_option("--selector", dest="selector",
                        default='GRankSelector',
                        help="Default selector. May be GRankSelector, GTournamentSelector, "
                             "GUniformSelector, GRouletteWheel. [default: %default]")
    group_ga.add_option("--ellitism-replacement", type="int", dest="ellitism_replacement",
                        default=Consts.CDefGAElitismReplacement,
                        help="How many best organisms of this generation will be "
                             "used in the next generation "
                             "without modification. Range: 0-population. [default: "
                             "%default]")

    parser.add_option_group(group_ga)

    group_gauss = OptionGroup(parser, "Gaussian mutator options")

    group_gauss.add_option("--mutation-gauss-mu", type="float", dest="mutation_gauss_mu",
                           default=Consts.CDefG1DListMutIntMU,
                           help="Mu in gauss distribution for mutation step. [default: "
                                "%default]")
    group_gauss.add_option("--mutation-gauss-sigma", type="float",
                           dest="mutation_gauss_sigma",
                           default=Consts.CDefG1DListMutIntSIGMA,
                           help="Sigma in gauss distribution for mutation step. "
                                "[default: %default]")

    parser.add_option_group(group_gauss)

    group_stat = OptionGroup(parser, "Statistics")

    group_stat.add_option("--stats-show-freq", dest="stats_show_freq", type='int',
                          default=10,
                          help="How frequently statistics will be shown. Once in n "
                               "iteration. 0 - do not show. "
                               "[default: %default]")
    group_stat.add_option("--print-organisms", dest="print_organisms", type='int',
                          default=0,
                          help="Prints organisms at each iteration (0 or 1). "
                               "[default: %default]")

    parser.add_option_group(group_stat)

    group_cache = OptionGroup(parser, "Cache")

    group_cache.add_option("--use-cache", dest="use_cache", type='int',
                           default=0,
                           help="Specifies whether cache will be used (0 or 1). "
                                "Warning: Default cache is file system cache in temp directory. "
                                "[default: %default]")

    parser.add_option_group(group_cache)

    (options, args) = parser.parse_args()

    if not options.cmd:
        print "Cmd not specified"
        exit(1)

    if not options.target_value:
        print "Target value not specified"
        exit(1)

    return options


def get_bad_value():
    return sys.maxint  # TODO: correct it


def execute_cmd(cmd_template, args):
    args = map(int, args)
    cmd = cmd_template.format(*args)

    try:
        return cache.get(cmd)
    except KeyError:
        pass

    pipe = subprocess.PIPE
    proc = subprocess.Popen(cmd, shell=True, stdout=pipe)
    stdout_text = proc.communicate()[0]

    ret = proc.wait()
    if ret != 0:
        result = get_bad_value()
        cache.put(cmd, result)
        return result

    try:
        result = float(stdout_text)
        cache.put(cmd, result)
        return result
    except ValueError:
        result = get_bad_value()
        cache.put(cmd, result)
        return result


def eval_func(chromosome):
    cmd_template = chromosome.getParam('cmd_template')
    target_value = chromosome.getParam('target_value')
    result = execute_cmd(cmd_template, chromosome.getInternalList())

    val = abs(target_value - result)

    if chromosome.getParam('print_organisms') == 1:
        print '{}, score: {}'.format(chromosome.getInternalList(), val)

    return val


def print_best(ga):
    print 'Best: {}, score: {}'.format(ga.bestIndividual().getInternalList(),
                                       ga.bestIndividual().getRawScore())


def step_callback(ga):
    if ga.currentGeneration % ga.getParam('freq_stats') == 0:
        print_best(ga)

    if ga.getParam('print_organisms') == 1:
        print '\n'  # prints separator of each iteration organisms

    return False


def main():
    opts = get_options()

    if opts.use_cache:
        global cache
        cache = TempFsCache()

    # escapes cmd string replacing {} by {{}}
    opts.cmd = re.sub('{(?P<block>[^}]*)}', '{{\g<block>}}', opts.cmd)

    num_args = len([m.start() for m in re.finditer(RANGE_TEMPLATE, opts.cmd)])
    minlist = []
    maxlist = []
    for minmax in re.findall(RANGE_TEMPLATE, opts.cmd):
        minlist.append(int(minmax[0]))
        maxlist.append(int(minmax[1]))

    # cleans up ranges and converts them just to {} for format() function
    opts.cmd = re.sub(RANGE_TEMPLATE, '{}', opts.cmd)

    genome = G1DList.G1DList(num_args)
    genome.mutator.set(Mutators.G1DListMutatorIntegerGaussian)
    genome.initializator.set(Initializators.G1DListInitializatorInteger)
    genome.setParams(cmd_template=opts.cmd)
    genome.setParams(target_value=opts.target_value)
    genome.setParams(bestrawscore=0)
    genome.setParams(print_organisms=opts.print_organisms)
    genome.setParams(rangemin=minlist)
    genome.setParams(rangemax=maxlist)
    genome.setParams(gauss_mu=opts.mutation_gauss_mu)
    genome.setParams(gauss_sigma=opts.mutation_gauss_sigma)

    genome.evaluator.set(eval_func)

    ga = GSimpleGA.GSimpleGA(genome)
    ga.stepCallback.set(step_callback)
    ga.setGenerations(opts.generations)
    ga.selector.set(getattr(Selectors, opts.selector))
    ga.setMinimax(Consts.minimaxType["minimize"])
    ga.terminationCriteria.set(GSimpleGA.RawScoreCriteria)
    ga.setParams(freq_stats=opts.stats_show_freq)
    ga.setParams(print_organisms=opts.print_organisms)

    if opts.ellitism_replacement == 0:
        ga.setElitism(False)
    else:
        ga.setElitism(True)
        ga.setElitismReplacement(opts.ellitism_replacement)

    ga.setMultiProcessing(True if opts.multithreading == 1 else False)
    ga.setPopulationSize(opts.population)
    ga.setMutationRate(opts.mutation_rate)
    ga.setCrossoverRate(opts.crossover_rate)

    ga.evolve(freq_stats=opts.stats_show_freq)

    print_best(ga)


if __name__ == '__main__':
    main()