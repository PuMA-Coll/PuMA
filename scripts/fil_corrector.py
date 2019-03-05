
# coding: utf-8

# In[1]:


#!/usr/bin/env python


# ## filterbank corrector

# Authors: L. Combi & F. García
# 
# Date: 11/02/19
# 
# This script corrects the time stamp of a raw Filterbank observation.

# In[1]:


import os, sys
from sigproc import *
import numpy as np
from astropy.time import Time
import glob
import argparse
from datetime import datetime
from datetime import timedelta


# In[ ]:


# options to correct time stamp antenna

parser = argparse.ArgumentParser()

parser.add_argument("-t", "--correction", action="store_true", 
                    help="corrects antenna")
parser.add_argument("antenna", type=int, choices=[1,2],
                    help="antenna")
args = parser.parse_args()

if args.antenna==1:
    tid=19
elif args.antenna ==2:
    tid=20


# In[ ]:


# Make a list of all availabe Filterbank files in the folder

fils = glob.glob('*.fil')


# In[ ]:


# For correcting timestemp
# Make a dic of all the starting time-stamps (ts)

tsold = {}

for x in fils:
    
       tsold[x] = read_header(x)[0]['tstart']

# We transform the ts from MJDs to isot format, we correct the non zero values and we re reconvert.
# Save them in a new dictionary.

tsnew= {}

for i in range(len(fils)):
    
        tmp= Time(tsold[fils[i]], format='mjd', scale='utc', precision=9)
        
        a = tmp.datetime

        # The script round the second but place here what you want to do with this.
        
        if a.microsecond > 900000:
                b = a - timedelta(microseconds=a.microsecond) + timedelta(seconds=1)
        else:
                b = a - timedelta(microseconds=a.microsecond)

        newdt = Time(b, format='datetime', scale = 'utc', precision=9)
        
        
        tsnew[fils[i]] = newdt.mjd


# In[ ]:


for i in range(len(fils)):
    
    f = open(fils[i], 'rb')
    
    filhdr = {}
    
    newhdr = ""
    
    outfile = open('tscorrected'+fils[i],'wb')
    
    while 1:                                                              
               
            param, val = read_hdr_val(f, stdout=False)                        
                
            filhdr[param] = val                                     
                                                                               
            #changing these header parameters. 
      
            if param=="machine_id":  val = 23
            if param=='telescope_id': val = tid
            if param=='tstart':
                if args.correction:
                    val = tsnew[fils[i]]
                else:
                    val= tsold[fils[i]]
     
             # Append to the new hdr string
            newhdr += addto_hdr(param, val)
     
             # Break out of the loop if the header is over
            if param=="HEADER_END":  break
    
    outfile.write(newhdr)
    
    hdrlen = f.tell()
    
    numbytes = os.stat(fils[i])[6] - hdrlen
    
    m=0
    
    while m < numbytes:
        
        towrite = f.read(1000000)
        m += 1000000
        outfile.write(towrite)
    
    towrite = f.read(numbytes-f.tell())
    
    outfile.write(towrite)
    
    outfile.close()   

