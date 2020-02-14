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

   ierr = 0
   if os.path.isabs(args.folder) is False:
      print('\n FATAL ERROR: folder path is not absolute\n')
      ierr = -1
      return ierr

   return ierr


def send_alert(alert_type):
   # Define remote alert in a future
   if alert_type == 'red':
      print('\n \x1b[31;1m GLITCH RED ALERT! \x1b[0m \n')

   elif alert_type == 'blue':
      print('\n \x1b[34;1m glitch blue alert \x1b[0m \n')


def write_pugliS_info(path2db,obs):
   """ Write information"""
   fname = path2db + obs.pname + '.txt'

   order = ['pname', 'mjd', 'antenna', 'nchans', 'red_alert', 'blue_alert', 'par', 'jump' ]

   if os.path.isfile(fname) is False:
      f = open(fname, 'w')
      header = ''
      for key in order:
         header += '{:>40}'.format(key)
      f.write(header)
      f.close()

   f = open(fname, 'a')
   line = ''
   for key in order:
      line += '{:>40}'.format(str(obs.__dict__[key]))
   f.write(line)
   f.close()

   


#==================================================================================

if __name__ == '__main__':

   # get cli-arguments
   args = set_argparse()

   # check arguments
   ierr = check_cli_arguments(args)
   if ierr != 0: sys.exit(1)

   start = time.time()

   # move observations to destination folder par_dirname
   # (to complete)

   # read relevant information from the .fil
   obs = Observation(args.folder)

   # search for glitches (code red)
   obs.do_glitch_search(args.thresh)
   if obs.red_alert: send_alert('red')

   # search for glitches (code blue)
   #obs.do_glitch_search(thresh)
   # if blue_alert: send_alert('blue')

   if obs.red_alert or obs.blue_alert:
      obs.glitch = True

   # write observation info
   path2db = args.path2pugliese + 'database/'
   write_pugliS_info(path2db, obs)

   # copy files for visualization in ...
   # (to do)

   # call updater for webpage
   # (puglieseweb_update)

   # exit with success printing duration
   end = time.time()
   hours, rem = divmod(end-start, 3600)
   minutes, seconds = divmod(rem, 60)
   print('\n Reduction process completed in {:0>2}:{:0>2}:{:05.2f}\n'.format(int(hours), int(minutes), seconds))
