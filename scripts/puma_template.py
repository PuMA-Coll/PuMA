#!/usr/bin/env python

## PuMA template
## Python script for template generator
# This script generates new templates from existing observation.
# Version: 0.1
# Date: 11/3/19
# author: Luciano Combi

# We will need to execute shell scripts

import subprocess
import sys
import glob
import os
import psrchive

# Open pfds.

pfdtype = '*tim*.pfd'
pfds = glob.glob(pfdtype)

# Basic Labeling

pulsar= 'B0833-45'
telescope = 'IAR2'

for pfd in pfds:
    arch = psrchive.Archive_load(pfd)
    arch.set_telescope(telescope)
    arch.set_source(pulsar)
    arch.unload()

# Add pfds and form a super pfd:

sumpfds = './timing/'+pulsar+'.pfd'
shutil.copy(pfds[0],sumpfds)

for pfd in pfds:
    arch= psrchive.Archive_load(pfd)
    if arch.get_nchan() == 64:
        subprocess.check_output(['psradd', '-F','-P',pfd,sumpfds,'-o',sumpfds])

# Make a smooth profile

subprocess.check_output(['psrsmooth', '-n','-e','std',sumpfds])
