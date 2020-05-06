import os, sys, subprocess
import pandas as pd

dbg = False


def pandasANDtext(PSR):
    # leer los ascii actuales como pandas
    df = pd.read_csv(PSR+'.txt', delim_whitespace=True)

    # guardar los pandas como json
    df.to_json(PSR+'.json')

    # leer los json como pandas
    df = pd.read_json(PSR+'.json')


def CreateThumbnail(file):
    subprocess.call(['convert', '-thumbnail 500',
                    file, file+'.thumb.jpg'])


def get_observed_pulsars(path):
    pulsars = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
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


def get_lastobs(PSR, DBPATH):
    if dbg:
        print(PSR)

    # FUTURE: READ THIS INFO FROM DATABASE
    LAST_DATE = '2020/01/10'
    LAST_EXP = '2.75'

    lines = "<!-- "+PSR+" --> \n"
    lines += '<article class="box page-content"><header><h2>'+PSR+'</h2></header> \n'
    lines += '<h3>Observed on '+LAST_DATE+' for a total of '+LAST_EXP+' hr</h3> \n'
    lines += '<div class="row 200%"> <div class="12u"> \n'
    lines += '<section class="box features"><div><div class="row"> \n'

    lines += '<div class="3u 6u(mobile)"><section class="box feature"> \n'
    lines += '<a href="last_obs/'+PSR+'/tempo.png"><img width="100%" src="last_obs/'+PSR+'/tempo.png" alt=""></a> \n'
    lines += '</section></div> \n'
    lines += '<div class="3u 6u(mobile)"><section class="box feature"> \n'
    lines += '<a href="last_obs/'+PSR+'/presto.png"><img width="100%" src="last_obs/'+PSR+'/presto.png" alt=""></a> \n'
    lines += '</section></div> \n'
    lines += '<div class="3u 6u(mobile)"><section class="box feature"> \n'
    lines += '<a href="last_obs/'+PSR+'/mask.png"><img width="100%" src="last_obs/'+PSR+'/mask.png" alt=""></a> \n'
    lines += '</section></div> \n'

    lines += '</div></div></section> \n'
    lines += '</div></div> \n'
    lines += '</article> \n'

    if dbg:
        print()

    return lines


def write_lastobs(pulsars, HEADER, FOOTER, WEBPATH, DBPATH):
    header = open(WEBPATH+HEADER).readlines()
    footer = open(WEBPATH+FOOTER).readlines()

    content = ''
    for psr in pulsars:
        content += get_lastobs(psr,DBPATH)

    file = open(WEBPATH+'last_obs_2.html', 'w')
    file.writelines(header)
    file.writelines(content)
    file.writelines(footer)
    file.close()
    return 0


# RUN MAIN CODE
if __name__ == "__main__":

    WEBPATH = "/home/fgarcia/github/puma/puglieseweb/"
    DBPATH = WEBPATH+'database/'
    # DBPATH/database/PSRNAME/mask_DATE.png presto_DATE.png tempo.png
    # DBPATH/last_obs/PSRNAME/mask.png presto.png tempo.png

    dbg = False
    print()
    print('READING PULSARS FROM DB AT '+DBPATH)
    pulsars = get_observed_pulsars(DBPATH)
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
