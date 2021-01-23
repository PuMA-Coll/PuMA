import numpy as np
import  matplotlib.pyplot as plt
import pandas as pd
from period import findP

def single_pulses(n_files, n_pulses, polycos, bestprof, n_bins=1220):

    ''' This funtion converts the output files from waterfall.py into
    a single csv files with all the single pulses (row = one pulse). 
    Also plots the folded pulse to check.
    
    Args:
    n_files: (int) number of imput files counting from 0
    n_pulses: (int) how many single pulses you want
    period: (float) period of the pulse in seconds obtained from presto
    n_bins: (int) how many points per single pulse. default: 1220
    
    Returns: nothing
    
    '''

    
    # times array
    file_name_1 = 'times_{}.csv'
    df_list_1 = []
    for i in range(0, n_files+1):
        df_list_1.append(pd.read_csv(file_name_1.format(i), header=None))
        times = (pd.concat(df_list_1).to_numpy()).T.flatten()
    
    # intensity array
    file_name_2 = 'original_{}.csv'
    df_list_2 = []
    for i in range(0, n_files+1):
        df_list_2.append(pd.read_csv(file_name_2.format(i), header=None))
        originals = (pd.concat(df_list_2).to_numpy()).T.flatten()
    
    # find the MJD0
    MJD0 = np.genfromtxt ( bestprof, comments="none", dtype=np.float128, skip_header=3, max_rows=1, usecols=(3) )

    # create a new vector of times to match the period:
    new_times=np.zeros(n_bins*n_pulses) # vector with (corrected) time in seconds since the start of the observation
    new_times[0]=times[0]

    MJD_times = np.zeros(n_pulses) # array with the MJD at the beggining of each individual pulse
    
    for n in range(0,n_pulses):
        temp = new_times[n*n_bins]            # time (in seconds since the beggining of the observation) at the beggining of each pulse
        period = findP(polycos, MJD0, temp)   # we find the instantaneous period
        new_dt = period/n_bins                # we divide the pulse into bins

#       print(str(n) + ' ' + str(n*n_bins) + ' ' + str(new_times[n * n_bins]) + ' ' + str(period*1000.))
    
        for i in range(0,n_bins):
                if n*n_bins+i+1 == n_bins*n_pulses: continue
                new_times[n * n_bins + i + 1] = new_times[n * n_bins + i] + new_dt # we save the corrected time

        MJD_times[n] = MJD0 + temp * 1./(24.*60.*60.) 

    # Interpolation
    new_data = (np.interp (new_times, times, originals)).reshape((n_pulses,n_bins))
    
    # Write table
    obs_data = bestprof[bestprof.find('_A')+1:bestprof.find('.pfd')]    # get the antenna and date
    output_csv = "sp_" + obs_data + ".csv"                              # name of the output .csv

    np.savetxt(output_csv,new_data,delimiter=',')                       # save as ascii file
    np.save(output_csv.replace(".csv", ".npy"),new_data)                # save as binary file

    np.savetxt("sp_MJD_" + obs_data + ".csv",MJD_times,delimiter=',')   # save the single pulses MJDs
    
    # Plot
    #folded = np.sum(new_data,axis=0)
    #plt.figure(figsize=(20,10))
    #plt.xlim(0,n_bins)
    #plt.plot(folded)
    #plt.savefig('pulse.png')

