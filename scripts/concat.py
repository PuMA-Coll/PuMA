import numpy as np
import  matplotlib.pyplot as plt
import pandas as pd


file_name_1 = 'times_{}.csv'

df_list_1 = []
for i in range(0, 23):
    df_list_1.append(pd.read_csv(file_name_1.format(i), header=None))

times = (pd.concat(df_list_1).to_numpy()).T.flatten()

#times.to_csv('times_all.csv', index=False, header=False)

print(times.shape)


file_name_2 = 'original_{}.csv'

df_list_2 = []
for i in range(0, 23):
    df_list_2.append(pd.read_csv(file_name_2.format(i), header=None))

originals = (pd.concat(df_list_2).to_numpy()).T.flatten()

#times.to_csv('times_all.csv', index=False, header=False)

print(originals.shape)

#number of pulses:
npulses=22900

#Create a new vector of times to match the period:
Period = 0.08940727255212666
new_nbins = 1220
new_dt = Period/new_nbins

new_times=np.zeros(new_nbins*npulses)
new_times[0]=times[0]
for i in range (1,len(new_times)):
    new_times[i] = new_times[i-1] + new_dt

#check
if new_times[-1] > times[-1]:
    print('Too many pulses!')
    exit()

# Interpolation
new_data = (np.interp (new_times, times, originals)).reshape((npulses,new_nbins))

# Write table
print(new_data.shape)
np.savetxt('pulses.csv',new_data,delimiter=',')

