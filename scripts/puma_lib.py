import os
import sys
sys.path.insert(1,os.path.join(sys.path[0], '/opt/pulsar/puma/scripts/'))

import sigproc
import glob
from pipe_red_trigger import glitch_search

class Observation(object):
    """ This is the main class that represents an observation from a single antenna."""

    def __init__(self, path2dir=''):
        self.dir_path = path2dir
        self.pname, self.antenna, self.mjd, self.nchans = self.get_pulsar_parameters()
        self.glitch = False
        self.red_alert = False
        self.blue_alert = False
        self.par_dir = '/opt/pulsar/tempo/tzpar/'
        self.par = '/opt/pulsar/tempo/tzpar/' + self.pname + '.par'


    def get_pulsar_parameters(self):
        # select .fil file
        fils = glob.glob(self.dir_path + '/*.fil')      
        fil = fils[0]

        # grab name of pulsar from the .fil with sigproc function read_header (dictionary)
        fil_dic = sigproc.read_header(fil)[0]
        pname = fil_dic['source_name'][:-3]
        antenna = fil_dic['source_name'][-2:]
        mjd = fil_dic['tstart']
        nchans = fil_dic['nchans']

        return pname, antenna, mjd, nchans


    def do_glitch_search(self, threshold):
        self.red_alert, self.jump = glitch_search(folder=self.dir_path, 
            par_dirname=self.par_dir, ncores=2, thresh=threshold)
