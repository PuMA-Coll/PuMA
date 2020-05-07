#!/usr/bin/env python2
#
# PuMA timing
# Python script for obtaining time of arrivals
# Author: PuMA collab.
# April 2020

# BORRAR LAS QUE NO SE USEN
import argparse
import time
import numpy as np
import shutil

import decimal
import subprocess
import math

import os
import scipy.stats


def set_argparse():
    # add arguments
    parser = argparse.ArgumentParser(prog='puma_timing.py',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description='calculate residuals using tempo2')
    parser.add_argument('--par_fname', default='', type=str,
            help='path to directory containing .par file')
    parser.add_argument('--tim_fname', default='', type=str,
            help='path to .tim file')

    return parser.parse_args()


def check_cli_arguments(args):
    ierr = 0

    # LATER CHECK IF ABSOLUTE PATHS ARE NEEDED
    #if os.path.isabs(args.par_dirname) is False:
    #    print('\n FATAL ERROR: .par file path is not absolute\n')
    #    ierr = -1
    #    return ierr

    #if os.path.isabs(args.tim_dirname) is False:
    #    print('\n FATAL ERROR: .tim file path is not absolute\n')
    #    ierr = -1
    #    return ierr

    return ierr


def calc_residuals(par_fname='', tim_fname=''):

    #tim_fname = tim_dirname + '/' + self.pname + self.antenna + '.tim'
    #par_fname = par_dirname + self.pname + '.par'

    # file where timing residuals will be stored (use .tim file as reference)
    res_fname = tim_fname.split('.ti')[0].split('/')[-1] + '.res'
    log_fname = tim_fname.split('.ti')[0].split('/')[-1] + '.log'

    line = '-residuals -us -f ' + par_fname + ' ' + tim_fname + ' > ' + log_fname

    # call tempo2 and store the output residuals and the log (fitting information)
    subprocess.call( 'tempo2 ' + line, shell=True )

    # the default name for the residuals files is 'residuals.dat'
    shutil.move('residuals.dat', res_fname)

    # we read the rms of the fitting from the tempo2 log
    rms = np.genfromtxt ( log_fname, comments="none", dtype=float, skip_header=18, max_rows=1, usecols=(10) )  

    # calculate the rms+- delta_rms(1 sigma) --> (not the errorbars, rather rms_min and rms_max) 
    n_obs = len(residuals) 
    prob_84 = scipy.stats.chi2.ppf( 0.84, n_obs)
    prob_16 = scipy.stats.chi2.ppf( 0.16, n_obs)    
    rms_min = round( math.sqrt( (n_obs / prob_84 )) * rms, 4) 
    rms_max = round( math.sqrt( (n_obs / prob_16 )) * rms, 4)
    print rms, rms_min, rms_max


def make_plot(par_fname='', tim_fname=''):

    import libstempo as T2
    import libstempo.plot as LP

    timing = T2.tempopulsar(parfile = par_fname, timfile = tim_fname)
    #residuals = timing.residuals()
    #n_obs = timing.nobs 

    # Plot residuals vs MJD
    LP.plotres(timing, alpha=0.2)

    # Save
    pname = tim_fname.split('.tim')[0].split('/')[-1]
    plot_output = pname + '_tempo.png'
    print('Saving plot to ' + plot_output)
    LP.savefig(plot_output, bbox_inches='tight')
    #LP.show()


if __name__ == '__main__':

    # get cli-arguments
    args = set_argparse()

    # check arguments
    ierr = check_cli_arguments(args)
    if ierr != 0: sys.exit(1)

    # file where timing residuals will be stored (use .tim file as reference)
    res_fname = args.tim_fname.split('.tim')[0].split('/')[-1] + '.res'
    log_fname = args.tim_fname.split('.tim')[0].split('/')[-1] + '.log'
    
    print('Calculating residuals')
    calc_residuals(par_fname=args.par_fname, tim_fname=args.tim_fname)

    print('Making residuals plot')
    make_plot(par_fname=args.par_fname, tim_fname=args.tim_fname)


    #tim_fname = '/home/jovyan/work/shared/PuGli-S/tims/J0437-4715_A1.tim'  
    #par_fname = '/opt/pulsar/puma/config/timing//J0437-4715.par'
    #puma_timing.py --par_fname='/opt/pulsar/puma/config/timing//J0437-4715.par' --tim_fname='/home/jovyan/work/shared/PuGli-S/tims/J0437-4715_A1.tim'  
