#!/usr/bin/env python2
## puma_reduc

#'El hermano lindo de pulsar_reduc'
#Author: Luciano Combi for PuMA
#Date: April 2019

import os
import sys
import time
import argparse

from ConfigParser import SafeConfigParser
import glob
import sigproc
import subprocess
import parfile

global dbg
dbg = True


# --------------------------------------------------------
#                        IDEAS
# --------------------------------------------------------
# 07/02/2020
# Treat each observation data as a python class such as:
# raw-data, mask, pfd, observation-data for glitches and
# more.
# Advantages: easy to access once its created and store in
# different formats (hdf5)
# --------------------------------------------------------


def set_argparse():
    # add arguments
    parser = argparse.ArgumentParser(prog='puma_reduc.py',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description='raw data folding with PRESTO')
    parser.add_argument('--ftype', default='timing', type=str,
            help='folding tag option')
    parser.add_argument('--folder', default=os.environ['PWD'], type=str,
            help='ABSOLUTE PATH where observations are stored and where output will be created')
    parser.add_argument('--ptopo', default=None, type=str,
            help='seed for the topocentric folding period in sec')
    parser.add_argument('--par_dirname', default='/opt/pulsar/tempo/tzpar/', type=str,
            help='path to directory containing .par file')

    return parser.parse_args()


def check_cli_arguments(args):

    ierr = 0

    if os.path.isabs(args.folder) is False:
        print('\n FATAL ERROR: folder path is not absolute\n')
        ierr = -1
        return ierr

    if args.ftype != 'timing' and args.ftype != 'par' and args.ftype != 'search':
        print('\n FATAL ERROR: unknown option for ftype\n')
        ierr = -1
        return ierr

    if args.ftype == 'search' and args.ptopo is None:
        print('\n FATAL ERROR: you must specify --ptopo for the search mode\n')
        ierr = -1
        return ierr

    return ierr


def get_pulsar_info(path, dotpar_path):

    # stuff to return
    ierr = 0
    Main, Parameters, Rfi = {}, {}, {}

    # check the name of the pulsar and fils
    # - grab name of .fils
    fils = glob.glob(path + '/*.fil')
    fils.sort()
    # - count how many fils are in the folder
    nfils = len(fils)

    # warning if there are more than one fil
    if nfils <= 0: 
        print('\n ERROR: no *.fil(s) found in ' + args.folder + '\n')
        ierr = -1
        return Main, Parameters, Rfi, ierr
    elif nfils > 1:
        print('\n WARNING: more than one fil in this folder. I will fold them all.\n')

    # grab name of pulsar from the .fil with sigproc function read_header (dictionary)
    fil_dic = sigproc.read_header(fils[0])[0]
    pulsarname = fil_dic['source_name'][:-3]
        
    # grab configuration file with same name than the pulsar
    configdest = '/opt/pulsar/puma/config/'
    configfile = SafeConfigParser()
    configfile.read(configdest + pulsarname + '.ini')

    # if we are not using manual mode, take all parameters in the config file,
    # this file contains 3 sections: main, parameters and rfi. Each of them will
    # be stored in different dictionaries, Main, Parameters and Rfi such that
    # this will be returned by get_pulsar_info function

    # Main information
    Main['timing'] = configfile.getboolean('main', 'timing')
    Main['dmsearch'] = configfile.getboolean('main', 'dmsearch')
    Main['rfimask'] = configfile.getboolean('main', 'rfimask')
    Main['gvoutput'] = configfile.getboolean('main', 'gvoutput')
    Main['movephase'] = configfile.getboolean('main', 'movephase')
    Main['name'] = pulsarname
    Main['date'] = fil_dic['rawdatafile'][-19:-4]
    Main['fils'] = fils

    # Parameters information
    Parameters['nbins'] = configfile.get('parameters', 'nbins')
    Parameters['nchan'] = fil_dic['nchans']
    Parameters['phase'] = configfile.get('parameters', 'phase')
    Parameters['npart'] = configfile.get('parameters', 'npart')
    Parameters['pstep'] = configfile.get('parameters', 'pstep')

    # Rfi information
    Rfi['nint'] = configfile.get('rfi', 'nint')
    Rfi['reuse'] = configfile.getboolean('rfi', 'reuse')

    # path to .par file
    dotpar = dotpar_path + '/' + pulsarname + '.par'
    if os.path.isfile(dotpar) is False:
        print('\n ERROR: no .par file found in ' + pardest + '\n')
        ierr = -1
        return Main, Parameters, Rfi, ierr
    else:
        Main['dotpar'] = dotpar

    return Main, Parameters, Rfi, ierr


def do_rfi_search(Main, Rfi, args):

    ierr = 0
    maskname = ''

    # RFIfind process
    # - check if we would re-use an existing mask. If not, start rfifind process
    output = 'mask_' + Main['name'] + '_' + Rfi['nint'] + '_' + Main['date']
    rfifind = ['rfifind', '-time', Rfi['nint'], '-zerodm', '-o', output]
    rfifind.extend(Main['fils'])

    if Rfi['reuse']:
        masks = glob.glob(args.folder + '/*.mask')
        if len(masks) > 1:
            print('WARNING: More than one mask in the folder! I will use the first one.')
            usingmask = masks[0]
        elif len(masks) == 0:
            print('WARNING: No mask in the folder. I will make one for you')
            subprocess.check_call(rfifind, cwd=args.folder)
            maskname = output+'_rfifind.mask'
        else:
            maskname = masks[0]
    else:
        subprocess.check_call(rfifind, cwd=args.folder)
        maskname = output + '_rfifind.mask'

    return maskname, ierr


def prepare_prepfold_cmd(Main, Parameters, Rfi, args):

    ierr = 0

    # command to run prepfold
    prepfold_args = ['prepfold',
            '-nsub', Parameters['nchan'],
            '-n', Parameters['nbins'],
            '-mask', Rfi['maskname'],
            '-noxwin']

    # do_dm_search
    if not Main['dmsearch']:
        prepfold_args.append('-nodmsearch')

    # move_phase
    if Main['movephase']:
        prepfold_args.extend(('-phs', Parameters['phase']))

    if args.ftype == 'timing':
        prepfold_args.extend(('-timing', Main['dotpar']))
    elif args.ftype == 'par':
        prepfold_args.extend(('-par', Main['dotpar'],
            '-pstep', Parameters['pstep'],
            '-npart', Parameters['npart']))
    elif args.ftype == 'search':
        prepfold_args.extend(('-topo', '-p', args.ptopo,
            '-pstep', Parameters['pstep'],
            '-npart', Parameters['npart']))

    # add output filename
    output = 'prepfold_' + args.ftype + '_' + Main['date']
    prepfold_args.extend(('-o', output, '-filterbank'))
    prepfold_args.extend(Main['fils'])

    return prepfold_args, ierr


def do_reduc(args):

    ierr = 0

    # get pulsar information
    Main, Parameters, Rfi, ierr = get_pulsar_info(path=args.folder, dotpar_path=args.par_dirname)

    # apply mask on observation(s)
    maskname, ierr = do_rfi_search(Main, Rfi, args)
    Rfi['maskname'] = maskname
    if ierr != 0: sys.exit(1)

    # prepare to call prepfold for observation reduction process
    prepfold_args, ierr = prepare_prepfold_cmd(Main, Parameters, Rfi, args)
    if ierr != 0: sys.exit(1)

    # do actual reduction
    subprocess.check_call(prepfold_args, cwd=args.folder)

    return ierr


if __name__ == 'main':

    # get cli-arguments
    args = set_argparse()

    # check arguments
    ierr = check_cli_arguments(args)
    if ierr != 0:
        sys.exit(1)
    else:
        start = time.time()

    ierr = do_reduc(args)
    if ierr != 0:
        sys.exit(1)

    # exit with success printing duration
    end = time.time()
    hours, rem = divmod(end-start, 3600)
    minutes, seconds = divmod(rem, 60)
    print('\n Reduction process completed in', end=' ')
    print('{:0>2}:{:0>2}:{:05.2f}\n'.format(int(hours), int(minutes), seconds))
