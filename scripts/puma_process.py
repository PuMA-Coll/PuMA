#!/usr/bin/env python2
## puma_reduc

#Author: Santiago del Palacio for PuMA
#Date: April 2020

import os
import sys
import argparse
import shutil
from puma_utils import *
from pipe_pugliS import *
from pipe_reduc import *

from ConfigParser import SafeConfigParser
import glob
import sigproc
import subprocess


# ---------------------------------------------------------------
#                        IDEAS
# ---------------------------------------------------------------
# April 2020
# The acquisition soft stores all observations in a single folder. 
# We move them to a folder that contains all the observations for 
# each object. Once in the folder, we run the reduction pipeline.
# ---------------------------------------------------------------


def set_argparse():
   # add arguments
   parser = argparse.ArgumentParser(prog='puma_process.py',
         formatter_class=argparse.ArgumentDefaultsHelpFormatter,
         description='moves observations to reduction folder and applies a reduction pipeline')
   parser.add_argument('--obs_folder', default='/home/jovyan/work/shared/upload/', type=str,
         help='ABSOLUTE PATH to folder containing all the folders for each specific observation')
   parser.add_argument('--dest_path', default='/home/jovyan/work/shared/', type=str,
         help='path to directory containing all the observations for reduction')

   return parser.parse_args()


def check_cli_arguments(args):

   ierr = 0

   if os.path.isabs(args.obs_folder) is False:
      print('\n FATAL ERROR: observation folder path is not absolute\n')
      ierr = -1
      return ierr

   if os.path.isabs(args.dest_path) is False:
      print('\n FATAL ERROR: destination folder path is not absolute\n')
      ierr = -1
      return ierr


   return ierr


def process_observations(obs_folder='', dest_path=''):
   '''
   This function moves multiple observations contained within a single folder.
   It calls move_observation for each of these sub-folders and then the 
   appropriate reduction pipeline.
   '''

   ierr = 0

   if os.path.isdir(obs_folder) is False:
      print('\n FATAL ERROR: obs_folder does not exist')
      ierr = -1
      return ierr

   observations = glob.glob(obs_folder+'/*')

   for path_to_obs in observations:
      ierr, pname, reduction_path = move_observation(path_to_obs, dest_path)

      if ierr == 0:
         # calibration sources are not reduced with the pipelines
         #if (pname == 'testSource' or pname == 'cal' or pname == 'bla'):
         if (pname[0] != 'J'):
            continue

         # pipeline for non-glitching (ms) pulsars:
         if pname == 'J0437-4715' or pname == 'J2241-5236':
            # important: make sub-folders for each separate observation
            fils = glob.glob(reduction_path + '/*.fil')
            for i in range(len(fils)):
               obs_id = '/obs' + str(i) + '/'
               new_reduction_path = reduction_path + obs_id
               os.mkdir(new_reduction_path)
               shutil.move(fils[i], new_reduction_path)
               do_pipe_reduc(folder=new_reduction_path)

         # pipeline for glitching pulsars:
         else:
            do_pipe_puglis(folder=reduction_path)


#====================================================================================

if __name__ == '__main__':

   # get cli-arguments
   args = set_argparse()

   # check arguments
   ierr = check_cli_arguments(args)
   if ierr != 0: sys.exit(1)
   
   print('\n Start moving folders and processing observations')

   ierr = process_observations(obs_folder=args.obs_folder, dest_path=args.dest_path)

   if ierr != 0: sys.exit(1)
   
   print('\n Finished moving folders and processing observations')
