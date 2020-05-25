#!/usr/bin/env python2
#
# PuMA toa
# Python script for obtaining time of arrivals
# Author: PuMA collab.
# 2020

import sys
import glob
import os
import argparse
import time

from puma_lib import *


def set_argparse():
    # add arguments
    parser = argparse.ArgumentParser(prog='puma_toa.py',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description='calculating TOA(s) using pat')
    parser.add_argument('--pname', default='', type=str,
            help='name of pulsar')
    parser.add_argument('--mode', default='add', type=str,
            help='mode to calculate TOA(s). Options are: add and all. `add` appends TOA to .tim file and `all` creates a new set of TOA(s)')
    parser.add_argument('--pfd_dirname', default=os.environ['PWD'], type=str,
            help='path to where pfd file(s) is(are) located')
    parser.add_argument('--par_dirname', default='/opt/pulsar/tempo/tzpar/', type=str,
            help='path to directory containing .par file')
    parser.add_argument('--std_dirname', default=os.environ['TIMING'], type=str,
            help='path to default folder with .std templates')
    parser.add_argument('--tim_dirname', default=os.environ['PWD'], type=str,
            help='path where .tim will be saved')
    parser.add_argument('--n_subints', default=1, type=int,
            help='number of subintegrations for TOA calculation(s)')

    return parser.parse_args()


def check_cli_arguments(args):
    ierr = 0

    if args.pname == '':
        print('\n FATAL ERROR: no pulsar name specified\n')
        ierr = -1
        return ierr

    if os.path.isabs(args.pfd_dirname) is False:
        print('\n FATAL ERROR: pfd folder path is not absolute\n')
        ierr = -1
        return ierr

    if os.path.isabs(args.par_dirname) is False:
        print('\n FATAL ERROR: par folder path is not absolute\n')
        ierr = -1
        return ierr

    if os.path.isabs(args.std_dirname) is False:
        print('\n FATAL ERROR: std folder path is not absolute\n')
        ierr = -1
        return ierr

    if os.path.isabs(args.tim_dirname) is False:
        print('\n FATAL ERROR: tim folder path is not absolute\n')
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
    # instanciate Observation class
    obs = Observation(path2dir=args.pfd_dirname, pname=args.pname)
   
    # obs.antenna not defined previously, this is a quick amend!
    dirname = args.pfd_dirname
    obs.antenna = dirname.split('/')[-1]

    ierr = obs.do_toas(mode=args.mode, pfd_dirname=args.pfd_dirname, par_dirname=args.par_dirname,
            std_dirname=args.std_dirname, tim_dirname=args.tim_dirname, n_subints=args.n_subints)
    if ierr != 0: sys.exit(1)

    del obs

    # exit with success printing duration
    end = time.time()
    hours, rem = divmod(end-start, 3600)
    minutes, seconds = divmod(rem, 60)
    print('\n Reduction process completed in {:0>2}:{:0>2}:{:05.2f}\n'.format(int(hours), int(minutes), seconds))
