#!/usr/bin/env python2


## PuMA toa
# ### Python script for Time of Arrivals generation
# This script is intended to obtain a reasonable set of TOAs 
# 
# Version: 0.1
# 
# Date: 11/3/19
# 
# author: Luciano Combi


# Import standard packages

import numpy as np
import subprocess

# We will need to execute shell scripts

import sys
import glob
import os
import shutil
import re
import getopt


# Import psrchive and rfifind libraries

import psrchive
from sigproc import *


# In[6]:


# Let us enable a no timing option and a help. Future options of calibration an pazi

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-t", "--template", action="store_true", default=False,
                    help="use another existing template in timingfolder")
parser.add_argument("-r", "--rewrite", action="store_true", default=False,
                    help="replace values in total toa if needed")
parser.add_argument("-f","--flag",action='store', type=str, help="additional flag", required=False)

args = parser.parse_args()


# In[81]:


# Open pfd.

pfd = glob.glob('*tim*.pfd')[0]

# Set useful tags (only use this for old observations)

directory = os.getcwd()
splitdir = directory.split('/')

if splitdir[7] == 'A1':
	subprocess.check_output(['psredit', '-c','site=IAR1','-m',pfd])
else:
        subprocess.check_output(['psredit', '-c','site=IAR2','-m',pfd])

subprocess.check_output(['psredit', '-c','name='+splitdir[5],'-m',pfd])


arch = psrchive.Archive_load(pfd)
source = arch.get_source()



# In[82]:


# Check if timing foler exist for the pulsar. If not, create it.

if arch.get_telescope() == 'IAR1':
    timingfolder= './../../../timing/A1/'
elif arch.get_telescope() == 'IAR2':
    timingfolder='./../../../timing/A2/'
else:
    print('The site of the telescope does not seem to be IAR')
    exit()


# In[14]:


# Choose the template for folding

if args.template:
    
    if os.path.exists(timingfolder+source+'.optional.std'):
        usingtemplate = timingfolder+source+'.optional.std'
    else:
        print ('WARNING: there is no {}.optional.std! Timing will fail'.format(source))
else:
    
    usingtemplate= timingfolder+source+'.std'

print (usingtemplate)

# In[15]:


# Define TOAs destination:

totaltoa =timingfolder+'suball.tim'
totaltoaone=timingfolder+'oneall.tim'
singletoa= arch.get_filename()+'.tim'
temptoa = timingfolder+'tempall.tim'
backuptoa = timingfolder+'backupall.tim'

# In[20]:


# Default option is rewrite if there are existing TOAs in all.

if args.rewrite: #Check if there is a all.fil
    
    f = open(totaltoa,'r')
    tempf = open(temptoa,'wb') #Create a new temporary toa file

    for line in f:
        tmp = line.split()
        a = " ".join(tmp)
        if tmp[0] == pfd:
            tempf.writelines(a)
            tempf.write('\n')

    tempf.close()
    f.close()
    
    shutil.copy(totaltoa,backuptoa)
    shutil.copy(temptoa, totaltoa)
    os.remove(temptoa)


# In[21]:


# if JUMP flags are on, check the number of JUMP and write a new flag.

if args.flag == 'JUMP':
    
    if os.path.exists(totaltoa):
        with open(totaltoa,'r') as f:
            lines = f.read().splitlines()
            last_line = lines[-1]
            flagposition = last_line.split()[5]
            nflag= int(flagposition[len(args.flag):])
    
        patflag = args.flag+str(nflag+1) #Increase the corresponding flag number.
    else:
        patflag = args.flag+str(1)
else:
    patflag=' '	
    
# In[28]:


# Define arguments
def pat_args(nsubint):
    return '-A PGS -f "tempo2" -X "{}" -s {} -jFD -j "T {}" '.format(patflag,usingtemplate,nsubint)


# In[32]:


# Define general output
pat_output_general= '>> {}'.format(totaltoa)
pat_output_generalone= '>> {}'.format(totaltoaone)

# Define individual output
pat_output_individual= '> {}'.format(singletoa)


# In[78]:


# Do the pat for singleTOA to check how many intergrations are worth doing:

tolerance = 3 # In useg
moresubs= True
subints= [30,15,10,5,3,2,1]
i=0

while moresubs:
    
    subprocess.call(['pat '+pat_args(subints[i])+pfd+pat_output_individual], shell=True)
        
    with open(singletoa,'r') as f:
        next(f)
        if all(float((x.split())[3])<tolerance for x in f):
            moresubs= False
	    break	
        elif subints[i]==1: 
            print('Complete observation has error > tolerance')
	    break
        else:
            i+=1


# In[79]:


# Do the pat for totalTOAs

subprocess.call(['pat '+pat_args(subints[i])+pfd+pat_output_general], shell=True)

subprocess.call(['pat '+pat_args(subints[1])+pfd+pat_output_generalone], shell=True)

