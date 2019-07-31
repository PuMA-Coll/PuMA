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
		self._nu_highest = a_param.get(name,'nu_highest')
		self._gain = a_param.get(name,'gain')
		self._system_temp = a_param.getfloat(name,'t_sys')
		self._npol = a_param.getfloat(name,'n_pol')
		self._beta_g = a_param.getfloat(name,'beta_g')
		self._obs_time = a_param.getfloat(name,'t_obs')*60.0
		self._DECJlimit = a_param.getfloat(name,'maxDECJ')
		self._pointer_file = a_param.get(name,'pointer_file')
		self._tel_id = a_param.get(name,'tel_id')
		self._mach_id = a_param.get(name,'mach_id')
		self._sub_bands = a_param.get(name,'sub_bands')

        
	def can_point(self,psr):
		psr_DECJ = Angle(psr.DECJ,unit=u.deg).to_value()
		return (psr_DECJ < self._DECJlimit)
    
    
	def can_detect(self,psr):
		psr_S1400_Jy = psr.S1400/1000.0
		psr_W50_sec = psr.W50/1000.0
		psr_flux = psr_S1400_Jy * np.sqrt((psr.P0-psr_W50_sec)/psr_W50_sec)
		min_flux = SNR_min * self._system_temp / np.sqrt(self._npol*self._obs_time*self._bandwidth)
		return (psr_flux > min_flux)


	def create_pointer(self,psr):
		pointer = open(psr.name+'_'+self._name+'.sh','w')
		pointer.write('#!/bin/bash'+'\n')
		pointer.write('# ./pulsar_usrp.sh RA_ang DEC_ang time_seconds Name'+'\n')
		pointer.write('./'+self._pointer_file+' '+psr.DECJ+' '+psr.RAJ+' '+psr.name+'\n')
		pointer.close()


	def create_iarfile(self,psr):
		psr_W50_sec = psr.W50/1000.0
		iar = open(psr.name + '_' + self._name + '.iar','w')
		line1='Source Name,' + psr.name + '_' + self._name +'\n'
		line2='Highest Observation Frequency (MHz),'+self._nu_highest +'\n'
		line3='Telescope ID,'+self._tel_id+'\n'
		line4='Machine ID,'+self._mach_id +'\n'
		line5='Data Type,1' +'\n'
		line6='Observing Time (minutes),200' +'\n'
		line7='Gain (dB),'+self._gain +'\n'
		line8='Total Bandwith (MHz),'+str(self._bandwidth/1e6) +'\n'
        #N_ave is a power 2**n
		n_min = int(np.log2(self._bandwidth*psr_W50_sec/2.0))
		line9='Average Data,'+ str(2**min(14,n_min)) +'\n'
		line10='Sub Bands,'+self._sub_bands + '\n'
		iar.writelines([line1, line2, line3, line4, line5, line6, line7, line8, line9, line10])
		iar.close()
        


#####################################################################################################

def IAR_can_point(pulsar):
	return (A1.can_point(pulsar) or A2.can_point(pulsar))


def IAR_can_detect(pulsar):
	return (A1.can_detect(pulsar) or A2.can_detect(pulsar))


def create_parfile(psr):
	par = open(psr.name+'.par','w')
	par.write(query.get_ephemeris(psr.name))
	par.close()

    
def create_inifile(self,psr):
	ini = open(psr.name + '.ini','w')
    
	line1=';' + psr.name + '.ini' + '\n' + '\n'
	line2='[main]' + '\n'
	line3='timing = True' + '\n'
	line4='dmsearch = False' + '\n'
	line5='rfimask = True' + '\n'
	line6='gvoutput = True' + '\n'
	line7='movephase = False' + '\n'
	line8='name = \'' + psr.name + '\'' + '\n' + '\n'
        
	line9='[parameters]' + '\n'
	line10='nbins= 256' + '\n'
	line11='nchan = 32' + '\n'
	line12='phase = 0.0' + '\n'
	line13='npart = 128' + '\n'
	line14='pstep = 1' + '\n' + '\n'
        
	line15='[rfi]' + '\n'
	line16='nint = 0.04' + '\n'
	line17='reuse = True' + '\n'
        
	ini.writelines([line1, line2, line3, line4, line5, line6, line7, line8, line9, line10, line11, line12, line13, line14, line15, line16, line17])
	ini.close()
        
        
#####################################################################################################

antennas_file = './antenna_parameters.dat'
A1 = Antenna(antennas_file,'A1')
A2 = Antenna(antennas_file,'A2')

#####################################################################################################

query = QueryATNF(condition='S1400 > 50 && W50 > 0')
psrs = query.get_pulsars()

#####################################################################################################

for psr in psrs:
	if IAR_can_point(psrs[psr]):
		if IAR_can_detect(psrs[psr]):
			A1.create_iarfile(psrs[psr])
			A2.create_iarfile(psrs[psr])
			create_parfile(psrs[psr])
			A1.create_pointer(psrs[psr])
			A2.create_pointer(psrs[psr])


