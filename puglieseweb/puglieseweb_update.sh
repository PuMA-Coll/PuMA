export WEBPATH="/home/observacion/scratchdisk/PuGli-S/puglieseweb/"
export DBPATH="/home/observacion/scratchdisk/PuGli-S/"

# Generate thumbnails
echo
echo Generating thumbnails ...
cd $DBPATH/last_obs/
~/bin/thumbnailer.sh

# Get RFI plots from GANCIO
echo Getting RFI plots
cd $DBPATH/rfi/plots/
wget -d http://tux.iar.unlp.edu.ar/~ggancio/pub/rfi/plots/Power_wide.png
wget -d http://tux.iar.unlp.edu.ar/~ggancio/pub/rfi/plots/Spectrum_limited.png
wget -d http://tux.iar.unlp.edu.ar/~ggancio/pub/rfi/plots/Spectrum_wide.png
cd $DBPATH

#Update the full website
cd $WEBPATH
python ./puglieseweb_update.py $WEBPATH $DBPATH

echo Updating website ...
#Update Last-Obs
rsync -av $DBPATH/last_obs/ lacar:public_html/private/last_obs/

#Update Webpage
rsync -av --exclude '*txt' --exclude '*md' --exclude '*py' \
          --exclude '*sh' $WEBPATH/ lacar:public_html/

#Update PSR database
rsync -av --exclude '*pfd' --exclude '*polycos' --exclude '*tim' --exclude '*json' \
          --exclude '*res' $DBPATH/J* lacar:public_html/private/

#Update RFI plots
scp $DBPATH/rfi/plots/* lacar:public_html/private/rfi/plots/

#Update last_obs.html by_psr.html
scp $DBPATH/*html lacar:public_html/private/

#Update diskspace
df -h | grep "sd" > $DBPATH/diskspace.txt
scp $DBPATH/diskspace.txt lacar:public_html/private/

#Update date
~/bin/get_mjd_now.py > $DBPATH/mjd.txt
scp $DBPATH/mjd.txt lacar:public_html/private/

echo
echo 'Everything is up-to-date now.'
echo
