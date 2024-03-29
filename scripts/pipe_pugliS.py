#!/usr/bin/env python2

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

from puma_lib import Observation
from puma_utils import *
from puma_timing import plot_residuals


def send_alert(alert_type):
   # Define remote alert in a future
   if alert_type == 'red':
      print('\n \x1b[31;1m GLITCH RED ALERT! \x1b[0m \n')

   elif alert_type == 'blue':
      print('\n \x1b[34;1m glitch blue alert \x1b[0m \n')


def do_pipe_puglis(folder='', thresh=1.0e-8, path2pugliese='/home/jovyan/work/shared/PuGli-S/', nfils_total=1):

   start = time.time()

	# read relevant information from the .fil
   obs = Observation(folder)
   obs.nfils_total = obs.nfils

   # search for glitches (code red)
   obs.do_glitch_search(threshold=thresh, path_to_dir=folder)
   if obs.red_alert: send_alert('red')

   # calculate signal-to-noise ratio
   pfds = glob.glob(folder + '/*.pfd')
   for pfd in pfds:
      obs.calc_snr(pfd=pfd)

   # calculate TOAs
   tim_folder = path2pugliese + '/tims/'
   obs.do_toas(pfd_dirname=folder, tim_dirname=tim_folder)

   # search for glitches (code blue)
   # obs.do_timing(thresh)
   # if blue_alert: send_alert('blue')

   if obs.red_alert or obs.blue_alert:
      obs.glitch = True

   # calculate good time interval percentage
   obs.get_mask_percentage(obs.maskname)

   # copy files for visualization and analysis
   obs.pngs, obs.pfds, obs.polycos = copy_db(obs.pname, obs.antenna, folder, path2pugliese)

   #plot TOAs and save in PuGli-S database
   tim_fname = tim_folder + obs.pname + '_' +  obs.antenna + '.tim'
   output_dir = path2pugliese + '/' + obs.pname + '/'
   #par_fname = obs.dotpar_filename
   par_fname = '/opt/pulsar/puma/config/timing/' + obs.pname + '.par'
   plot_residuals(par_fname=par_fname, tim_fname=tim_fname, output_dir=output_dir, copy2last=True, units='ms')

   # call updater for webpage (puglieseweb_update)
   try:
      # write observation info
      write_pugliS_info_jason(path2pugliese,obs)
   except Exception,e:
      print(str(e))
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
   parser = argparse.ArgumentParser(prog='pipe_pugliS.py',
      formatter_class=argparse.ArgumentDefaultsHelpFormatter,
      description='Main pipeline for pulsar timing and glitch detections')
   parser.add_argument('--folder', default=os.environ['PWD'], type=str,
      help='ABSOLUTE PATH where observations are stored and where output will be created')
   parser.add_argument('--par_dirname', default='/opt/pulsar/tempo/tzpar/', type=str,
      help='path to directory containing .par file')
   parser.add_argument('--thresh', default=1e-8, type=float,
      help='threshold for glitch alert (DP/P > thresh)')
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

   do_pipe_puglis(args.folder, args.thresh, args.path2pugliese)
