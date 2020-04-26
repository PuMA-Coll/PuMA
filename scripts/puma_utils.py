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
   if (path_to_obs[-2:] == 'A1' or path_to_obs[-2:] == 'A2'):
      new_path_to_obs = path_to_obs
   else:
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
   path_to_reduc = pulsar_folder_name + '/' + new_path_to_obs.split('/')[-1] + '/'
   try:
      shutil.move(new_path_to_obs, pulsar_folder_name+'/')
      return ierr, pulsar_name, path_to_reduc
   except Exception as e:
      print(e)
      ierr = -1
      return ierr, pulsar_name, path_to_reduc



