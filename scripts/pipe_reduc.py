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
from puma_timing import plot_residuals


def do_pipe_reduc(folder='', path2pugliese='/home/jovyan/work/shared/PuGli-S/', nfils_total=1):

   start = time.time()

   # read relevant information from the .fil
   obs = Observation(folder)
   obs.nfils_total = nfils_total

   # reduce using PRESTO (timing mode only)
   obs.set_params2reduc(path_to_dir=folder)
   obs.do_reduc()

   # calculate signal-to-noise ratio
   pfd = glob.glob(folder + '/*.pfd')[0]
   obs.calc_snr(pfd=pfd)

   # calculate TOAs
   tim_folder = path2pugliese + '/tims/'
   obs.do_toas(pfd_dirname=folder, tim_dirname=tim_folder)

   # non-glitching pulsar
   obs.glitch = False
   obs.jump = 0

   # calculate good time interval percentage
   obs.get_mask_percentage(obs.maskname)   

   # copy files for visualization and analysis; also store the output paths in observation object
   obs.pngs, obs.pfds, obs.polycos = copy_db(obs.pname, obs.antenna, folder, path2pugliese)   

   # plot TOAs and save in PuGli-S database
   tim_fname = tim_folder + obs.pname + '_' +  obs.antenna + '.tim'
   output_dir = path2pugliese + '/' + obs.pname + '/'
   #par_fname = obs.dotpar_filename
   par_fname = '/opt/pulsar/puma/config/timing/' + obs.pname + '.par'
   plot_residuals(par_fname=par_fname, tim_fname=tim_fname, output_dir=output_dir, copy2last=True, units='us')
   
   # write observation info
   try:
      write_pugliS_info_jason(path2pugliese,obs)
   except:
      print('\n JASON_NEW FAILED')

   # exit with success printing duration
   end = time.time()
   hours, rem = divmod(end-start, 3600)
   minutes, seconds = divmod(rem, 60)
   print('\n Reduction process completed in {:0>2}:{:0>2}:{:05.2f}\n'.format(int(hours), int(minutes), seconds))


   
#=========================================================================
# BELOW IS JUST FOR RUNNING AS INDEPENDENT PROGRAM   


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
   # check if command line arguments are OK
   ierr = 0
   if os.path.isabs(args.folder) is False:
      print('\n FATAL ERROR: folder path is not absolute\n')
      ierr = -1
      return ierr

   return ierr


if __name__ == '__main__':

   # get cli-arguments
   args = set_argparse()

   # check arguments
   ierr = check_cli_arguments(args)
   if ierr != 0: sys.exit(1)

   do_pipe_reduc(args.folder, args.path2pugliese)
