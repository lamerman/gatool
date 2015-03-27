# gatool

Utility for adjustment of parameters for console applications with genetic algorithm.

Sometimes we want to adjust parameters of some console app or script but we do not want to do it manually. This script adjusts them for you automatically by using genetic algorithm.

Simple usage:
Suppose we want to find parameters for quadratic function to equal 32. The simple way is:

    gatool.py --cmd "python -c \"print 2*{}+4*pow({},2)\"" --target-value 32

More complicated and more efficient approach is to set some parameters of genetic algorithm manually (more about params in help):

    gatool.py --cmd "python -c \"print 2*{}+4*pow({},2)\"" --target-value 32 --population 5 --crossover-rate 0.0 --min-value -10 --max-value 110 --generations 20  --mutation-gauss-mu 0 --mutation-gauss-sigma 10 --print-organisms 0 --mutation-rate 0.5 --ellitism-replacement 0  --stats-show-freq 1

So, it can run any app or script. By {} you specify a place where argument will be inserted before execution. In our case

    "python -c \"print 2*{}+4*pow({},2)\""

will transform to, say:

    "python -c \"print 2*3+4*pow(8,2)\""

and executed. The execution will print 262 to stdout, which is quite far from the target value 32. As long as its far, GA will continue with new values before it finds the solution or the number of generations ends.

What if my application does not return just one number to stdout? Very simple, you must write an adapter that converts the output of your script to just one number in stdout. It will look like:

    gatool.py --cmd "python -c \"print 2*{}+4*pow({},2)\" | my_adapter.py" --target-value 32


Limitations:
Now only integers are supported as arguments to your program, but floats will come soon.
Only G1DListMutatorIntegerGaussian is supported but others will come soon.

The tool uses pyevolve library.
