#!/usr/bin/env python

import glob
import argparse
import os
'''
Rename files replacing <old_string> in their names to <new_string>
Run as: rename_files.py <old_string> <new_string>
'''

def set_argparse():
   # add arguments
   parser = argparse.ArgumentParser(prog='rename_files.py',
         formatter_class=argparse.ArgumentDefaultsHelpFormatter,
         description='Rename files replacing <old_string> in their names to <new_string>')
   parser.add_argument('old_string', default='', type=str,
         help='string in the name to be replaced')
   parser.add_argument('new_string', default='', type=str,
         help='string in the name to replace with')
   return parser.parse_args()


# Get strings from command line arguments
args = set_argparse()
old_string, new_string = args.old_string, args.new_string

# Search for all files containing <old_string> in their name
old_files = glob.glob('*' + old_string + '*')

# Rename the files replacing the <old_string> for <new_string>
for old_file in old_files:
   os.rename(old_file, old_file.replace(old_string, new_string))


