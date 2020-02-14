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
import parfile

from puma_reduc import do_reduc



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



def read_bestprof(ftype=''):

   ierr = 0
   try:
      filename = glob.glob('*'+ftype+'*.bestprof')[0]
   except Exception:
      print('\n FATAL ERROR: could not find bestprofile for ',ftype,'\n')
      ierr = -1
      return 1000,10,ierr

   f = open(filename, 'r')
   lines = f.readlines()
   for line in lines:
      if 'P_topo ' in line:
         str_arr = line.strip().split(' ')
         P_topo = filter(None, str_arr)[4]
         err_P_topo = filter(None, str_arr)[6]
         break

   f.close()

   return float(P_topo),float(err_P_topo),ierr


def glitch_search(folder='', par_dirname='', ncores=2, thresh=1e-8):

   # Check if the reducs have already been made
   if len(glob.glob('*timing*.pfd')) + len(glob.glob('*par*.pfd')) < 2: 

      ierr = do_reduc(ftype='timing', folder=folder, par_dirname=par_dirname, ncores=ncores)
      if ierr != 0:
         sys.exit(1)

      ierr = do_reduc(ftype='par', folder=folder, par_dirname=par_dirname, ncores=ncores)
      if ierr != 0:
         sys.exit(1)

   # Check for glitch
   P_eph, err_P, ierr = read_bestprof('timing')
   if ierr != 0:
      sys.exit(1)

   P_obs, err_P, ierr = read_bestprof('par')
   if ierr != 0:
      sys.exit(1)

   DP = P_eph - P_obs
   jump = DP/P_eph

   glitch = False
   if jump > thresh and err_P/P_eph < thresh:
      glitch = True

   return glitch, jump

#==================================================================================

if __name__ == '__main__':

   # get cli-arguments
   args = set_argparse()

   # check arguments
   ierr = check_cli_arguments(args)
   if ierr != 0:
      sys.exit(1)
   else:
      start = time.time()

      glitch, jump = glitch_search(folder=args.folder, par_dirname=args.par_dirname, 
         ncores=2, thresh=args.thresh)

   print('Found glitch?', glitch, 'delta P/P = ', jump)

   if glitch: print('\n GLITCH RED ALERT! \n')

   # exit with success printing duration
   end = time.time()
   hours, rem = divmod(end-start, 3600)
   minutes, seconds = divmod(rem, 60)
   print('\n Reduction process completed in {:0>2}:{:0>2}:{:05.2f}\n'.format(int(hours), int(minutes), seconds))
