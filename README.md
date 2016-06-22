# gatool

Utility for console applications parameters adjustment with genetic algorithm.

Sometimes we want to adjust parameters of a console app or script but we do not want to do it manually. This script adjusts them for you automatically using genetic algorithm.

Simple usage:
Imagine we need to choose values for equation 2*X+4*Y^2=32
Let's solve it with python. Roughly it will look like:

    python -c "print 2*X+4*pow(Y,2)"

Replace those X and Y with syntaxis acceptable by gatool:

     python -c "print 2*{-3,6}+4*pow({1,10},2)"

Here {-3,6} is a range that X can accept, the same for Y
The final command that will choose variables with genetic algorithm is:

    gatool.py --cmd "python -c \"print 2*{-3,6}+4*pow({1,10},2)\"" --target-value 32

More complicated and more efficient approach is to set some parameters of genetic algorithm manually (more about params in --help):

    gatool.py --cmd "python -c \"print 2*{-3,6}+4*pow({1,10},2)\"" --target-value 32 --population 5 --crossover-rate 0.0 --generations 20  --mutation-gauss-mu 0 --mutation-gauss-sigma 10 --print-organisms 0 --mutation-rate 0.5 --ellitism-replacement 0  --stats-show-freq 1

So, it can run any app or script. The only requirement is that your script should return a number. This number will be compaired to --target-value and the closest numbers will be saved as best results.

What if my application does not return just one number to stdout? Very simple, you must write an adapter that converts the output of your script to just one number in stdout. It will look like:

    gatool.py --cmd "python -c \"print 2*{}+4*pow({},2)\" | my_adapter.py" --target-value 32


Limitations:
Now only integers are supported as arguments to your program, but floats will come soon.
Only G1DListMutatorIntegerGaussian is supported but others will come soon.

The tool uses pyevolve library.
