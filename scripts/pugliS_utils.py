"""
Utility functions for pipe_pugliS
"""

import os
import sys
import glob
import shutil


def move_observation(path_to_obs='', dest_path=''):
    '''
    this function moves all files from an observation done by each
    antenna into the database folder for later reduction
    '''

    ierr = 0

    if os.path.isfolder(path_to_obs) is False:
        print('\n FATAL ERROR: path_to_obs does not exist')
        ierr = -1
        return ierr

    # skel: path_to_obs = '.../upload/date'

    # grab pulsar name from *.iar if it exist, else use the *.fil file
    if os.path.isfile(path_to_obs + '*.iar'):
        iar_fname = glob.glob('*.iar')[0]
        pulsar_name = iar_fname.split('_')[0]

    elif os.path.isfile(path_to_obs + '*.fil'):
        fil_fname = glob.glob('*.fil')[0]
        pulsar_name = fil_fname.split('_')[1]

    # now try to create folder with pulsar name in dest_path
    # else, just move files inside that folder
    pulsar_folder_name = dest_path + '/' + pulsar_name
    try:
        os.mkdir(pulsar_folder_name)
    except Exception:
        print('pulsar folder already exists')

    # move obs data to newly created folder
    try:
        shutil.move(path_to_obs, pulsar_folder_name)
    except Exception as e:
        print(e)
        ierr = -1
        return ierr


def do_many_moves(path_to_obs, dest_path):

    ierr = 0

    if os.path.isfolder(path_to_obs) is False:
        print('\n FATAL ERROR: path_to_obs does not exist')
        ierr = -1
        return ierr


    
