#!/usr/bin/env python2
#
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
import parfile

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("name", action='store', type=str, help="write name of the pulsar")
parser.add_argument("--s", action='store', type=str, help="choose subintegration number", default='5')
args = parser.parse_args()



# Open pfds.

pfdtype = '*.pfd'
pfds = glob.glob(pfdtype)
pfds.sort()

# Basic Labeling

pulsar = args.name
timingfolder = '/opt/pulsar/puma/config/timing/'
timingpar = timingfolder+'{}.par'.format(pulsar)
pulsarpar= parfile.psr_par(timingpar)
scoord = pulsarpar.RAJ+pulsarpar.DECJ


for pfd in pfds:
    subprocess.call(['psredit','-c',
	'coord='+scoord,'-c',
	'name='+pulsar,
	'-m',pfd])
    subprocess.call(['psredit','-c',
	'obs:projid=PuMA','-c',
	'be:name=Ettus-SDR',
	'-m',pfd])

# Choose a given template named 'pulsar.pfd.std'
usingtemplate = timingfolder+'{}.pfd.std'.format(pulsar)

# Define arguments.
def pat_args(nsubint):
    return '-A PGS -f "tempo2" -s {} -jFD -j "T {}" '.format(usingtemplate,nsubint)

subintstoa= './subints.tim'
singletoa= './single.tim'

# Define general output
pat_output_subints= '>> {}'.format(subintstoa)

# Define individual output
pat_output_individual= '>> {}'.format(singletoa)

# Choose a given number of subintegrations to obtain toa and a flag:

nsubints= args.s

# Loop over all the observatins:

# First remove old .tim
subprocess.call(['rm',singletoa,subintstoa])

for pfd in pfds:
    subprocess.call(['pat '+pat_args(nsubints)+pfd+pat_output_subints], shell=True)
    subprocess.call(['pat '+pat_args(1)+pfd+pat_output_individual], shell=True)
