"""
Utility functions for pipe_pugliS
"""

import os
import sys
import glob
import shutil

#need to import pipe_pugliS and pipe_reduc?

def copy_db(path2ini, path2end):
   '''
   Copy files useful for database (.ps converted to png, and pfdfiles)
   '''
   path2pngs = path2end + 'last_obs/'
   path2pfds =  path2end + 'pfds/' 

   ps_mask = glob.glob(path2ini + '/*mask*.ps')[0]
   pngfile = ps_mask[:-2] + 'png'
   os.system('convert ' + ps_mask + ' ' + pngfile)

   png_files = glob.glob(path2ini + '/*.png') 
   pfd_files = glob.glob(path2ini + '/*.pfd') 

   for png_file in png_files:
      shutil.copy(png_file, path2pngs)

   for pfd_file in pfd_files:
      shutil.copy(pfd_file, path2pfds)


def move_observation(path_to_obs='', dest_path=''):
   '''
   This function moves all files from an observation done by each
   antenna into the database folder for later reduction. It also 
   returns the pulsar name and the new reduction folder.
   '''

   ierr = 0

   if os.path.isdir(path_to_obs) is False:
      print('\n FATAL ERROR: path_to_obs does not exist')
      ierr = -1
      return ierr, 'NN', 'No path'

   # skel: path_to_obs = '.../upload/date', dest_path = '.../'
   print(path_to_obs)

   # grab pulsar name and antenna from *.fil file name 
   try:
      fil_fname = glob.glob(path_to_obs + '/*.fil')[0]
      pulsar_name = fil_fname.split('_')[1].split('/')[-1]
      antenna = fil_fname.split('_')[2]

   except:
      print('\n FATAL ERROR: no .fil file found!')
      ierr = -1
      return ierr, 'NN', 'No path'

   # add antenna to the observation folder name
   new_path_to_obs = path_to_obs + '_' + antenna

   shutil.move(path_to_obs, new_path_to_obs)

   # now try to create folder with pulsar name in dest_path
   # else, just move files inside that folder
   pulsar_folder_name = dest_path + '/' + pulsar_name
   try:
      os.mkdir(pulsar_folder_name)
   except Exception:
      print('pulsar folder for {} already exists'.format(pulsar_name))

   # move obs data to newly created folder
   try:
      shutil.move(new_path_to_obs, pulsar_folder_name+'/')
      return ierr, pulsar_name, new_path_to_obs
   except Exception as e:
      print(e)
      ierr = -1
      return ierr, pulsar_name, new_path_to_obs


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

      # TO COMPLETE:
      #if ierr == 0:
         #if pname == 'J0437-4715':
            #pipe_reduc(reduction_path)

         #else:
            #pipe_pugliS(reduction_path)


   #


