#!/usr/bin/env python

__author__ = 'Alexander Ponomarev'

import sys
import subprocess
from optparse import OptionParser, OptionGroup
from pyevolve import G1DList, GSimpleGA, Consts, Mutators, Selectors

class InMemoryCache:
    def __init__(self):
        self.db = {}

    def get(self, key):
        if not key in self.db:
            raise KeyError("No such key in db")

        return self.db[key]

    def put(self, key, value):
        self.db[key] = value

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
    parser = OptionParser()

    group_general = OptionGroup(parser, "General options")

    group_general.add_option("--cmd", dest="cmd",
                        help="[REQUIRED] Command pattern to be executed. [default: %default]")
    group_general.add_option("--target-value", type="float", dest="target_value",
                        help="[REQUIRED] The value that function will attempt to reach. [default: %default]")
    group_general.add_option("--initial-values", dest="initial_values", action="callback",
                        callback=vararg_callback,
                        help="[REQUIRED] Initial arguments values. [default: %default]")
    group_general.add_option("--multithreading", type="int", dest="multithreading",
                        default=0,
                        help="Enables multithreading (1 or 0). [default: %default]")

    parser.add_option_group(group_general)


    group_ga = OptionGroup(parser, "Genetic algorithm common")

    group_ga.add_option("--generations", type="int", dest="generations",
                        default=Consts.CDefGAGenerations,
                        help="Maximum number of generations. Range: 1-inf. [default: %default]")
    group_ga.add_option("--population", type="int", dest="population",
                        default=Consts.CDefGAPopulationSize,
                        help="Size of population. Range: 2-inf. [default: %default]",)
    group_ga.add_option("--mutation-rate", type="float", dest="mutation_rate",
                        default=Consts.CDefGAMutationRate,
                        help="Mutation rate. Range: 0.0-1.0. [default: %default]")
    group_ga.add_option("--crossover-rate", type="float", dest="crossover_rate",
                        default=Consts.CDefGACrossoverRate,
                        help="Crossover rate. Range: 0.0-1.0. [default: %default]")
    group_ga.add_option("--ellitism-replacement", type="int", dest="ellitism_replacement",
                        default=Consts.CDefGAElitismReplacement,
                        help="How many best organisms of this generation will be used in the next generation "
                            "without modification. Range: 0-population. [default: %default]")

    parser.add_option_group(group_ga)


    group_gauss = OptionGroup(parser, "Gaussian mutator options")

    group_gauss.add_option("--min-value", type="float", dest="min_value",
                        default=Consts.CDefRangeMin,
                        help="Minimal possible value of any of parameters. [default: %default]")
    group_gauss.add_option("--max-value", type="float", dest="max_value",
                        default=Consts.CDefRangeMax,
                        help="Maximum possible value of any of parameters. [default: %default]")
    group_gauss.add_option("--mutation-gauss-mu", type="float", dest="mutation_gauss_mu",
                        default=Consts.CDefG1DListMutIntMU,
                        help="Mu in gauss distribution for mutation step. [default: %default]")
    group_gauss.add_option("--mutation-gauss-sigma", type="float", dest="mutation_gauss_sigma",
                        default=Consts.CDefG1DListMutIntSIGMA,
                        help="Sigma in gauss distribution for mutation step. [default: %default]")

    parser.add_option_group(group_gauss)


    group_stat = OptionGroup(parser, "Statistics")

    group_stat.add_option("--stats-show-freq", dest="stats_show_freq", type='int',
                        default=10,
                        help="How frequently statistics will be shown. Once in n iteration. 0 - do not show. "
                         "[default: %default]")
    group_stat.add_option("--print-organisms", dest="print_organisms", type='int',
                        default=0,
                        help="Prints organisms at each iteration (0 or 1). [default: %default]")

    parser.add_option_group(group_stat)


    group_cache = OptionGroup(parser, "Cache")

    group_cache.add_option("--use-cache", dest="use_cache", type='int',
                        default=1,
                        help="Specifies whether cache will be used (0 or 1). [default: %default]")

    parser.add_option_group(group_cache)


    (options, args) = parser.parse_args()

    if not options.cmd or not options.target_value\
            or not options.initial_values:
        parser.print_help()
        exit(1)

    return options


def get_bad_value():
    return sys.maxint # TODO: correct it

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

    val = abs(target_value-result)

    if chromosome.getParam('print_organisms') == 1:
        print '{}, score: {}'.format(chromosome.getInternalList(), val)

    return val


def print_best(ga):
    print 'Best: {}, score: {}'.format(ga.bestIndividual().getInternalList(), ga.bestIndividual().getRawScore())

def step_callback(ga):
    if ga.currentGeneration % ga.getParam('freq_stats') == 0:
        print_best(ga)

    if ga.getParam('print_organisms') == 1:
        print '\n' #prints separator of each iteration organisms

    return False


def main():
    opts = get_options()

    if opts.use_cache:
        global cache
        cache = InMemoryCache()

    genome = G1DList.G1DList(len(opts.initial_values))
    genome.mutator.set(Mutators.G1DListMutatorIntegerGaussian)
    genome.setInternalList([int(val) for val in opts.initial_values])
    genome.setParams(cmd_template=opts.cmd)
    genome.setParams(target_value=opts.target_value)
    genome.setParams(bestrawscore=0)
    genome.setParams(print_organisms=opts.print_organisms)

    if opts.min_value:
        genome.setParams(rangemin=opts.min_value)

    if opts.max_value:
        genome.setParams(rangemax=opts.max_value)

    if opts.mutation_gauss_mu:
        genome.setParams(gauss_mu=opts.mutation_gauss_mu)

    if opts.mutation_gauss_sigma:
        genome.setParams(gauss_sigma=opts.mutation_gauss_sigma)

    genome.evaluator.set(eval_func)

    ga = GSimpleGA.GSimpleGA(genome)
    ga.stepCallback.set(step_callback)
    ga.setGenerations(opts.generations)
    ga.selector.set(Selectors.GRouletteWheel)
    ga.setMinimax(Consts.minimaxType["minimize"])
    ga.terminationCriteria.set(GSimpleGA.RawScoreCriteria)
    ga.setParams(freq_stats=opts.stats_show_freq)
    ga.setParams(print_organisms=opts.print_organisms)

    if opts.ellitism_replacement:
        ga.setElitismReplacement(opts.ellitism_replacement)

    if opts.multithreading:
        ga.setMultiProcessing(True if opts.multithreading == 1 else False)

    if opts.population:
        ga.setPopulationSize(opts.population)

    if opts.mutation_rate:
        ga.setMutationRate(opts.mutation_rate)

    if opts.crossover_rate:
        ga.setCrossoverRate(opts.crossover_rate)

    if opts.stats_show_freq:
        ga.evolve(freq_stats=opts.stats_show_freq)

    print_best(ga)


if __name__ == '__main__':
    main()