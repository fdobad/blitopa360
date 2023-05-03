#!/bin/env bash
touch "${1}/out.txt"
## VIDEO 
#for file in $(find mediaBAK -type f -regex '.*.mp4\b' );
#do
#    echo "processing ${file}"
#    exiftool/exiftool -b -api largefilesupport -ee -p '${GPSDateTime;DateFmt("%s")} ${gpslatitude#} ${gpslongitude#}' $file > "${file/mp4/txt}"
#done
# IMAGE
for file in $(find $1 -type f -regex '.*.insp\b' );
do
#    echo "processing ${file}"
#    #exiftool/exiftool -api largefilesupport -ee -p HowTo/fdo_gpx.fmt $file > "${file/insp/txt}"
#    #exiftool/exiftool -api largefilesupport -p HowTo/fdo_gpx.fmt $file > "${file/insp/txt}"
    exiftool/exiftool -ee3 -p '${filename#} ${createdate#} ${gpslatitude#} ${gpslongitude#} ${gpsaltitude#}' $file >> "${1}/out.txt" 2>/dev/null
done

# INVS 
#for file in $(find mediaBAK -type f -regex '.*_00_[0-9]*.insv\b' );
#do
#    echo "processing ${file}"
#    #GPSLatitude/Longitude/Speed/Altitude/Track
#    exiftool/exiftool -b -api largefilesupport -ee -p '${GPSDateTime;DateFmt("%s")} ${gpslatitude#} ${gpslongitude#} ${gpsaltitude#}' $file > "${file/insv/txt}"
#done
