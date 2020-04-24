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


if __name__ == '__main__':

    #tim_fname = tim_dirname + '/' + self.pname + self.antenna + '.tim'
    #par_fname = par_dirname + self.pname + '.par'

    #tim_fname = '/home/jovyan/work/shared/PuGli-S/tims/J0437-4715_A1.tim'  
    #par_fname = '/opt/pulsar/puma/config/timing//J0437-4715.par'
    #puma_timing.py --par_fname='/opt/pulsar/puma/config/timing//J0437-4715.par' --tim_fname='/home/jovyan/work/shared/PuGli-S/tims/J0437-4715_A1.tim'  

    # get cli-arguments
    args = set_argparse()

    # check arguments
    ierr = check_cli_arguments(args)
    if ierr != 0: sys.exit(1)
    
    start = time.time()

    # file where timing residuals will be stored (use .tim file as reference)
    res_fname = args.tim_fname.split('.ti')[0].split('/')[-1] + '.res'
    log_fname = args.tim_fname.split('.ti')[0].split('/')[-1] + '.log'

    # Una posibilidad es algo de la forma: 
    # 'tempo2 -output general2 -s "{bat} {post} {err} \n" > ' + res_fname
    # Pero el formato no queda del todo bien. 
    line = '-residuals -us -f ' + args.par_fname + ' ' + args.tim_fname + ' > ' + log_fname

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

    # use the tempo2 library instead
    #import libstempo as tempo2
    #timing = t2.tempopulsar(parfile = par_fname, timfile = tim_fname)
    #residuals = timing.residuals()
    #n_obs = timing.nobs 

    # We can plot TOAs vs. residuals, but we should first sort the arrays; otherwise the array 
    # follow the order in the tim file, which may not be chronological.

    # get sorted array of indices
    #i = np.argsort(timing.toas())
    # use numpy fancy indexing to order residuals 
    #P.errorbar(timing.toas()[i],timing.residuals()[i],yerr=1e-6*timing.toaerrs[i],fmt='.',alpha=0.2)
    
    # Even simpler!
    #import libstempo.plot as LP
    #import matplotlib.pyplot as P
    #LP.plotres(timing,alpha=0.2)
