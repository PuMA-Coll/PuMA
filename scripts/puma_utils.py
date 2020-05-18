"""
Utility functions for pipe_pugliS
"""

import os
import sys
import glob
import shutil
import pandas as pd


def copy_db(pname, antenna, path2ini, path2end):
   '''
   Copy files useful for database (.ps converted to png, pfd and polycos)
   '''
   
   path2last = path2end + '/last_obs/'
   path2pngs = path2end + '/' + pname + '/pngs/'
   path2pfds = path2end + '/' + pname + '/pfds/' 
   # Create the specific directory for the pulsar if it does not exist
   try:
      os.makedirs(path2pngs)
      os.makedirs(path2pfds)
   except Exception:
      print('pulsar database directory already exists')

   ps_mask = glob.glob(path2ini + '/*mask*.ps')[0]
   pngfile = ps_mask[:-2] + 'png'
   os.system('convert -density 300 -rotate 90 -alpha off ' + ps_mask + ' ' + pngfile)

   png_files = glob.glob(path2ini + '/*.png') 
   pfd_files = glob.glob(path2ini + '/*.pfd') 
   polycos_files = glob.glob(path2ini + '/*.polycos') 

   # Copy all png files and save their paths in a list of pngs
   pngs = []
   for png in png_files:
      pngs = pngs + [png.split('/')[-1]]
      shutil.copy(png, path2pngs)
      # Make a copy in last_obs directory taking out the date information
      if 'mask' in png:
         # Only the first page of the mask is needed
         if '-0' in png:
            shutil.copy(png, path2last + pname + '_' + antenna + '_mask.png' )
      else:
         if 'par' in png:
            shutil.copy(png, path2last + pname + '_' + antenna + '_par.png' )
         elif 'timing' in png:
            shutil.copy(png, path2last + pname + '_' + antenna + '_timing.png' )
         else:
            print('What is this file: ' + png + '?!')

   # Copy pfds and polycos and save their paths in a list of pngs
   pfds = []
   for pfd in pfd_files:
      pfds = pfds + [pfd.split('/')[-1]]
      shutil.copy(pfd, path2pfds)

   polycoss = []
   for polycos in polycos_files:
      polycoss = polycoss + [polycos.split('/')[-1]]
      shutil.copy(polycos, path2pfds)

   return pngs, pfds, polycoss


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

def write_pugliS_info_jason(path2pugliese,obs):
   """ Write information in JSON format"""
   PSR = path2pugliese + '/' + obs.pname + '/' + obs.pname + '.json'

   try:
       df = pd.read_json(PSR, orient='records')
   except:
       df = pd.DataFrame()

   #WE HAVE TO CHECK IF AND OBSID EXISTS TO REPLACE IT INSTEAD OF APPEND

   df_new = df.append(obs.__dict__, ignore_index=True)

   # guardar los pandas como json
   df_new.to_json(path_or_buf=PSR, orient='records', date_format='iso', double_precision=14)
   return
