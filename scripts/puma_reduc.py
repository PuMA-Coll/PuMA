#!/usr/bin/env python2
## puma_reduc

#'El hermano lindo de pulsar_reduc'
#Author: Luciano Combi for PuMA
#Date: April 2019

from ConfigParser import SafeConfigParser
import glob
import sigproc
import subprocess
import parfile

# Check the name of the pulsar and fils

# Grab name of .fils

fils = glob.glob('*.fil')

# Count how many fils are in the folder
nfils = len(fils)

#Warning if there are more than one fil
if nfils > 1:
    print ('WARNING: more than one fil in this folder. I will fold them all.')
    
# Grab name of pulsar from the .fil with sigproc function read_header (dictionary)

fil_dic= sigproc.read_header(fils[0])[0]
pulsarname = fil_dic['source_name'][:-3]
date= fil_dic['rawdatafile'][-19:-4]

# Grab configuration file with same name than the pulsar

configdest = '/opt/pulsar/puma/config/'
configfile = SafeConfigParser()
configfile.read(configdest+pulsarname+'.ini') 

# If we are not using manual mode, take all parameters in the config file

# RFI parameters
rfitime = configfile.get('rfi','nint')
checkmask = configfile.getboolean('main','rfimask')
checkreuse = configfile.getboolean('rfi','reuse')

# Folding parameters

nbins = configfile.get('parameters','nbins')
nchan = str(fil_dic['nchans'])
dmsearch= configfile.getboolean('main', 'dmsearch')
gvoutput = configfile.getboolean('main', 'gvoutput')
movephase = configfile.getboolean('main', 'movephase')
phase = configfile.get('parameters','phase')


# Config parameters. Define search parameters if timing is not used:
checktiming= configfile.getboolean('main','timing')

if not checktiming:
    npart = configfile.get('parameters','npart')
    pstep = configfile.get('parameters','pstep')

# Parameters from .par
pardest = '/opt/pulsar/tempo/tzpar/'
dotpar = glob.glob(pardest+pulsarname+'.par')


# RFIfind process

# Check if we would re-use an existing mask. If not, start rfifind process
rfifind = ['rfifind','-time',rfitime,'-zerodm','-o',output]
rfifind.extend(fils)

if checkreuse:
    
    maskes = glob.glob('*.mask')

    if len(maskes)>1:
        
        print('WARNING: More than one mask in the folder! I will use the first one.')
        usingmask = maskes[0]
        
    elif len(maskes)==0:
        
        print('WARNING: No mask in the folder. I will make one for you')
        output= 'mask_'+pulsarname+'_'+rfitime
        subprocess.check_call(rfifind)      
        usingmask = output+'_rfifind.mask'
  
    else:
	usingmask = maskes[0]	
    
else:
    
    output= 'mask_'+pulsarname+'_'+rfitime
    subprocess.check_call(rfifind)      
    usingmask = output+'_rfifind.mask'

# Prepfold process

#Seed process:
prepfold= ['prepfold','-nsub',nchan, '-n', nbins,'-mask',usingmask,'-noxwin']

# Check what to use and complete process

if not dmsearch:
    prepfold.append('-nodmsearch')
    
if movephase:
    prepfold.append('-phs')
    prepfold.append(phase)
    
if checktiming:
    prepfold.append('-timing')
    prepfold.append(dotpar[0])
    
else:
    prepfold.append('-par')
    prepfold.append(dotpar[0])
    prepfold.append('-pstep')
    prepfold.append(pstep)
    prepfold.append('-npart')
    prepfold.append(npart)

# Output & Input

output = 'prepfold_'+date
prepfold.append('-o')
prepfold.append(output)
prepfold.append('-filterbank')
prepfold.extend(fils)

# RUN PREPFOLD

subprocess.check_call(prepfold)
