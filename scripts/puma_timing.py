#!/usr/bin/env python2
#
# PuMA timing
# Python script for obtaining and plotting residuals
# Author: PuMA collab.
# April 2020

import argparse
import numpy as np
import shutil
import math
import os

import scipy.stats
import libstempo as T2

import matplotlib
#matplotlib.use('TKAgg', warn=False, force=True)
matplotlib.use('Agg')
from matplotlib import pyplot as P


def calc_residuals_errorbars(rms, n_obs):
    """" Calculate the rms uncertainties at 1 sigma (rms_min and rms_max, not the errorbars)."""

    prob_84 = scipy.stats.chi2.ppf( 0.84, n_obs)
    prob_16 = scipy.stats.chi2.ppf( 0.16, n_obs)    
    rms_min = round( math.sqrt( (n_obs / prob_84 )) * rms, 4) 
    rms_max = round( math.sqrt( (n_obs / prob_16 )) * rms, 4)
    return rms_min, rms_max


def plot_residuals(par_fname='', tim_fname='', output_dir='', copy2last=False, units=''):
    """Plot residuals."""

    # file where timing residuals will be stored (use .tim file as reference)
    res_fname = output_dir + '/' + tim_fname.split('.tim')[0].split('/')[-1] + '.res'

    print('Calculating residuals')

    timing = T2.tempopulsar(parfile=par_fname, timfile=tim_fname)
    res, t, errs = timing.residuals(), timing.toas(), timing.toaerrs

    print('Saving residuals to ' + res_fname)

    residuals_array = np.vstack((t, res, errs)).T
    np.savetxt(res_fname, residuals_array, header='MJD[day]  res[us]    err[us]')    

    if timing.nobs < 2:
        print("There are {0} points, I cannot make a plot".format(timing.nobs))
    else:
        print("Plotting {0} points.".format(timing.nobs))

        if units == 'us':
            un = 1e6
            ylabel = 'res [us]'
            rms_title = '\mu$s'
        elif units == 'ms':
            un = 1e3
            ylabel = 'res [ms]'
            rms_title = '$ms'

        rms = timing.rms()*un    # convert to units
        rms_min, rms_max = calc_residuals_errorbars(n_obs=timing.nobs, rms=rms)
        rms_err = math.sqrt( (rms-rms_min)**2 + (rms-rms_max)**2 )/2 # APPROX! 

        i = np.argsort(t)
        P.errorbar(t[i], res[i]*un, yerr=errs[i]*un/1e6, fmt='x', marker=".")
            
        #P.legend(unique,numpoints=1,bbox_to_anchor=(1.1,1.1))
        P.xlabel('MJD'); P.ylabel(ylabel)
        P.title("{0} , $rms={1:.2f} \pm {2:.2f} {3} , $\chi^2_r={4:.2f}$".format(timing.name,rms,rms_err,rms_title,timing.chisq()))

        # Save
        pname_A = tim_fname.split('.tim')[0].split('/')[-1]
        plot_output = output_dir + '/' + pname_A + '_tempo.png'
        print('Saving plot to ' + plot_output)
        P.savefig(plot_output, bbox_inches='tight')

        # Save a copy in last_obs if requested:
        if copy2last: 
            path2pugliese='/home/jovyan/work/shared/PuGli-S/'
            path2last = path2pugliese + '/last_obs/'
            shutil.copy(plot_output, path2last)

        # Clear figure for possible future calls in a pipeline
        P.clf()


#=========================================================================
# BELOW IS JUST FOR RUNNING AS INDEPENDENT PROGRAM   

def set_argparse():
    # add arguments
    parser = argparse.ArgumentParser(prog='puma_timing.py',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description='Calculate residuals using tempo2 and plot them')
    parser.add_argument('--par_fname', default='', type=str,
            help='absolute path to directory containing .par file')
    parser.add_argument('--tim_fname', default='', type=str,
            help='absolute path to .tim file')
    parser.add_argument('--output_dir', default=os.environ['PWD'], type=str,
            help='absolute path where the plot will be saved')
    parser.add_argument('--copy2last', default=False, type=bool,
            help='Do you want to make a copy in Pugli-S/last_obs?')
    parser.add_argument('--units', default='', type=str,
            help='Units for the plot. Options are: ms, us')

    return parser.parse_args()


def check_cli_arguments(args):
    ierr = 0
    if os.path.isabs(args.par_fname) is False:
        print('\n FATAL ERROR: .par file path is not absolute\n')
        ierr = -1
        return ierr
    if os.path.isabs(args.tim_fname) is False:
        print('\n FATAL ERROR: .tim file path is not absolute\n')
        ierr = -1
        return ierr
    return ierr


if __name__ == '__main__':

    # get cli-arguments
    args = set_argparse()

    # check arguments
    ierr = check_cli_arguments(args)
    if ierr != 0: sys.exit(1)
    
    plot_residuals(par_fname=args.par_fname, tim_fname=args.tim_fname, output_dir=args.output_dir, units=args.units)

    #tim_fname = '/home/jovyan/work/shared/PuGli-S/tims/J0437-4715_A1.tim'  
    #par_fname = '/opt/pulsar/puma/config/timing//J0437-4715.par'
    #puma_timing.py --par_fname='/opt/pulsar/puma/config/timing//J0437-4715.par' --tim_fname='/home/jovyan/work/shared/PuGli-S/tims/J0437-4715_A1.tim' --copy2last=True  
