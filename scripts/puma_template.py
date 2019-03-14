#!/usr/bin/env python


## PuMA template
## Python script for template generator
# This script generates new templates from existing observation.
# Version: 0.1
# Date: 11/3/19
# author: Luciano Combi


# Import standard packages

import numpy as np

# We will need to execute shell scripts

import subprocess
import sys 
import glob
import os
sys.path.append('/opt/pulsar/')
import shutil
import getopt


# Import psrchive and rfifind libraries

import psrchive 
import rfifind
from sigproc import *

# Open pfd.

pfdtype = '*tim*.pfd'
pfd = glob.glob(pfdtipe)[0]

# Rudimentary labeling

directory = os.getcwd()
splitdir = directory.split('/')

if splitdir[7] == 'A1':
        subprocess.call(['psredit', '-c','site=IAR1','-m',pfd])
else:
        subprocess.call(['psredit', '-c','site=IAR2','-m',pfd])

subprocess.call(['psredit', '-c','name='+splitdir[5],'-m',pfd])

# Take parameters from pfd

arch = psrchive.Archive_load(pfd)
source = arch.get_source()


# Check if timing foler exist for the pulsar. If not, create it.

if arch.get_telescope() == 'IAR1':
    timingfolder= './../../../timing/A1/'
elif arch.get_telescope() == 'IAR2':
    timingfolder='./../../../timing/A2/'
else:
    print('The site of the telescope does not seem to be IAR')
    exit()
    
if not os.path.exists(timingfolder):
    os.makedirs(tfolder)


# Create template variables:

totalobservation = timingfolder+source+'.pfd'

tmp= timingfolder+'tmp.pfd'


# Check if you have a seed:

if not os.path.exists(totalobservation):
    
    print('WARNING: this would be the first observation to create template. You should not do timing with this one')
    shutil.copy(pfd,totalobservation)


# Add current pfd to total pfd into a tmp.pfd
    
subprocess.check_output(['psradd', '-F','-P',pfd,totalobservation,'-o',tmp]) 


# Compute the total snr of tmp and total    
#totalsnr =float(subprocess.check_output(['psrstat','-jTFp','-Q','-q','-c','snr',totalobservation]).strip('\n') .strip(' '))
#tmpsnr =float(subprocess.check_output(['psrstat','-jTFp','-Q','-q','-c','snr',tmp]).strip('\n'))
# Keep the one with the biggest snr.
#if totalsnr < tmpsnr:
#    os.remove(totalobservation)
#    os.rename(tmp, totalobservation)
#else:  
#    os.remove(tmp)
 
# Create standard template:

subprocess.output(['psrsmooth', '-n','-e','std',totalobservation])  

