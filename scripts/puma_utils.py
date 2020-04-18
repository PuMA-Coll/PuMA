"""
Utility functions for pipe_pugliS
"""

import os
import sys
import glob
import shutil

#need to import pipe_pugliS and pipe_reduc?

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

    # grab pulsar name and antenna from *.iar file if it exist, else use the *.fil file
    if len(glob.glob(path_to_obs + '/*.iar')) > 0:
        if os.path.isfile(glob.glob(path_to_obs + '/*.iar')[0]):
            iar_fname = glob.glob(path_to_obs + '/*.iar')[0]
            pulsar_name = iar_fname.split('_')[0].split('/')[-1]
            antenna = iar_fname.split('_')[1].split('.')[0]

    elif len(glob.glob(path_to_obs + '/*.fil')) > 0:
        if os.path.isfile(glob.glob(path_to_obs + '/*.fil')[0]):
            fil_fname = glob.glob(path_to_obs + '/*.fil')[0]
            pulsar_name = fil_fname.split('_')[1].split('/')[-1]
            antenna = fil_fname.split('_')[2]

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


