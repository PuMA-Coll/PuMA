#!/usr/bin/env python2

#Author: PuGli-S
#Date: April 2020

import os
import sys
sys.path.insert(1,os.path.join(sys.path[0], '/opt/pulsar/puma/scripts/'))
import time
import argparse

from ConfigParser import SafeConfigParser
import glob
import sigproc
import subprocess

from puma_lib import Observation
from puma_utils import *
from puma_timing import make_plot


def set_argparse():
   # add arguments
   parser = argparse.ArgumentParser(prog='pipe_reduc.py',
      formatter_class=argparse.ArgumentDefaultsHelpFormatter,
      description='Main pipeline for pulsar timing (no glitch search)')
   parser.add_argument('--folder', default=os.environ['PWD'], type=str,
      help='ABSOLUTE PATH where observations are stored and where output will be created')
   parser.add_argument('--par_dirname', default='/opt/pulsar/tempo/tzpar/', type=str,
      help='path to directory containing .par file')
   parser.add_argument('--path2pugliese', default='/home/jovyan/work/shared/PuGli-S/', type=str,
      help='Pugli-S database folder')

   return parser.parse_args()


def check_cli_arguments(args):

   ierr = 0
   if os.path.isabs(args.folder) is False:
      print('\n FATAL ERROR: folder path is not absolute\n')
      ierr = -1
      return ierr

   return ierr


def write_obs_info(path2db,obs):
   """ Write information"""
   fname = path2db + obs.pname + '.txt'

   # Use the same order as for glitching pulsars for consistency in a single database.
   order = ['pname', 'mjd', 'path_to_dir', 'antenna', 'nchans', 'dotpar_filename', 'jump', 'gti_percentage', 'nfils', 'nempty']

   if os.path.isfile(fname) is False:
      f = open(fname, 'w')
      header = ''
      for key in order:
         header += '{:>40}'.format(key)
      header += '\n'
      f.write(header)
      f.close()

   f = open(fname, 'a')
   line = ''
   for key in order:
      line += '{:>40}'.format(str(obs.__dict__[key]))
   line += '\n'
   f.write(line)
   f.close()

   
def do_pipe_reduc(folder='', path2pugliese='/home/jovyan/work/shared/PuGli-S/'):

   start = time.time()

   # read relevant information from the .fil
   obs = Observation(folder)

   # reduce using PRESTO (timing mode only)
   obs.set_params2reduc(path_to_dir=folder)
   obs.do_reduc()

   # calculate TOAs
   tim_folder = path2pugliese + '/tims/'
   obs.do_toas(pfd_dirname=folder, tim_dirname=tim_folder)

   # plot TOAs and save in PuGli-S database
   #tim_fname = tim_folder + obs.pname + '_' +  obs.antenna + '.tim'
   #output_dir = path2pugliese + '/' + obs.pname + '/'
   #make_plot(par_fname=obs.dotpar_filename, tim_fname=tim_fname, output_dir=output_dir)
   
   # non-glitching pulsar
   obs.glitch = False
   obs.jump = 0

   # calculate good time interval percentage
   obs.get_mask_percentage(obs.maskname)   

   # write observation info
   path2db = path2pugliese + 'database/'
   write_obs_info(path2db, obs)
  
   # copy files for visualization and analysis
   copy_db(obs.pname, folder, path2pugliese)   

   # call updater for webpage
   # (puglieseweb_update)

   # exit with success printing duration
   end = time.time()
   hours, rem = divmod(end-start, 3600)
   minutes, seconds = divmod(rem, 60)
   print('\n Reduction process completed in {:0>2}:{:0>2}:{:05.2f}\n'.format(int(hours), int(minutes), seconds))


   
#==================================================================================

if __name__ == '__main__':

   # get cli-arguments
   args = set_argparse()

   # check arguments
   ierr = check_cli_arguments(args)
   if ierr != 0: sys.exit(1)

   do_pipe_reduc(args.folder, args.path2pugliese)
