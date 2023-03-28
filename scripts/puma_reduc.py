#!/usr/bin/env python2
## puma_reduc

#'El hermano lindo de pulsar_reduc'
#Author: Luciano Combi for PuMA
#Date: April 2019

import os
import sys
import time
import argparse
from puma_lib import *

from ConfigParser import SafeConfigParser
import glob
import sigproc
import subprocess


# --------------------------------------------------------
#                        IDEAS
# --------------------------------------------------------
# 07/02/2020
# Treat each observation data as a python class such as:
# raw-data, mask, pfd, observation-data for glitches and
# more.
# Advantages: easy to access once its created and store in
# different formats (hdf5)
# --------------------------------------------------------


def set_argparse():
    # add arguments
    parser = argparse.ArgumentParser(prog='puma_reduc.py',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description='raw data folding with PRESTO')
    parser.add_argument('--ftype', default='timing', type=str,
            help='folding tag. Options are: timing, par and search')
    parser.add_argument('--folder', default=os.environ['PWD'], type=str,
            help='ABSOLUTE PATH where observations are stored and where output will be created')
    parser.add_argument('--ptopo', default=None, type=str,
            help='seed for the topocentric folding period in sec')
    parser.add_argument('--par_dirname', default='/opt/pulsar/puma/pardir', type=str,
            help='path to directory containing .par file')
    parser.add_argument('--start', default=0.0, type=float,
            help='The folding start time as a fraction of the full obs')
    parser.add_argument('--end', default=1.0, type=float,
            help='The folding end time as a fraction of the full obs')
    parser.add_argument('--rficlean', default=False, type=bool,
            help='Use rficlean as part of the cleaning algorithm')

    return parser.parse_args()


def check_cli_arguments(args):

    ierr = 0

    if os.path.isabs(args.folder) is False:
        print('\n FATAL ERROR: folder path is not absolute\n')
        ierr = -1
        return ierr

    if args.ftype != 'timing' and args.ftype != 'par' and args.ftype != 'search':
        print('\n FATAL ERROR: unknown option for ftype\n')
        ierr = -1
        return ierr

    if args.ftype == 'search' and args.ptopo is None:
        print('\n FATAL ERROR: you must specify --ptopo for the search mode\n')
        ierr = -1
        return ierr

    return ierr


if __name__ == '__main__':

    # get cli-arguments
    args = set_argparse()

    # check arguments
    ierr = check_cli_arguments(args)
    if ierr != 0: sys.exit(1)
    
    start = time.time()

    obs = Observation(path2dir=args.folder)
    ierr = obs.set_params2reduc(ftype=args.ftype, path_to_dir=args.folder, par_dirname=args.par_dirname, 
    	ptopo=args.ptopo, start=args.start, end=args.end)
    ierr = obs.do_reduc(args.rficlean)
    if ierr != 0: sys.exit(1)
	
    del obs

    # exit with success printing duration
    end = time.time()
    hours, rem = divmod(end-start, 3600)
    minutes, seconds = divmod(rem, 60)
    print('\n Reduction process completed in {:0>2}:{:0>2}:{:05.2f}\n'.format(int(hours), int(minutes), seconds))
