#!/usr/bin/env python2
## pipe_red_trigger

#Author: PuGli-S
#Date: Feb 2020

import os
import sys
sys.path.insert(1,os.path.join(sys.path[0], '/opt/pulsar/puma/scripts/'))
import time
import argparse

from ConfigParser import SafeConfigParser
import glob
import sigproc
import subprocess
import parfile

from puma_reduc import do_reduc


