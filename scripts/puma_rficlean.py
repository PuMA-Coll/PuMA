#!/usr/bin/env python

## PuMA rficlean
# This script runs rficlean in all folders within the current ms pulsar folder
# Version: 0.1
# Date: 07/06/20
# author: Santiago del Palacio

import subprocess
import glob
import time
import os

# List all folders with observations
folders = glob.glob('2020-07*A1/obs*')
# For non-ms pulsar: folders = glob.glob('*')

# Check how long does it take to rfiClean all files
start = time.time()

# Call rficlean for each (just one for ms pulsars) .fil file in obs folder
print('\n I will run rfiClean in ' + str(len(folders)) + ' folders')
i = 0
for folder in folders:
   i += 1
   print('\n rfiClean-ing ' + str(i) + '/' + str(len(folders)) )
   fil = glob.glob(folder + '/*.fil')[0] # For non-ms pulsars we should iterate over all .fil files
   input_name = fil.split('/')[-1]
   output_name = 'CLEAN' + input_name
   rficlean_cmd = ['rficlean', '-o', output_name, input_name]
   subprocess.check_call(rficlean_cmd, cwd=folder)


# exit with success printing duration
end = time.time()
hours, rem = divmod(end-start, 3600)
minutes, seconds = divmod(rem, 60)
print('\n rfiClean process completed in {:0>2}:{:0>2}:{:05.2f}\n'.format(int(hours), int(minutes), seconds))

# Move the observations to a new folder
dest = '/home/jovyan/work/shared/Data/J0437-4715/Prueba_rficlean/A1/con_rficlean'

print('\n I will move ' + str(len(folders)) + ' folders')
for folder in folders:
   new_dir = dest + '/' + folder
   print('Creating directory ' + new_dir)
   os.makedirs(new_dir)
   clean_fil = glob.glob(folder + '/CLEAN*')[0]
   new_fil = new_dir + '/' + clean_fil.split('/')[-1]
   print('Renaming file ' + clean_fil + ' as ' + new_fil)
   os.rename(clean_fil, new_fil)

#reduction_folders = glob.glob('*/*obs*')
#reduc_cmd = ['puma_reduc.py']
#for folder in reduction_folders:
#   subprocess.check_call(reduc_cmd, cwd=folder)
