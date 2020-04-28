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

snr_max = 0.0
pfd_max = ''
for pfd in glob.glob("*pfd", recursive=True):
    arch = psrchive.Archive_load(pfd)
    snr_string = subprocess.check_output(['psrstat','-j','pF','-c','snr',arch.get_filename()])
    snr = float(snr_string[snr_string.index('snr')+4:-1])
    if snr > snr_max:
        snr_max = snr
        pfd_max = pfd

print('The best observation has S/N = ', snr_max)
arch = psrchive.Archive_load(pfd_max)

# Make a smooth profile with the best observation

subprocess.check_output(['psrsmooth','-n','-e','std',pfd])
