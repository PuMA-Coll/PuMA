#!/usr/bin/env python

## PuMA all templates
## Python script for multiple template generator using puma_template.py
# Robbing author: SdP

import glob
import subprocess

pulsars = glob.glob('./J*/')
print('There are ' + str(len(pulsars)) + ' pulsars in this directory')

i = 0
for psr in pulsars:
    if 'J0437' not in psr:
        i += 1
        print( 'Creating template for psr ' + psr + '(' + str(i) + '/' + str(len(pulsars)) + ')' )
        subprocess.check_call('puma_template.py', cwd=psr)


