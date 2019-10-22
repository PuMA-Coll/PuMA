#!/usr/bin/env python2
#
# Python script for converting .par files from TCB to TDB units
# Author: Santiago del Palacio (based in puma_toa.py by L. Combi)
# 2019

# We will need to execute shell scripts
import subprocess
import sys
import glob
import os
import shutil

# Select all available pars:
par_folder = os.getcwd()
partype = '*.par'
pars = glob.glob(partype)
pars.sort()

ATNF_par_folder = par_folder+'/ATNF_pars'

if not os.path.exists(ATNF_par_folder):
    os.makedirs(ATNF_par_folder)


# Make a copy of the .par files as _TCB, run the tempo2 converter (and store as _TDB?)

for par in pars:
    
    shutil.copy(par,ATNF_par_folder)

    # Transform TCB to TDB (have to do it twice to work)
    subprocess.call(['tempo2','-gr','transform',par,'temp.par','back'])
    subprocess.call(['tempo2','-gr','transform','temp.par',par,'back'])

    # Read in the file
    with open(par, 'r') as file:
        filedata = file.read()

    # Replace the target strings: 
    # TRES -nan --> TRES 10000 (also changes chi2r)
    filedata = filedata.replace('-nan', '10000')
    # Comment out the CLK line
    filedata = filedata.replace('CLK', '#CLK')
    # Fix the pulsar name
    filedata = filedata.replace('PSRJ', 'PSRB')
#    filedata = filedata.add('PSRJ	', os.path.splitext(par)[0])

    # Write the file out again
    with open(par, 'w') as file:
    	file.write("PSRJ" + "\t" + os.path.splitext(par)[0]+ "\n")
        file.write(filedata)
        

os.remove('temp.par')

