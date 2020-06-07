#!/usr/bin/env python

#######             #######
# Pulsar reduction looper #
#######             #######

# import system modules
import sys, glob, os, re
import subprocess

# choose a process to loop
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("script", action='store', type=str, help="choose the process and this will loop it")
parser.add_argument("--p", action='store', type=str, help="additional", required=False)
args = parser.parse_args()

# Check where you are
directory = os.getcwd()

# Make a list of all subdirectories
rootlist=[]

for root, dirs, files in os.walk(directory):
    rootlist.append(root)

# Find those directories suitable for pulsar_reduction treatment

# We create a list of folders 
looplist=[]

# We just take the folders of the type: /obs#
files = re.compile(r'obs[0-9]+')

for x in rootlist:
	if files.findall(x):
	        looplist.append(x)

#We arrange the list
looplist.sort()

#Now DO IT

print ('Looping in the following folders')
for x in looplist:
        print(x)

if args.p:
       for x in looplist:
               subprocess.call([args.script,args.p], cwd=x, shell=True)
else :
       for x in looplist:
              subprocess.call([args.script], cwd=x, shell=True)
