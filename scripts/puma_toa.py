#!/usr/bin/env python2
# PuMA toa
# Python script for obtaining time of arrivals
# Author: Luciano Combi.
# 2019

# We will need to execute shell scripts

import subprocess
import sys
import glob
import os
import shutil

# Import psrchive

import psrchive

# Open pfds.

pfdtype = '*tim*.pfd'
pfds = glob.glob(pfdtype)
pfds.sort()

arch = psrchive.Archive_load(pfds[0])
pulsarname= arch.get_source()

# Choose a given template named 'pulsar.pfd.std'
usingtemplate = './timing/{}.pfd.std'.format(pulsarname)

# Define arguments.
def pat_args(patflags, nsubint):
    return '-A PGS -f "tempo2" {} -s {} -jFD -j "T {}" '.format(patflags,usingtemplate,nsubint)

totaltoa= './timing/total.tim'
singletoa= './timing/single.tim'

# Define general output
pat_output_total= '>> {}'.format(totaltoa)

# Define individual output
pat_output_individual= '>> {}'.format(singletoa)

# Choose a given number of subintegrations to obtain toa and a flag:

nsubints= 10
flags= '-X "-section "'

# Loop over all the observatins:

j=0
for pfd in pfds:
    subprocess.call(['pat '+pat_args(flags+str(j),nsubints)+pfd+pat_output_total], shell=True)
    subprocess.call(['pat '+pat_args(flags+str(j),1 )+pfd+pat_output_individual], shell=True)
    j+=1
