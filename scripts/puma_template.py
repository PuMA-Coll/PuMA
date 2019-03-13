
# coding: utf-8

# In[3]:


#!/usr/bin/env python


# # PuMA template

# ### Python script for template generator
# 
# This script generates new templates from existing observation.
# 
# Version: 0.1
# 
# Date: 11/3/19
# 
# author: Luciano Combi

# In[1]:


# Import standard packages

import numpy as np
import matplotlib.pyplot as mp

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


# In[2]:


# Open pfd.

pfd = glob.glob('*.pfd')[0]
arch = psrchive.Archive_load(pfd)
source = arch.get_source()


# In[3]:


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


# In[4]:


# Create template variables:

totalobservation = timingfolder+source+'.pfd'

tmp= timingfolder+'tmp.pfd'


# In[6]:


# Check if you have a seed:
if not os.path.exists(totalobservation):
    
    print('WARNING: this would be the first observation to create template. You should not do timing with this one')
    shutil.copy(pfd,totalobservation)


# In[8]:


# Add current pfd to total pfd into a tmp.pfd
    
subprocess.call(['psradd', '-F','-P',pfd,totalobservation,'-o',tmp]) 


# In[9]:


# Compute the total snr of tmp and total    
totalsnr =float(subprocess.check_output(['psrstat','-jTFp','-Q','-q','-c','snr',totalobservation]).strip('\n') .strip(' '))
tmpsnr =float(subprocess.check_output(['psrstat','-jTFp','-Q','-q','-c','snr',tmp]).strip('\n'))
    


# In[13]:


# Keep the one with the biggest snr.

if totalsnr < tmpsnr:
    os.remove(totalobservation)
    os.rename(tmp, totalobservation)
else:  
    os.remove(tmp)
        


# In[16]:


# Create standard template:
subprocess.call(['psrsmooth', '-n','-e','std',totalobservation])  

