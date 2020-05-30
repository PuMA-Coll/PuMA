#!/usr/bin/env python2
## puma_reprocess

#Author: Santiago del Palacio for PuMA
#Date: May 2020

import os
import sys
import shutil
import glob
from puma_process import process_observations

'''
This program must be executed in the pulsar folder to reprocess. 
It takes care of old formatting in the folders and then uses 
the subroutine in puma_process to reprocess the observations which
are previously moved to a temporary folder within the pulsar folder.
'''

def oldfolder_to_newfolder(folder=''):
   '''
   This function moves multiple observations contained within a single folder with 
   old_paths: /YYYYMMDD/A*/obs*/ or /YYYYMMDD/A*/all/
   The new paths are: /YYYY-MM-DDT_A*/
   '''
   def adapt_folder(folder, fils, AX):
      if len(fils) > 0:
         new_folder = folder + '_' + AX + '/'
         try:
            print('creating ' + new_folder)
            os.mkdir(new_folder)
         except Exception:
            print(new_folder + ' already exists')
         for fil in fils:
            os.rename(fil, new_folder+fil.split('/')[-1])


   if os.path.isdir(folder):
      fils_A1 = glob.glob(folder + '*/A1/*/*.fil')
      adapt_folder(folder, fils_A1, 'A1')

      fils_A2 = glob.glob(folder + '*/A2/*/*.fil')
      adapt_folder(folder, fils_A2, 'A2')

      # SHOULD WE SEARCH MORE EXTENSIVELY WITH A WALK? SEE IF NUMBER OF FILES MATCH?
      # This is just in case some observations are not placed in a subfolder
      fils_A1 = glob.glob(folder + '*/A1/*.fil')
      adapt_folder(folder, fils_A1, 'A1')

      fils_A2 = glob.glob(folder + '*/A2/*.fil')
      adapt_folder(folder, fils_A2, 'A2')

      shutil.rmtree(folder)
   

#====================================================================================


if __name__ == '__main__':

   pwd = os.getcwd()
   temp_folder = pwd + '/temp/'
   if len( glob.glob(temp_folder + '*') ) > 0:
   	print(temp_folder + ' is not empty! ABORT')
   	sys.exit(1)

   # Get absolute paths to all .fil files. We have two distinct formats:
   # old_paths: these are strings /YYYYMMDD/A*/obs*/ or /YYYYMMDD/A*/all/
   # new_paths: these are strings /YYYY-MM-DDT:HH:MM:SS/ or /YYYY-MMTDD:HH:MM:SS_A*/

   print('\n Looking for observations in old folders format')
   folders = glob.glob('*')
   old_folders = []
   for folder in folders:
      if 'T' not in folder:
         old_folders.append(folder)

   # Change the structure in the old observation folder to match the new one
   print('\n Adapting ' + str(len(old_folders)) + ' folders to the new format')
   for folder in old_folders:
      oldfolder_to_newfolder(folder=folder)

   # Move all the observations to a new directory to reduce them one by one
   print('\n Moving the observations to a temporary folder')
   os.mkdir(temp_folder)
   folders = glob.glob('*A*')
   for folder in folders:
      print(folder, temp_folder + folder)
      os.rename(folder, temp_folder + folder)

   # Process the observations using puma_process.py
   reduction_folder = '/home/jovyan/work/shared/' # (THIS CAN BE CHANGED AS A CLI ARGUMENT IF NEEDED)
   print('\n Start moving and processing observations from temp folder (' + temp_folder + ') to reduction folder (' + reduction_folder + ') using process_observations')

   ierr = process_observations(obs_folder=temp_folder, dest_path = reduction_folder)

   if ierr != 0: sys.exit(1)

   print('Removing temp folder (' + temp_folder + ')')
   os.rmdir(temp_folder)

   print('\n Finished reprocessing observations')
