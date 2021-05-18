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
        lines += '<p><a href="https://ui.adsabs.harvard.edu/search/q=((%3Dabs%3A%22PSR%20'+PSR+'%22%20OR%20simbid%3A%223510432%22%20OR%20nedid%3A%220%22)%20database%3Aastronomy)&sort=date%20desc%2C%20bibcode%20desc&p_=0">ADS</a>&nbsp|&nbsp;'
        lines += '<a href="https://www.atnf.csiro.au/research/pulsar/psrcat/proc_form.php?version=1.63&startUserDefined=true&c1_val=&c2_val=&c3_val=&c4_val=&sort_attr=jname&sort_order=asc&condition=&pulsar_names='+PSR+'&ephemeris=long&submit_ephemeris=Get+Ephemeris&coords_unit=raj%2Fdecj&radius=&coords_1=&coords_2=&style=Long+with+last+digit+error&no_value=*&fsize=3&x_axis=&x_scale=linear&y_axis=&y_scale=linear&state=query">ATNF</a></p>'

        lines += '<h3>Historical Tempo Plots</h3> \n'
        lines += '<h4>A1</h4><a class="swipebox" href="'+PSR+'/'+PSR+'_A1_tempo.png"> \n'
        lines += '<img width="30%" src="'+PSR+'/'+PSR+'_A1_tempo.png" alt="A1"></a> \n'
        lines += '<h4>A2</h4><a class="swipebox" href="'+PSR+'/'+PSR+'_A2_tempo.png"> \n'
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
        df.sort_values(by=['obs_date','antenna'],ascending=False, inplace=True)
    except:
        return -1

    lines = "<!-- "+PSR+" --> \n"
    lines += '<article class="box page-content"><header><h2><a href="'+PSR+'.html">'+PSR+'</a></h2></header> \n'
    lines += '<p><a href="https://ui.adsabs.harvard.edu/search/q=((%3Dabs%3A%22PSR%20'+PSR+'%22%20OR%20simbid%3A%223510432%22%20OR%20nedid%3A%220%22)%20database%3Aastronomy)&sort=date%20desc%2C%20bibcode%20desc&p_=0">ADS</a>&nbsp|&nbsp;'
    lines += '<a href="https://www.atnf.csiro.au/research/pulsar/psrcat/proc_form.php?version=1.63&startUserDefined=true&c1_val=&c2_val=&c3_val=&c4_val=&sort_attr=jname&sort_order=asc&condition=&pulsar_names='+PSR+'&ephemeris=long&submit_ephemeris=Get+Ephemeris&coords_unit=raj%2Fdecj&radius=&coords_1=&coords_2=&style=Long+with+last+digit+error&no_value=*&fsize=3&x_axis=&x_scale=linear&y_axis=&y_scale=linear&state=query">ATNF</a></p>'
    lines += '<h3>Historical Tempo Plots</h3> \n'
    lines += '<h4>A1</h4><a class="swipebox" href="'+PSR+'_A1_tempo.png"> \n'
    lines += '<img width="30%" src="'+PSR+'_A1_tempo.png" alt="A1"></a> \n'
    lines += '<h4>A2</h4><a class="swipebox" href="'+PSR+'_A2_tempo.png"> \n'
    lines += '<img width="30%" src="'+PSR+'_A2_tempo.png" alt="A2"></a> \n'
    lines += '<h3>Pulse Profile Template</h3> \n'
    lines += '<a class="swipebox" href="'+PSR+'_template.png"> \n'
    lines += '<img width="30%" src="'+PSR+'_template.png" alt="template"></a> \n'
    lines += '</article>\n'

    lines += '<article> <table>\n'
    lines += '<thead ><tr>\n'
    if '0437-4715' in PSR:
        lines += '<th><b>Date</b></th><th><b>Antenna</b></th><th><b>Nfils</b></th><th><b>GTI</b></th><th><b>Exposure</b></th><th><b>SNR_par</b></th><th><b>SNR_tim</b></th>\n'
        lines += '</tr></thead><tbody>\n'
    else:
        lines += '<th><b>Date</b></th><th><b>Antenna</b></th><th><b>Nfils</b></th><th><b>GTI</b></th><th><b>Exposure</b></th><th><b>SNR_par</b></th><th><b>SNR_tim</b></th><th><b>Jump</b></th><th><b>Glitch</b></th>\n'
        lines += '</tr><tr>'
        lines += '<th> </th><th><b>Blue Alert</b></th><th><b>Yellow Alert</b></th><th><b>Red Alert</b></th><th><b>Thresh</b></th><th><b>P_err</b></th><th><b>P_eph</b></th><th><b>P_obs</b></th>\n'
        lines += '</tr></thead><tbody>\n'

    for idx in df.index:
        antenna = df.antenna.loc[idx]
        gti = float(df.gti_percentage.loc[idx])
        exp = float(df.obs_duration.loc[idx])/3600.
        date = df.obs_date.loc[idx]
        nfils = int(df.nfils.loc[idx])
        try:
            nfils_total = int(df.nfils_total.loc[idx])
        except:
            nfils_total = -1
        try:
            snr_par = float(df.snr_par.loc[idx])
        except:
            snr_par = -1
        try:
            snr_timing = float(df.snr_timing.loc[idx])
        except:
            snr_timing = -1

        try:
            glitch = df.glitch.loc[idx]
            jump = float(df.jump.loc[idx])
        except:
            glitch = jump = -1

        try: blue_alert = df.blue_alert.loc[idx]
        except: blue_alert = -1
        try: yellow_alert = df.yellow_alert.loc[idx]
        except: yellow_alert = -1
        try: red_alert = df.red_alert.loc[idx]
        except: red_alert = -1

        try:
            thresh = float(df.thresh.loc[idx])
        except:
            thresh = -1
        try:
            P_obs = float(df.P_obs.loc[idx])
            P_eph = float(df.P_eph.loc[idx])
            err_P = float(df.err_P.loc[idx])
        except:
            P_obs = P_eph = err_P = -1

        try:
            pngsdir = 'pngs/'
            pngs = df.pngs[idx]
            pngs = [png.split('/')[-1] for png in pngs]
            pngmask = pngtiming = pngpar = ''
            for png in pngs:
                 if 'rfifind.png' in png:
                     pngmask = pngsdir + png
                 elif 'prepfold' in png:
                     if 'timing' in png:
                          pngtiming = pngsdir + png
                     elif 'par' in png:
                          pngpar = pngsdir + png
        except:
            pngmask, pngtiming, pngpar = '', '', ''

        lines += '<tr>\n'
        if '0437-4715' in PSR:
            lines += '   <td>{}</td><td>{}</td><td>{}</td><td>{:.2f}&percnt;</td><td>{:.2f}hr</td><td>{:.2f}</td><td>{:.2f}</td>\n'.format(date, antenna, nfils_total, gti, exp, snr_par, snr_timing)
            lines += '   <td><a class="swipebox" href="{}">MASK</a> <a class="swipebox" href="{}">TIMING</a></td>\n'.format(pngmask, pngtiming)
        else:
            lines += '   <td>{}</td><td>{}</td><td>{}</td><td>{:.2f}&percnt;</td><td>{:.2f}hr</td><td>{:.2f}</td><td>{:.2f}</td><td>{:.8f}</td><td><b>{}</b></td>\n'.format(date, antenna, nfils, gti, exp, snr_par, snr_timing, jump, glitch)
            lines += '</tr><tr>\n'
            lines += '   <td> </td><td style="color:blue">{}</td><td style="color:yellow">{}</td><td style="color:red">{}</td><td>{:.8f}</td><td>{:.8f}</td><td> {:.8f}</td><td>{:.8f}</td>\n'.format(blue_alert, yellow_alert, red_alert, thresh, err_P, P_eph, P_obs)
            lines += '   <td><a class="swipebox" href="{}">MASK</a> <a class="swipebox" href="{}">TIMING</a> <a class="swipebox" href="{}">PAR</a></td>\n'.format(pngmask, pngtiming, pngpar)
        lines += '</tr>\n'

    lines += '</tbody> </table> </article>\n\n'

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
    lines += '<p><a href="https://ui.adsabs.harvard.edu/search/q=((%3Dabs%3A%22PSR%20'+PSR+'%22%20OR%20simbid%3A%223510432%22%20OR%20nedid%3A%220%22)%20database%3Aastronomy)&sort=date%20desc%2C%20bibcode%20desc&p_=0">ADS</a>&nbsp|&nbsp;'
    lines += '<a href="https://www.atnf.csiro.au/research/pulsar/psrcat/proc_form.php?version=1.63&startUserDefined=true&c1_val=&c2_val=&c3_val=&c4_val=&sort_attr=jname&sort_order=asc&condition=&pulsar_names='+PSR+'&ephemeris=long&submit_ephemeris=Get+Ephemeris&coords_unit=raj%2Fdecj&radius=&coords_1=&coords_2=&style=Long+with+last+digit+error&no_value=*&fsize=3&x_axis=&x_scale=linear&y_axis=&y_scale=linear&state=query">ATNF</a></p>'


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
        if '0437-4715' not in PSR:
	        lines += '<div class="3u 6u(mobile)"><section class="box feature"> \n'
	        lines += '<a class="swipebox" href="last_obs/'+PSR+'_'+antenna+'_par.png"><img width="100%" src="last_obs/'+PSR+'_'+antenna+'_par.jpg" alt=""></a> \n'
		lines += '</div>'
        lines += '<div class="3u 6u(mobile)"><section class="box feature"> \n'
        lines += '<a class="swipebox" href="last_obs/'+PSR+'_'+antenna+'_timing.png"><img width="100%" src="last_obs/'+PSR+'_'+antenna+'_timing.jpg" alt=""></a> \n'
        lines += '</div> \n'
        lines += '<div class="3u 6u(mobile)"><section class="box feature"> \n'
        lines += '<a class="swipebox" href="last_obs/'+PSR+'_'+antenna+'_mask.png"><img width="100%" src="last_obs/'+PSR+'_'+antenna+'_mask.jpg" alt=""></a> \n'
        lines += '</div> \n'
        lines += '<div class="3u 6u(mobile)"><section class="box feature"> \n'
        lines += '<a class="swipebox" href="last_obs/'+PSR+'_'+antenna+'_tempo.png"><img width="100%" src="last_obs/'+PSR+'_'+antenna+'_tempo.jpg" alt=""></a> \n'
        lines += '</div> \n'
        lines += '</section> \n'
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

    if len(sys.argv) > 1:
         WEBPATH = sys.argv[1]
         DBPATH = sys.argv[2]

    dbg = False
    print('\n>>>READING PULSARS FROM DB AT '+DBPATH)
    pulsars = get_observed_pulsars(DBPATH)
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
    print('-----------------')

    # by_psr.html
    HEADER = 'by_psr_header.txt'
    FOOTER = 'by_psr_footer.txt'
    print('-----------------')
    print('START by_psr.html')
    if write_bypsr(pulsars, HEADER, FOOTER, WEBPATH, DBPATH) == 0:
        print('WRITTEN by_psr.html')
    else:
        print('ERROR by_psr.html')
    print('-----------------')

    # last_obs/last_obs.html
    HEADER = 'last_obs_header.txt'
    FOOTER = 'last_obs_footer.txt'
    print('-------------------')
    print('START last_obs.html')
    if write_lastobs(pulsars, HEADER, FOOTER, WEBPATH, DBPATH) == 0:
        print('WRITTEN last_obs.html')
    else:
        print('ERROR last_obs.html')
    print('-------------------')

    # EXIT PROGRAM
    print('>>> FINISHED UPDATING WEBPAGE AT '+WEBPATH+'\n\n')
