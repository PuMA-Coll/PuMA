#!/usr/bin/env python

## PuMA template
## Python script for template generator
# This script generates new templates from existing observation.
# Version: 0.1
# Date: 11/3/19
# author: Luciano Combi, Eduardo Gutierrez

# We will need to execute shell scripts

import subprocess
import sys
import glob
import os
import psrchive

# Search for the highest S/N observation

pwd = os.getcwd()
snr_max = 0.0
pfd_max = ''
pfds = [pfd for x in os.walk('.') for pfd in glob.glob(os.path.join(x[0], '*.pfd'))]

if pfds == []:
    print('There are no pfds in this folder!')

else:
    for pfd in pfds:
        arch = psrchive.Archive_load(pfd)
        snr_string = subprocess.check_output(['psrstat','-j','pF','-Q','-q','-c','snr',arch.get_filename()])
        snr = float(snr_string)
        if snr > snr_max:
            snr_max = snr
            pfd_max = pfd

    aux_index = pfd_max.index('20')
    print('The best observation is from ' + pfd_max[aux_index:aux_index+8] + ' and has S/N = '+str(snr_max)+'\n')
    arch = psrchive.Archive_load(pfd_max)

    # Make a smooth profile with the best observation

    subprocess.check_output(['psrsmooth', '-n', '-e', 'std', pfd_max])
    fname = arch.get_filename()[1:] + '.std'
    new_fname = 'J' + fname.split('_')[-1]
    subprocess.check_output(['mv', os.getcwd()+arch.get_filename()[1:] + '.std', pwd + '/' + new_fname])

