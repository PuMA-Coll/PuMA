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


def write_bypsr(pulsars, HEADER, FOOTER, WEBPATH, DBPATH):
    header = open(WEBPATH+HEADER).readlines()
    footer = open(WEBPATH+FOOTER).readlines()

    lines = ''
    for PSR in pulsars:
        lines += "<!-- "+PSR+" --> \n"
        lines += '<article class="box page-content"><header><h2><a href="'+PSR+'/'+PSR+'.html">'+PSR+'</a></h2></header> \n'
        lines += '<h3>Historical Tempo Plots</h3> \n'
        lines += '<h4>A1</h4><a href="'+PSR+'/'+PSR+'_A1_tempo.png"> \n'
        lines += '<img width="30%" src="'+PSR+'/'+PSR+'_A1_tempo.png" alt="A1"></a> \n'
        lines += '<h4>A2</h4><a href="'+PSR+'/'+PSR+'_A2_tempo.png"> \n'
        lines += '<img width="30%" src="'+PSR+'/'+PSR+'_A2_tempo.png" alt="A2"></a> \n'
        lines += '</article>\n\n'

    file = open(DBPATH+'by_psr.html', 'w')
    file.writelines(header)
    file.writelines(lines)
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
    lines += '<h3>Historical Tempo Plots</h3> \n'
    lines += '<h4>A1</h4><a href="'+PSR+'_A1_tempo.png"> \n'
    lines += '<img width="30%" src="'+PSR+'_A1_tempo.png" alt="A1"></a> \n'
    lines += '<h4>A2</h4><a href="'+PSR+'_A2_tempo.png"> \n'
    lines += '<img width="30%" src="'+PSR+'_A2_tempo.png" alt="A2"></a></article> \n'

    lines += "<article> \n"
    lines += '<b>Date Antenna Nfils GTI Exposure SNR_par SNR_tim Glitch</b><br> \n'

    for idx in range(len(df)):
        antenna = df.antenna.loc[idx]
        gti = float(df.gti_percentage.loc[idx])
        exp = float(df.obs_duration.loc[idx])/3600.
        date = df.obs_date.loc[idx]
        nfils = df.nfils.loc[idx]
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
            pngs = [png.split('/')[-1] for png in pngs]
            if len(pngs) == 3:
                pngpar, pngtiming, pngmask = pngs
            elif len(pngs) == 2:
                pngtiming, pngmask = pngs
                pngpar = ''
            else:
                pngmask, pngtiming, pngpar = '', '', ''
        except:
            pngmask, pngtiming, pngpar = '', '', ''

        lines += '{} {} {} {:.2f}&percnt; {:.2f}hr {:.2f} {:.2f} {} \n'.format(date, antenna, nfils, gti, exp, snr_par, snr_timing, glitch)
        lines += '<a href="pngs/{}">MASK</a> <a href="pngs/{}">TIMING</a> <a href="pngs/{}">PAR</a><br>\n'.format(pngmask, pngtiming, pngpar)

    lines += '</article>\n\n'

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
    lines += '<article class="box page-content"><header><h2><a href="'+PSR+'/'+PSR+'.html">'+PSR+'</a></h2></header> \n'

    for antenna in antennas:
        try:
            idx = df[df.antenna == antenna].obs_date.idxmax()
        except:
            continue

        gti = float(df.gti_percentage.loc[idx])
        exp = float(df.obs_duration.loc[idx])/3600.
        date = df.obs_date.loc[idx]
        nfils = df.nfils.loc[idx]
        try:
            snr_par = float(df.snr_par.loc[idx])
        except:
            snr_par = -1
        try:
            snr_timing = float(df.snr_timing.loc[idx])
        except:
            snr_timing = -1

        glitch = df.glitch[idx]

        lines += '<h3>{}: observed on {} for a total of {:.2f} hr with {:.2f} &#37; GTI <br> \n'.format(antenna, date, exp, gti)
        lines += '      SNR_par: {:.2f}  ;  SNR_timing: {:.2f}  ;   Glitch: {}  ; Nfils: {} </h3> \n'.format(snr_par, snr_timing, glitch, nfils)
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

    file = open(DBPATH+'last_obs.html', 'w')
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

    # PSR/PSR.html
    HEADER = 'psr_header.txt'
    FOOTER = 'psr_footer.txt'
    print('-----------------')
    print('START psr.html')
    for pulsar in pulsars:
         if write_psr(pulsar, HEADER, FOOTER, WEBPATH, DBPATH) ==0:
               print('WRITTEN '+pulsar+'.html')
         else:
               print('ERROR in '+pulsar+'.html')
    print()
    
    # by_psr.html
    HEADER = 'by_psr_header.txt'
    FOOTER = 'by_psr_footer.txt'
    print('-----------------')
    print('START by_psr.html')
    if write_bypsr(pulsars, HEADER, FOOTER, WEBPATH, DBPATH) == 0:
        print('WRITTEN by_psr.html')
    else:
        print('ERROR by_psr.html')
    print()

    # last_obs/last_obs.html
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
