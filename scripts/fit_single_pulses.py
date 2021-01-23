"""

Input files:

 - sp_MJD_A*.csv : MJD times at the beginning of each single pulse with each antenna
 - sp_A*.npy : single pulses with each atenna

Output files_

 - new_pulses_A1.npy
 - new_pulses_A2.npy

"""

import numpy as np
import csv
import glob

pulses_A1 = np.load(glob.glob('sp_A1*.npy')[0])
pulses_A2 = np.load(glob.glob('sp_A2*.npy')[0])

MJD_A1 = np.loadtxt(glob.glob('sp_MJD_A1*.csv')[0], usecols=0)
MJD_A2 = np.loadtxt(glob.glob('sp_MJD_A2*.csv')[0], usecols=0)

n = 0
m = 0

if MJD_A1[0] < MJD_A2[0]:

        while int(MJD_A1[n]*1e6) != int(MJD_A2[0]*1e6):

                n += 1

        start_A1 = n
        start_A2 = 0

        while n < len(MJD_A1)-1 and m < len(MJD_A2)-1:

                n += 1
                m += 1

        finish_A1 = n
        finish_A2 = m

elif MJD_A1[0] > MJD_A2[0]:

        while int(MJD_A1[0]*1e6) != int(MJD_A2[m]*1e6):

                m += 1

        start_A1 = 0
        start_A2 = m

        while n < len(MJD_A1)-1 and m < len(MJD_A2)-1:

                n += 1
                m += 1

        finish_A1 = n
        finish_A2 = m

print("Length A1 observation = " + str(len(MJD_A1[start_A1:finish_A1])) + " pulses")
print("Length A2 observation = " + str(len(MJD_A2[start_A2:finish_A2])) + " pulses")

if(len(MJD_A1[start_A1:finish_A1]) == len(MJD_A2[start_A2:finish_A2])):

        print("Funciona")

        np.savetxt("new_pulses_A1.csv", pulses_A1[start_A1:finish_A1,:], delimiter=',')
        np.savetxt("new_pulses_A2.csv", pulses_A2[start_A2:finish_A2,:], delimiter=',')

        np.save("new_pulses_A1.npy", pulses_A1[start_A1:finish_A1,:])
        np.save("new_pulses_A2.npy", pulses_A2[start_A2:finish_A2,:])

