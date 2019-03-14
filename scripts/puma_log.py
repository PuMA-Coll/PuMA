
# coding: utf-8

# In[3]:


#!/usr/bin/env python


# # PuMA log

# ### Python script for .log file generation.
# 
# This script is intended to gain control and check systematics in all PuMA observations. 
# 
# Can be adapted for particular projects. 
# 
# It is expected to run after the pulsar_reduc routine. It works under the pulsar_reduc organisation scheme: /pulsar_name/yearmonthday/AX/obs# where AX could be A1 or A2 with (a) pulsar .fil files (b) calibration .fil files (c) .pfd files (d) .mask files.
# 
# 
# Version: 0.1
# Date: 1/4/19
# authors: Luciano Combi

# In[1]:


# Import standard packages

import numpy as np
import astropy 
from astropy.io import ascii
from astropy.table import Table, Column, MaskedColumn
from astropy import units as u
import subprocess
# We will need to execute shell scripts

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
from os.path import dirname
sys.path.append('/opt/pulsar/PyPulse/pypulse/')


# In[2]:


# Let us enable a no timing option and a help. Future options of calibration an pazi

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-n", "--notoa", action="store_true",
                    help="save log and moves folders without obtaining TOAs")
args = parser.parse_args()

if args.notoa:
    antenna = 'N'
    print('Saving log and moving files without obtaining toas')
else: antenna = 'Y'


# In[2]:


# Extract number of parts of raw files

rawname = glob.glob('*.fil')
firstfil= read_header(rawname[0])[0]


# In[5]:


# Observation details (from the first filterbank if there are more than one)

#Formating for coordinates:

def coord_format():
    
    scoord=""
    ra = str(firstfil['src_raj'])
    dec = str(firstfil['src_dej'])
    
    for coord in ra, dec:
        
        pos = coord.find('.')
     
        if pos ==5:
            coord = '0'+coord[:pos-4]+':'+coord[pos-4:pos-2]+':'+coord[pos-2:]
        else:
            coord= coord[:pos-4]+':'+coord[pos-4:pos-2]+':'+coord[pos-2:]
            
        scoord+= coord
    
    return scoord

# Parameters of observation

telid = firstfil['telescope_id']
scoord = coord_format()
backend = firstfil['machine_id']
tsample = firstfil['tsamp']
tstart = firstfil['tstart']
sourceantenna = firstfil['rawdatafile']
pulsar= sourceantenna[:len(sourceantenna)-3]


# In[6]:


# Open pfd files and masks.

pfd = glob.glob('*.pfd')[0]
maskname = glob.glob('*.mask')[0]


# In[7]:


# Correct metadata information. We should include a proper name function here (e.g. for vela)

# Type
subprocess.call(['psredit', '-c','type=Pulsar','-m',pfd], shell=True)

# Coordinates
subprocess.check_output(['psredit', '-c','coord='+scoord,'-m',pfd]) 
# Source
subprocess.check_output(['psredit', '-c','name='+pulsar,'-m',pfd]) 
# Reciever
if telid == '19':
    subprocess.check_output(['psredit', '-c','rcvr:name=AI','-m',pfd]) 
else:
    subprocess.check_output(['psredit', '-c','rcvr:name=AII','-m',pfd]) 
# Backend
subprocess.check_output(['psredit', '-c','be:name=Ettus-B120','-m',pfd]) 
# Proyect
subprocess.check_output(['psredit', '-c','obs:projid=PuMA','-m',pfd]) 


# In[8]:


# In this step we should include a zapping option and calibration. 
# Since we do not have yet two polarization we skip calibration.


# In[9]:


# Save all relevant data from the pfd using rfifind and psrchive.
    
arch = psrchive.Archive_load(pfd)
maskrfi = rfifind.rfifind(maskname)
mjd = arch.start_time()


# In[10]:


#Usable % of the observations due to RFI. We do not take into account pazi filters.

maskrfi.read_bytemask()
maskarr = maskrfi.bytemask
nbadint = float(np.count_nonzero(maskarr))
ntotalint = float(len(maskrfi.goodints))*float(len(maskrfi.freqs))


# In[11]:


# Parameters (we also have nobs and coords)

datemjd = [mjd.in_days()]
pulsar = sourceantenna[:len(sourceantenna)-3]
antenna = [arch.get_receiver_name()]
bw = [arch.get_bandwidth()]
freq = [arch.get_centre_frequency()]
nbin = [arch.get_nbin()]
nchan = [arch.get_nchan()]
pol = [arch.get_npol()]
calyn = [arch.get_poln_calibrated()]
snr = [subprocess.check_output(['psrstat','-jTFp','-Q','-q','-c','snr',pfd]).strip('\n') .strip(' ')]
obstime = [arch.integration_length()/60]
rfitime = [maskrfi.dtint]
usablepercent = [nbadint/ntotalint*100]


# In[13]:


#Define table
logvar = [pulsar, 
          tstart, 
          antenna, 
          scoord, 
          bw, 
          freq,
          tsample,
          nbin, 
          nchan, 
          pol, 
          calyn, 
          snr, 
          obstime,
          datemjd,
          rfitime, 
          usablepercent,
          backend]
lognames = ['Name of pulsar', 
            'Date', 
            'Coordinates', 
            'Antenna', 
            'BW', 
            'Freq',
            'Time Sample'
            'NBin',
            'NFchanel',
            'NPol',
            'Calibrated?',
            'S/N',
            'Observation Time',
            'Date (MJD)'
            'Time of RFI Mask',
            '% of RFI in obs',
           'Backend']


# In[ ]:


# Do the log with the current information. Use astropy table. 
destination='./../../../'
file_name = pulsar+'log.txt'
if not os.path.exists(destination+file_name):
    table = Table(logvar, names = lognames)
    ascii.write(table,destination+file_name)
    print ('*** A new pulsar log table for '+ file_name+ ' has been created ***') 
else:
    table = ascii.read(destination+file_name)
    table.add_row(logvar)
    ascii.write(table,destination+file_name)    

