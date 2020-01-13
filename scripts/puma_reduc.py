#!/usr/bin/env python2
## puma_reduc

#'El hermano lindo de pulsar_reduc'
#Author: Luciano Combi for PuMA
#Date: April 2019

import os
import sys
import argparse

from ConfigParser import SafeConfigParser
import glob
import sigproc
import subprocess
import parfile


# Get command-line arguments
parser = argparse.ArgumentParser(prog='puma_reduc.py',formatter_class=argparse.ArgumentDefaultsHelpFormatter, description='raw data folding with PRESTO')

# - add arguments
parser.add_argument('--ftype', default='timing', type=str, help='folding tag option')
parser.add_argument('--folder', default=os.environ['PWD'], type=str, help='ABSOLUTE PATH where observations are stored and where output will be created')
parser.add_argument('--ptopo', default=None, type=str, help='seed for the topocentric folding period in sec')
parser.add_argument('--par_dirname', default='/opt/pulsar/tempo/tzpar/', type=str, help='path to directory containing .par file')
args = parser.parse_args()

if os.path.isabs(args.folder) is False:
	print('\n FATAL ERROR: folder path is not absolute\n')
	sys.exit(1)

if args.ftype != 'timing' and args.ftype != 'par' and args.ftype != 'search':
	print('\n FATAL ERROR: unknown option for ftype\n')
	sys.exit(1)

if args.ftype == 'search' and args.ptopo is None:
	print('\n FATAL ERROR: you must specify --ptopo for the search mode\n')
	sys.exit(1)

# Check the name of the pulsar and fils
# - Grab name of .fils
fils = glob.glob(args.folder + '/*.fil')
fils.sort()
# Count how many fils are in the folder
nfils = len(fils)

#Warning if there are more than one fil
if nfils <= 0: 
	print('\n ERROR: no *.fil(s) found in ' + args.folder + '\n')
	sys.exit(1)
elif nfils > 1:
	print('WARNING: more than one fil in this folder. I will fold them all.')
    
# Grab name of pulsar from the .fil with sigproc function read_header (dictionary)
fil_dic = sigproc.read_header(fils[0])[0]
pulsarname = fil_dic['source_name'][:-3]
date = fil_dic['rawdatafile'][-19:-4]

# Grab configuration file with same name than the pulsar
configdest = '/opt/pulsar/puma/config/'
configfile = SafeConfigParser()
configfile.read(configdest + pulsarname + '.ini')

# If we are not using manual mode, take all parameters in the config file

# get RFI parameters from .ini
rfitime = configfile.get('rfi','nint')
checkmask = configfile.getboolean('main','rfimask')
checkreuse = configfile.getboolean('rfi','reuse')

# RFIfind process
# Check if we would re-use an existing mask. If not, start rfifind process
output = 'mask_' + pulsarname + '_' + rfitime + '_' + date
rfifind = ['rfifind', '-time', rfitime, '-zerodm', '-o', output]
rfifind.extend(fils)

if checkreuse:
	masks = glob.glob(args.folder + '/*.mask')

    	if len(masks) > 1:
		print('WARNING: More than one mask in the folder! I will use the first one.')
		usingmask = masks[0]
        
    	elif len(masks) == 0:
        	print('WARNING: No mask in the folder. I will make one for you')
        	subprocess.check_call(rfifind, cwd=args.folder)
        	usingmask = output+'_rfifind.mask'
  
    	else:
		usingmask = masks[0]	
    
else:
	subprocess.check_call(rfifind, cwd=args.folder)
	usingmask = output + '_rfifind.mask'


# Folding parameters
nbins = configfile.get('parameters','nbins')
nchan = str(fil_dic['nchans'])
dmsearch= configfile.getboolean('main', 'dmsearch')
gvoutput = configfile.getboolean('main', 'gvoutput')
movephase = configfile.getboolean('main', 'movephase')
phase = configfile.get('parameters','phase')
npart = configfile.get('parameters','npart')
pstep = configfile.get('parameters','pstep')

# Parameters from .par
pardest = args.par_dirname
dotpar = pardest + '/' + pulsarname + '.par'
if os.path.isfile(dotpar) is False:
	print('ERROR: no .par file found in ' + pardest)
	sys.exit(1)

# Prepfold process
# - Seed process:
prepfold = ['prepfold', '-nsub', nchan, '-n', nbins, '-mask', usingmask, '-noxwin']

# Check what to use and complete process
if not dmsearch:
	prepfold.append('-nodmsearch')
   
if movephase:
	prepfold.extend(('-phs', phase))
    
if args.ftype == 'timing':
	prepfold.extend(('-timing', dotpar))
elif args.ftype == 'par':
	prepfold.extend(('-par', dotpar, '-pstep', pstep, '-npart', npart))
elif args.ftype == 'search':
	prepfold.extend(('-topo', '-p', args.ptopo, '-pstep', pstep, '-npart', npart))

# Output & Input
output = 'prepfold_' + args.ftype + '_' + date
prepfold.extend(('-o', output, '-filterbank'))
prepfold.extend(fils)


# RUN PREPFOLD
subprocess.check_call(prepfold, cwd=args.folder)
