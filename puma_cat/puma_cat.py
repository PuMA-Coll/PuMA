# Must install psrqpy first: https://github.com/mattpitkin/psrqpy
from psrqpy import *
from configparser import ConfigParser
from astropy import units as u
from astropy.coordinates import Angle

SNR_min = 8.0

#########################################################################################################

class Antenna:     
	def __init__(self,a_param_location,name):
		a_param = ConfigParser()
		a_param.read(a_param_location)
		
		self._name = name
		self._bandwidth = a_param.getfloat(name,'bandwidth')
		self._nu_highest = a_param.get(name,'nu_highest')
		self._gain = a_param.getfloat(name,'gain')
		self._t_sys = a_param.getfloat(name,'t_sys')
		self._npol = a_param.getfloat(name,'n_pol')
		self._beta = a_param.getfloat(name,'beta') 
		self._obs_time = a_param.getfloat(name,'t_obs')*60.0
		self._DECJlimit = a_param.getfloat(name,'maxDECJ')
		self._pointer_file = a_param.get(name,'pointer_file')
		self._tel_id = a_param.get(name,'tel_id')
		self._mach_id = a_param.get(name,'mach_id')
		self._sub_bands = a_param.get(name,'sub_bands')
		self._beta_g = self._beta*self._gain
		self._LO = a_param.getfloat(name,'local_oscillator')

		
		SNR_min = 8.0
		self._min_flux = SNR_min * self._t_sys * self._beta_g / np.sqrt(self._npol*self._obs_time*self._bandwidth)


	def can_point(self,psr):
		psr_DECJ = Angle(psr.DECJ,unit=u.deg).to_value()
		return (psr_DECJ < self._DECJlimit)
    
    
	def can_detect(self,psr):
		psr_S1400_Jy = psr.S1400/1000.0
		psr_W50_sec = psr.W50/1000.0
		psr_flux = psr_S1400_Jy * np.sqrt((psr.P0-psr_W50_sec)/psr_W50_sec)
#		print(psr_flux,self._min_flux)
		return (psr_flux > self._min_flux)


	def create_pointer(self,psr):
		pointer = open(psr.name+'_'+self._name+'.sh','w')
		pointer.write('#!/bin/bash'+'\n')
		pointer.write('# ./pulsar_usrp.sh RA_ang DEC_ang time_seconds Name'+'\n')
		pointer.write('./'+self._pointer_file+' '+psr.RAJ+' '+psr.DECJ+' '+psr.name+'\n')
		pointer.close()


	def create_iarfile(self,psr):
		psr_W50_sec = psr.W50/1000.0
		iar = open(psr.name + '_' + self._name + '.iar','w')
		lines = []
		lines.append('Source Name,' + psr.name + '_' + self._name +'\n')
		lines.append('Source RA (hhmmss.s),' + str(psr.raj).replace(':', '') +'\n')
		lines.append('Source DEC (ddmmss.s),' + str(psr.decj).replace(':', '') +'\n')
		lines.append('Reference DM,' + str(psr.dm) +'\n')
		lines.append('Pulsar Period,'+ str(psr.p0) +'\n')
		lines.append('Highest Observation Frequency (MHz),' + self._nu_highest +'\n')
		lines.append('Telescope ID,' + self._tel_id+'\n')
		lines.append('Machine ID,' + self._mach_id +'\n')
		lines.append('Data Type,1' +'\n')
		lines.append('Observing Time (minutes),200'+'\n')
		lines.append('Local Oscillator (MHz),' + str(self._LO) +'\n')
		lines.append('Gain (dB),' + str(20) +'\n')
#		lines.append('Gain (dB),'+str(self._gain) +'\n')
		lines.append('Total Bandwith (MHz),' + str(self._bandwidth/1e6) +'\n')
        #N_ave is a power 2**n
		n_min = int(np.log2(self._bandwidth*psr_W50_sec/2.0))
		lines.append('Average Data,' + str(2**min(14,n_min)) +'\n')
		lines.append('Sub Bands,' + self._sub_bands + '\n')
		iar.writelines(line for line in lines)
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
    
    
def create_inifile(psr):
	ini = open(psr.name + '.ini','w')
	
	lines = []
	lines.append(';' + psr.name + '.ini' + '\n' + '\n')
	lines.append('[main]' + '\n')
	lines.append('timing = True' + '\n')
	lines.append('dmsearch = False' + '\n')
	lines.append('rfimask = True' + '\n')
	lines.append('gvoutput = True' + '\n')
	lines.append('movephase = False' + '\n')
	lines.append('name = \'' + psr.name + '\'' + '\n' + '\n')
	lines.append('[parameters]' + '\n')
	lines.append('nbins= 256' + '\n')
	lines.append('nchan = 32' + '\n')
	lines.append('phase = 0.0' + '\n')
	lines.append('npart = 128' + '\n')
	lines.append('pstep = 1' + '\n' + '\n')
	lines.append('[rfi]' + '\n')
	lines.append('nint = 1.0' + '\n')
	lines.append('reuse = True' + '\n')
	
	ini.writelines(line for line in lines)
	ini.close()
        
#####################################################################################################

antennas_file = './antenna_parameters.dat'
A1 = Antenna(antennas_file,'A1')
A2 = Antenna(antennas_file,'A2')

#####################################################################################################

#Just the bright pulsars to test with a smaller sample
query = QueryATNF(condition='S1400 > 1.9 && W50 > 0 && decjd < -9',checkupdate=True)
psrs = query.get_pulsars()

psrs_iar = pulsar.Pulsars()
for psr in psrs:
	if IAR_can_point(psrs[psr]):
		if IAR_can_detect(psrs[psr]):
			psrs_iar.add_pulsar(psrs[psr])
            
#####################################################################################################

for psr in psrs_iar:
	create_parfile(psrs_iar[psr])
		create_inifile(psrs_iar[psr])
		A1.create_iarfile(psrs_iar[psr])
		A2.create_iarfile(psrs_iar[psr])
		A1.create_pointer(psrs_iar[psr])
		A2.create_pointer(psrs_iar[psr])
            
#####################################################################################################
            
arr = np.zeros((len(psrs_iar),8), dtype=object)
for i,psr in enumerate(psrs_iar):
	arr[i,0], arr[i,1] = psrs_iar[psr].name, psrs_iar[psr].raj
	arr[i,2], arr[i,3] = psrs_iar[psr].decj, psrs_iar[psr].p0
	arr[i,4], arr[i,5] = psrs_iar[psr].w50, psrs_iar[psr].S1400
	arr[i,6], arr[i,7] = psrs_iar[psr].dm, psrs_iar[psr].NGlt
    
# Create output Data Frame object
import pandas as pd
OutputObj = pd.DataFrame(arr)
WriterObj = pd.ExcelWriter('psr_iar.xlsx')
OutputObj.to_excel(WriterObj, sheet_name = 'Sheet1' ,na_rep = ' ', index = False, header = False)
WriterObj.save()

