#!/usr/bin/env python2
## pipe_red_trigger

#Author: PuGli-S
#Date: Feb 2020

import os
import sys
sys.path.insert(1,os.path.join(sys.path[0], '/opt/pulsar/puma/scripts/'))
import time
import argparse

from ConfigParser import SafeConfigParser
import glob
import sigproc
import subprocess

from puma_lib import *


def set_argparse():
    
   # add arguments
   parser = argparse.ArgumentParser(prog='pipe_red_trigger.py',
      formatter_class=argparse.ArgumentDefaultsHelpFormatter,
      description='Red alerts for major glitches detected only using PRESTO')
   parser.add_argument('--folder', default=os.environ['PWD'], type=str,
      help='ABSOLUTE PATH where observations are stored and where output will be created')
   parser.add_argument('--par_dirname', default='/opt/pulsar/tempo/tzpar/', type=str,
      help='path to directory containing .par file')
   parser.add_argument('--thresh', default=1e-8, type=float,
      help='threshold for glitch alert (DP/P > thresh)')

   return parser.parse_args()


def check_cli_arguments(args):

   ierr = 0
   if os.path.isabs(args.folder) is False:
      print('\n FATAL ERROR: folder path is not absolute\n')
      ierr = -1
      return ierr

   return ierr


#==================================================================================

if __name__ == '__main__':

   # get cli-arguments
   args = set_argparse()

   # check arguments
   ierr = check_cli_arguments(args)
   if ierr != 0: sys.exit(1)
    
   start = time.time()

   obs = Observation()
   ierr = obs.do_glitch_search(path_to_dir=args.folder, par_dirname=args.par_dirname, ncores=1, thresh=args.thresh)

   print('Found glitch?', obs.red_alert, 'delta P/P = ', obs.jump)
   if obs.red_alert: print('\n GLITCH RED ALERT! \n')

   del obs

   # exit with success printing duration
   end = time.time()
   hours, rem = divmod(end-start, 3600)
   minutes, seconds = divmod(rem, 60)
   print('\n Reduction process completed in {:0>2}:{:0>2}:{:05.2f}\n'.format(int(hours), int(minutes), seconds))
