import os, sys, glob, subprocess
import pandas as pd

dbg = True


def CreateThumbnail(file):
    file = file.split('.')[0]
    subprocess.call(['convert', '-thumbnail 500',
                    file+'.png', file+'.thumb.jpg'])

def get_observed_pulsars(path):
    #pulsars = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
    pulsars = [d.strip().split('/')[-2] for d in glob.glob(path+'/J*/')]
    pulsars.sort()
    return pulsars


def get_dates(PSR,path):
    files = os.listdir(path+'/'+PSR+'/')
    dates = []
    for file in files:
        if 'mask_' in file:
            dates.append(file[5:13])
    return dates


def get_bypsr(PSR,DBPATH):
    if dbg: print(PSR)
    lines = "<!-- "+PSR+" --> \n"
    lines += '<article class="box page-content"><header><h2>'+PSR+'</h2></header> \n'
    lines += '<h3>Historical Tempo Plot</h3> \n'
    lines += '<a href="database/'+PSR+'/tempo.png"> \n'
    lines += '<img width="30%" src="database/'+PSR+'/tempo.png" alt=""></a> \n'
    lines += '<p> \n'
    for date in get_dates(PSR,DBPATH):
        if dbg: print(date)
        lines += date[0:4]+'/'+date[4:6]+'/'+date[6:8] +'\n'
        #FUTURE: ADD LINES WITH INFO FROM OBSERVATION FROM DATABASE
        lines += '<a href="database/'+PSR+'/mask_'+date+'.png">Mask</a> \n'
        lines += '<a href="database/'+PSR+'/presto_'+date+'.png">Presto</a> \n'
        lines += '<br> \n'
    lines += '<p> \n'
    lines += '</article> \n'

    if dbg:
        print()

    return lines


def write_bypsr(pulsars, HEADER, FOOTER, WEBPATH, DBPATH):
    header = open(WEBPATH+HEADER).readlines()
    footer = open(WEBPATH+FOOTER).readlines()

    content = ''
    for psr in pulsars:
        content += get_bypsr(psr, DBPATH)

    file = open(WEBPATH+'by_psr.html', 'w')
    file.writelines(header)
    file.writelines(content)
    file.writelines(footer)
    file.close()
    return 0


def write_psr(PSR, HEADER, FOOTER, WEBPATH, DBPATH):
    header = open(WEBPATH+HEADER).readlines()
    footer = open(WEBPATH+FOOTER).readlines()

    try:
        df = pd.read_json('{}/{}/{}.json'.format(DBPATH,PSR,PSR))
    except:
        return -1

    lines = "<!-- "+PSR+" --> \n"
    lines += '<article class="box page-content"><header><h2><a href="'+PSR+'.html">'+PSR+'</a></h2></header> \n'

    for idx in range(len(df)):
        antenna = df.antenna.loc[idx]
        gti = float(df.gti_percentage.loc[idx])
        exp = float(df.obs_duration.loc[idx])/1000.
        date = df.obs_date.loc[idx]
        try:
            snr_par = float(df.snr_par.loc[idx])
        except:
            snr_par = -1
        try:
            snr_timing = float(df.snr_timing.loc[idx])
        except:
            snr_timing = -1

        glitch = df.glitch[idx]

        try:
            pngs = df.pngs[idx]
        except:
            pngs = ''

        lines += '{} {} {} {} {} {} {} <a href="{}">Plots</a><br>\n'.format(antenna, gti, exp, date, snr_par, snr_timing, glitch, pngs)

    file = open(DBPATH+'/'+PSR+'/'+PSR+'.html', 'w')
    file.writelines(header)
    file.writelines(lines)
    file.writelines(footer)
    file.close()
    return 0



def get_lastobs(PSR, DBPATH, antennas=['A1','A2']):
    if dbg:
        print(PSR)

    try:
        df = pd.read_json('{}/{}/{}.json'.format(DBPATH,PSR,PSR))
    except:
        return ''

    lines = "<!-- "+PSR+" --> \n"
    lines += '<article class="box page-content"><header><h2><a href="'+PSR+'.html">'+PSR+'</a></h2></header> \n'

    for antenna in antennas:
        try:
            idx = df[df.antenna == antenna].obs_date.idxmax()
        except:
            continue

        gti = float(df.gti_percentage.loc[idx])
        exp = float(df.obs_duration.loc[idx])/1000.
        date = df.obs_date.loc[idx]
        try:
            snr_par = float(df.snr_par.loc[idx])
        except:
            snr_par = -1
        try:
            snr_timing = float(df.snr_timing.loc[idx])
        except:
            snr_timing = -1

        glitch = df.glitch[idx]

        lines += '<h3>{}: observed on {} for a total of {:.2f} ks with {:.2f} &#37; GTI <br> \n'.format(antenna, date, exp, gti)
        lines += '      SNR_par: {:.2f}  ;  SNR_timing: {:.2f}  ;   Glitch: {} </h3> \n'.format(snr_par, snr_timing, glitch)
        lines += '<div class="row 200%"> <div class="12u"> \n'
        lines += '<section class="box features"><div><div class="row"> \n'
        lines += '<div class="3u 6u(mobile)"><section class="box feature"> \n'
        lines += '<a href="last_obs/'+PSR+'_'+antenna+'_par.png"><img width="100%" src="last_obs/'+PSR+'_'+antenna+'_par.jpg" alt=""></a> \n'
        lines += '</section></div> \n'
        lines += '<div class="3u 6u(mobile)"><section class="box feature"> \n'
        lines += '<a href="last_obs/'+PSR+'_'+antenna+'_timing.png"><img width="100%" src="last_obs/'+PSR+'_'+antenna+'_timing.jpg" alt=""></a> \n'
        lines += '</section></div> \n'
        lines += '<div class="3u 6u(mobile)"><section class="box feature"> \n'
        lines += '<a href="last_obs/'+PSR+'_'+antenna+'_mask.png"><img width="100%" src="last_obs/'+PSR+'_'+antenna+'_mask.jpg" alt=""></a> \n'
        lines += '</section></div> \n'
        lines += '<div class="3u 6u(mobile)"><section class="box feature"> \n'
        lines += '<a href="last_obs/'+PSR+'_'+antenna+'_tempo.png"><img width="100%" src="last_obs/'+PSR+'_'+antenna+'_tempo.jpg" alt=""></a> \n'
        lines += '</section></div> \n'
        lines += '</div></div></section> \n'
        lines += '</div></div> \n'

    lines+= '</article> \n'

    if dbg:
        print()

    return lines


def write_lastobs(pulsars, HEADER, FOOTER, WEBPATH, DBPATH):
    header = open(WEBPATH+HEADER).readlines()
    footer = open(WEBPATH+FOOTER).readlines()

    content = ''
    for psr in pulsars:
        content += get_lastobs(psr,DBPATH)

    file = open(WEBPATH+'last_obs.html', 'w')
    file.writelines(header)
    file.writelines(content)
    file.writelines(footer)
    file.close()
    return 0


# RUN MAIN CODE
if __name__ == "__main__":

    WEBPATH = "/home/observacion/scratchdisk/PuGli-S/puglieseweb/"
    DBPATH = "/home/observacion/scratchdisk/PuGli-S/"

    dbg = False
    print('')
    print('READING PULSARS FROM DB AT '+DBPATH)
    pulsars = get_observed_pulsars(DBPATH)
    print('')
    if dbg: print(pulsars)

    # by_psr.html
    HEADER = 'by_psr_header.txt'
    FOOTER = 'by_psr_footer.txt'
    print('-----------------')
    print('START psr.html')
    for pulsar in pulsars:
         if write_psr(pulsar, HEADER, FOOTER, WEBPATH, DBPATH) ==0:
               print('WRITTEN '+pulsar+'.html')
         else:
               print('ERROR in '+pulsar+'.html')
    print()

#    print('-----------------')
#    print('START by_psr.html')
#    if write_bypsr(pulsars, HEADER, FOOTER, WEBPATH, DBPATH) == 0:
#        print('WRITTEN by_psr.html')
#    else:
#        print('ERROR by_psr.html')
#    print()

    # last_obs.html
    HEADER = 'last_obs_header.txt'
    FOOTER = 'last_obs_footer.txt'
    print('-------------------')
    print('START last_obs.html')
    if write_lastobs(pulsars, HEADER, FOOTER, WEBPATH, DBPATH) == 0:
        print('WRITTEN last_obs.html')
    else:
        print('ERROR last_obs.html')
    print()

    # EXIT PROGRAM
    print()
    print('FINISHED UPDATING WEBPAGE AT '+WEBPATH)
    print()
