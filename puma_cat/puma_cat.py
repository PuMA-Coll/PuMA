# Must install psrqpy first: https://github.com/mattpitkin/psrqpy
from psrqpy import *
from configparser import ConfigParser
from astropy import units as u
from astropy.coordinates import Angle

SNR_min = 10.0

#########################################################################################################
class Antenna:     
    def __init__(self,a_param_location,name):
        a_param = ConfigParser()
        a_param.read(a_param_location)
        
        self._name = name
        self._bandwidth = a_param.getfloat(name,'bandwidth')
        self._nu_central = a_param.getfloat(name,'nu_central')
        self._gain = a_param.getfloat(name,'gain')
        self._system_temp = a_param.getfloat(name,'t_sys')
        self._npol = a_param.getfloat(name,'n_pol')
        self._beta_g = a_param.getfloat(name,'beta_g')
        self._obs_time = a_param.getfloat(name,'t_obs')*60.0
        self._DECJlimit = a_param.getfloat(name,'maxDECJ')
        self._pointer_file = a_param.get(name,'pointer_file')
        
    def can_detect(self,psr):
        psr_S1400_Jy = psr.S1400/1000.0
        psr_W50_sec = psr.W50/1000.0
        psr_flux = psr_S1400_Jy * np.sqrt((psr.P0-psr_W50_sec)/psr_W50_sec)
        min_flux = SNR_min * self._system_temp / np.sqrt(self._npol*self._obs_time*self._bandwidth)
        cond1 = (psr_flux > min_flux)
        psr_DECJ = Angle(psr.DECJ,unit=u.deg).to_value()
        cond2 = (psr_DECJ < self._DECJlimit)
        return (cond1 and cond2)
    
    def create_parfile(self,psr):
        par = open(psr.name+'.par','w')
        par.write(query.get_ephemeris(psr.name))
        par.close()
    
    def create_pointer(self,psr):
        pointer = open(psr.name+'_'+self._name+'.sh','w')
        pointer.write('#!/bin/bash'+'\n')
        pointer.write('# ./pulsar_usrp.sh RA_ang DEC_ang time_seconds Name'+'\n')
        pointer.write('./'+self._pointer_file+' '+psr.DECJ+' '+psr.RAJ+' '+psr.name+'\n')
        pointer.close()

#####################################################################################################

def IAR_can_detect(pulsar):
    return (A1.can_detect(pulsar) or A2.can_detect(pulsar))

#####################################################################################################

antennas_file = './antenna_parameters.dat'
A1 = Antenna(antennas_file,'A1')
A2 = Antenna(antennas_file,'A2')

#####################################################################################################

query = QueryATNF(condition='S1400 > 0 && W50 > 0')
psrs = query.get_pulsars()

#####################################################################################################

for psr in psrs:
    if(IAR_can_detect(psrs[psr])):
        A1.create_parfile(psrs[psr])
        A1.create_pointer(psrs[psr])
        A2.create_pointer(psrs[psr])