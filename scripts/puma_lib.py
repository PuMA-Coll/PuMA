import os
import sys
sys.path.insert(1,os.path.join(sys.path[0], '/opt/pulsar/puma/scripts/'))
import shutil

from ConfigParser import SafeConfigParser
import sigproc
import glob
import subprocess
import numpy as np

import rfifind

class Observation(object):
    """ This is the main class that represents an observation from a single antenna."""

    DEFAULT_PAR_DIRNAME = '/opt/pulsar/puma/pardir/'
    DEFAULT_CONFIG_DIRNAME = '/opt/pulsar/puma/config/'
    DEFAULT_TIMING_DIRNAME = DEFAULT_CONFIG_DIRNAME + 'timing/'

    DEFAULT_THRESHOLD_FOR_REDUC = 1000000  # 1 Mb in bytes

    def __init__(self, path2dir=os.environ['PWD'], pname=''):
        self.path_to_dir = path2dir
        if pname != '': 
            self.pname = pname
        else:
            self.pname, self.antenna, self.mjd, self.nchans = self.get_pulsar_parameters()
        self.glitch = False
        self.red_alert = False
        self.blue_alert = False
        self.par_dirname = self.DEFAULT_PAR_DIRNAME
        self.config_dirname = self.DEFAULT_CONFIG_DIRNAME
        self.dotpar_filename = self.par_dirname + self.pname + '.par'
        self.was_reduced = False
        self.params2reduc = {}
        self.nfils = 1
        self.nempty = 0


    def get_pulsar_parameters(self):
        # select .fil file
        fils = glob.glob(self.path_to_dir + '/*.fil')
        fil = fils[0]

        # grab name of pulsar from the .fil with sigproc function read_header (dictionary)
        fil_dic = sigproc.read_header(fil)[0]
        pname = fil_dic['source_name'][:-3]
        antenna = fil_dic['source_name'][-2:]
        mjd = fil_dic['tstart']
        nchans = fil_dic['nchans']

        return pname, antenna, mjd, nchans

    def do_rfi_search(self):

        ierr = 0
        self.maskname = ''

        # search for antenna in one of the .fil(s)
        if 'A1' in self.params2reduc['fils'][0]:
            sigmas = '35'
        elif 'A2' in self.params2reduc['fils'][0]:
            sigmas = '4'
        else:
            print('\n ERROR: no antenna A1 or A2 found in .fil name \n')
            sys.exit(1)

        # RFIfind process
        # - check if we would re-use an existing mask. If not, start rfifind process
        output = 'mask_' + self.pname + '_' + self.params2reduc['nint'] + '_' + self.params2reduc['date']
        rfifind = ['rfifind', '-ncpus', self.params2reduc['ncores'], '-time', self.params2reduc['nint'], '-freqsig', sigmas, '-zerodm', '-o', output]
        rfifind.extend(self.params2reduc['fils'])

        if self.params2reduc['reuse']:
            masks = glob.glob(self.path_to_dir + '/*.mask')
            if len(masks) > 1:
                print('WARNING: More than one mask in the folder! I will use the first one.')
                usingmask = masks[0]
            elif len(masks) == 0:
                print('WARNING: No mask in the folder. I will make one for you')
                subprocess.check_call(rfifind, cwd=self.path_to_dir)
                self.maskname = self.path_to_dir + '/' + output+'_rfifind.mask'
            else:
                self.maskname = masks[0]
        else:
            subprocess.check_call(rfifind, cwd=self.path_to_dir)
            self.maskname = self.path_to_dir + '/' + output + '_rfifind.mask'

        return ierr


    def prepare_prepfold_cmd(self):

        ierr = 0

        # command to run prepfold
        prepfold_args = ['prepfold',
                '-nsub', self.params2reduc['nchan'],
                '-n', self.params2reduc['nbins'],
                '-mask', self.maskname,
                '-ncpus', self.params2reduc['ncores'],
                '-start', self.start,
                '-end', self.end,
                '-noxwin']

        # do_dm_search
        if not self.params2reduc['dmsearch']:
            prepfold_args.append('-nodmsearch')

        # move_phase
        if self.params2reduc['movephase']:
            prepfold_args.extend(('-phs', self.params2reduc['phase']))

        if self.params2reduc['ftype'] == 'timing':
            prepfold_args.extend(('-timing', self.dotpar_filename))
        elif self.params2reduc['ftype'] == 'par':
            prepfold_args.extend(('-par', self.dotpar_filename,
                '-pstep', self.params2reduc['pstep'],
                '-npart', self.params2reduc['npart'],
                '-nopdsearch'))
        elif self.params2reduc['ftype'] == 'search':
            # search dm
            f = open(self.params2reduc['dotpar'], 'r')
            lines = f.readlines()
            for line in lines:
                if 'DM ' in line:
                    str_arr = line.strip().split(' ')
                    dm = filter(None, str_arr)[1]
                    break
            f.close()
            prepfold_args.extend(('-topo', '-p', self.params2reduc['ptopo'],
                '-pstep', self.params2reduc['pstep'],
                '-npart', self.params2reduc['npart'],
                '-dm', dm,
                '-nopdsearch'))

        # add output filename
        output = 'prepfold_' + self.params2reduc['ftype'] + '_' + self.antenna + '_' + self.params2reduc['date']
        prepfold_args.extend(('-o', output, '-filterbank'))
        prepfold_args.extend(self.params2reduc['fils'])

        return prepfold_args, ierr


    def set_params2reduc(self, ftype='timing', path_to_dir=os.environ['PWD'], par_dirname=DEFAULT_PAR_DIRNAME, ptopo=1.0, ncores=2, start=0.0, end=1.0):
    
        self.params2reduc['ftype'] = ftype
        self.path_to_dir = path_to_dir
        self.par_dirname = par_dirname
        self.start = str(start)
        self.end = str(end)
        if self.params2reduc['ftype'] == 'search': self.params2reduc['ptopo'] = str(ptopo)
        
        ierr = 0

        # check the name of the pulsar and fils
        # - grab name of .fils
        fils = glob.glob(self.path_to_dir + '/*.fil')
        fils.sort()
        # just use the ones that have a size above the threshold
        fils2reduc = [fil for fil in fils if os.stat(fil).st_size > self.DEFAULT_THRESHOLD_FOR_REDUC]

        # - count how many fils are in the dir
        self.nfils = len(fils2reduc)
        self.nempty = len(fils) - self.nfils
        
        # warning if there are more than one fil
        if self.nfils <= 0:
            print('\n ERROR: no *.fil(s) found in ' + self.path_to_dir + '\n')
            ierr = -1
            return ierr
        elif self.nfils > 1:
            print('\n WARNING: more than one fil found in the folder. I will fold them all. \n')

        # grab name of pulsar from the .fil with sigproc function read_header (dictionary)
        fil_dic = sigproc.read_header(fils[0])[0]
        pulsarname = fil_dic['source_name'][:-3]
        
        if (self.pname == ''): self.pname = pulsarname
        elif (self.pname != pulsarname):
            print('\n WARNING: Pulsar name in the header .fil different from the name of the pulsar you intend to reduce. You might be in a wrong folder. \n')

        # grab configuration file with same name than the pulsar
        configfile = SafeConfigParser()
        configfile.read(self.config_dirname + self.pname + '.ini')

        # if we are not using manual mode, take all parameters in the config file,
        # this file contains 3 sections: main, parameters and rfi. Each of them will
        # be stored in different dictionaries, Main, Parameters and Rfi such that
        # this will be returned by get_pulsar_info function

        self.params2reduc['timing'] = configfile.getboolean('main', 'timing')
        self.params2reduc['dmsearch'] = configfile.getboolean('main', 'dmsearch')
        self.params2reduc['rfimask'] = configfile.getboolean('main', 'rfimask')
        self.params2reduc['gvoutput'] = configfile.getboolean('main', 'gvoutput')
        self.params2reduc['movephase'] = configfile.getboolean('main', 'movephase')
        self.params2reduc['date'] = fil_dic['rawdatafile'][-19:-4]
        self.params2reduc['fils'] = fils2reduc
        self.params2reduc['ncores'] = str(ncores)

        self.params2reduc['nbins'] = configfile.get('parameters', 'nbins')
        self.params2reduc['nchan'] = str(fil_dic['nchans'])
        self.params2reduc['phase'] = configfile.get('parameters', 'phase')
        self.params2reduc['npart'] = configfile.get('parameters', 'npart')
        self.params2reduc['pstep'] = configfile.get('parameters', 'pstep')

        # Rfi information
        self.params2reduc['nint'] = configfile.get('rfi', 'nint')
        self.params2reduc['reuse'] = configfile.getboolean('rfi', 'reuse')

        self.dotpar_filename = self.par_dirname + '/' + self.pname + '.par'
        if os.path.isfile(self.dotpar_filename) is False:
            print ('\n ERROR: no .par file found in ' + self.par_dirname + '\n')
            ierr = -1
            return ierr
        return ierr


    def do_reduc(self):

        ierr = 0

        # apply mask on observation(s)
        ierr = self.do_rfi_search()
        if ierr != 0: sys.exit(1)

        # prepare to call prepfold for observation reduction process
        prepfold_args, ierr = self.prepare_prepfold_cmd()
        if ierr != 0: sys.exit(1)

        # do actual reduction
        subprocess.check_call(prepfold_args, cwd=self.path_to_dir)
        self.was_reduced = True

        return ierr


    def read_bestprof(self,ftype=''):

        ierr = 0
        try:
            filename = glob.glob(self.path_to_dir + '/*'+ftype+'*.bestprof')[0]
        except Exception:
            print('\n FATAL ERROR: could not find bestprofile for ',ftype,'\n')
            ierr = -1
            return 1000,10,ierr

        f = open(filename, 'r')
        lines = f.readlines()
        for line in lines:
            if 'P_topo ' in line:
                str_arr = line.strip().split(' ')
                P_topo = filter(None, str_arr)[4]
                err_P_topo = filter(None, str_arr)[6]
                break

        f.close()
        return float(P_topo), float(err_P_topo), ierr


    def do_glitch_search(self, path_to_dir=os.environ['PWD'], par_dirname=DEFAULT_PAR_DIRNAME, thresh=1.0e-8, ncores=2):
        
        ierr = 0

        # Check if the reduction has already been made
        if len(glob.glob('*timing*.pfd')) + len(glob.glob('*par*.pfd')) >= 2: self.was_reduced = True

        if self.was_reduced is False:
            
            self.set_params2reduc(ftype='timing', path_to_dir=path_to_dir, par_dirname=par_dirname, ncores=ncores)
            ierr = self.do_reduc()
            if ierr != 0: sys.exit(1)

            self.set_params2reduc(ftype='par', path_to_dir=path_to_dir, par_dirname=par_dirname, ncores=ncores)
            ierr = self.do_reduc()
            if ierr != 0: sys.exit(1)
        else:
            self.maskname = glob.glob('*.mask')[0]

        # Check for glitch
        P_eph, err_P, ierr = self.read_bestprof('timing')
        if ierr != 0: sys.exit(1)
        
        P_obs, err_P, ierr = self.read_bestprof('par')
        if ierr != 0: sys.exit(1)

        DP = P_eph - P_obs  # if >0 glithc, <0 anti_glitch
        self.jump = DP/P_eph

        self.red_alert = False
        if abs(self.jump) > thresh and err_P/P_eph < thresh:
            self.red_alert = True

        return ierr


    def do_toas(self, mode='add', pfd_dirname=os.environ['PWD'], par_dirname=DEFAULT_PAR_DIRNAME,
                std_dirname=DEFAULT_TIMING_DIRNAME, tim_dirname='', n_subints=1):

        def do_single_toa(pfd, pfd_dirname, par_fname, std_fname, n_subints, tim_fname):
            ierr = 0
            try:
                # get RAJ DECJ from .par
                f = open(par_fname)
                lines = f.readlines()
                f.close()
                for line in lines:
                    if 'RAJ' in line: RAJ = line.strip().split()[1]
                    if 'DECJ' in line: DECJ = line.strip().split()[1]
                # change pfd header
                coord = RAJ + DECJ
                subprocess.call(['psredit',
                    '-c', 'coord=' + coord, '-c', 'name=' + self.pname, '-m', pfd])
                subprocess.call(['psredit',
                    '-c', 'obs:projid=PuMA', '-c', 'be:name=Ettus-SDR', '-m', pfd])

                # before calling pat to get TOAs, move *_par* files to a temporary
                # folder, then run the pat line, bring back *_par* files and remove
                # tmp folder
                path_to_tmp_folder = pfd_dirname + '/tmp/'
                try:
                    os.mkdir(path_to_tmp_folder) 
                except:
                    pass
                # move *_par* files to tmp folder
		try:
                    files = glob.glob(pfd_dirname + '/*_par*')
                    for file in files:
                        shutil.move(file, path_to_tmp_folder)
		except:
		    pass


                # define arguments for call to pat
                line = '-A PGS -f \"tempo2\" -s ' + std_fname + ' -jFD -j \"T ' + str(n_subints) + '\" '
                # call to pat to get toa
                subprocess.call(['pat ' + line + pfd + ' >> ' + tim_fname], shell=True)

                # move back files in the tmp folder
		try:
                    files = glob.glob(path_to_tmp_folder + '/*')
                    for file in files:
                        shutil.move(file, pfd_dirname)
                    os.rmdir(path_to_tmp_folder)
		except:
		    pass

                # if everything went well, just remove tmp folder
                # os.rmdir(path_to_tmp_folder)

            except Exception:
                ierr = -1
            return ierr
            

        ierr = 0
        
        pfds = glob.glob(pfd_dirname + '/*timing*.pfd')

        # filenames
        tim_fname = tim_dirname + '/' + self.pname + '_' +  self.antenna + '.tim'
        par_fname = par_dirname + self.pname + '.par'
        std_fname = std_dirname + '/' + self.pname + '.pfd.std'

        # computing toa for observations(s)
        if mode == 'all':
            # first remove old .tim
            subprocess.call(['rm', '-f', tim_fname])
            print('Creating tim file ' + tim_fname)
            for pfd in pfds:
                do_single_toa(pfd, pfd_dirname, par_fname, std_fname, n_subints, tim_fname)
        elif mode == 'add':
            print('Adding TOA to ' + tim_fname)
            do_single_toa(pfds[0], pfd_dirname, par_fname, std_fname, n_subints, tim_fname)
        else:
            print('\n ERROR: unknown mode for computing toa(s) \n')
            ierr = -1

        return ierr


    def get_mask_percentage(self, maskname=''):
        
        ierr = 0
 
        print('\n Getting GTI from mask: {}\n'.format(maskname))

        if os.path.isfile(maskname) is False:
            ierr = -1
            print('\nMask {} not found, cannot get_mask_percentage\n\n'.format(maskname))
            return ierr

        maskrfi = rfifind.rfifind(maskname)
        maskrfi.read_bytemask()
        maskarr = maskrfi.bytemask
        nbad = float(np.count_nonzero(maskarr))
        ntot = float(len(maskrfi.goodints)) * float(len(maskrfi.freqs))
        self.gti_percentage = (1.0 - nbad/ntot) * 100
        return ierr
