#!/usr/bin/env python3
#
# PuMA select pfds
# Python script for selecting the high SNR observations for high-precision timing
# Author: Santiago del Palacio (based in puma_toa.py by L. Combi)
# 2019

# We will need to execute shell scripts

import subprocess
import sys
import glob
import os
import shutil
#import parfile

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("snr_min", action='store', type=float, help="Indicate minimum SNR to keep observations", default='10')
args = parser.parse_args()
snr_min = args.snr_min

# Select all available pfds:

pfd_folder = os.getcwd()
pfdtype = '*.pfd'
pfds = glob.glob(pfdtype)
pfds.sort()

bad_pfd_folder = pfd_folder+'/no_tan_malas'
if not os.path.isdir(bad_pfd_folder):
    os.makedirs(bad_pfd_folder)

# Look which pfds have a low SNR and move them to another folder

for pfd in pfds:
	#check_output returns a bytes object, decode transforms to string
    salida = subprocess.check_output(['psrstat','-Q','-jTFD','-c','snr',pfd]).decode("utf-8")
    a,snr = salida.split()
    print(snr)

    if float(snr) < snr_min:
        shutil.move(pfd, bad_pfd_folder)
        polycos = pfd + '.polycos'
        bestprof = pfd + '.bestprof'
        if os.path.exists(polycos):
            shutil.move(polycos, bad_pfd_folder)
        if os.path.exists(bestprof):
            shutil.move(bestprof, bad_pfd_folder)

    	#try:
    		
