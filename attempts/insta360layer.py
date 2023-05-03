#!/bin/env python3
from pathlib import Path
from subprocess import Popen, PIPE
from shlex import split as shlex_split
from pandas import Timestamp, DataFrame

df = DataFrame( columns=('dt','lat','lon','ele'))

cwd = Path.cwd()
media_dir = cwd / 'media360'
exif_directory = cwd / 'blitopa/exiftool'
assert media_dir.is_dir() and exif_directory.is_dir()
image_file_list = sorted( media_dir.glob('*.insp'))
assert len(image_file_list)>0

#createdate;DateFmt('%s')
# Timestamp(ds.iloc[-1]) + timedelta(hours=1)
# Timestamp(x).isoformat(timespec='seconds')
img_cmd = "./exiftool -ee3 -p '${DateTimeOriginal} ${gpslatitude#} ${gpslongitude#} ${gpsaltitude#}' "
for i,afile in enumerate(image_file_list):
    cmd = img_cmd + str(afile)
    print('cmd',cmd)
    process = Popen( shlex_split(cmd), stdout=PIPE, stderr=PIPE, cwd=exif_directory)
    stdout, stderr = process.communicate()
    print('stdout',stdout)#.decode().replace('\n',''))
    print('stdout',stdout.decode().split())#.decode().replace('\n',''))
    date,time,lat,lon,ele = stdout.decode().split()
    dt = Timestamp(date.replace(':','-')+' '+time).isoformat(timespec='seconds')
    df.loc[i] = [dt, float(lat), float(lon), float(ele)]
    print(dt,lat,lon,ele)
    break
    dt,lat,lon,alt = stdout.split()
    print('stderr',stderr)#.decode().replace('\n',''))

in_directory = Path( media_dir )
video_file_list = in_directory.glob('*.mp4')

vid_cmd = '''./exiftool -b -api largefilesupport -ee -p "${GPSDateTime;DateFmt('%s')} ${gpslatitude#} ${gpslongitude#}" '''

def loopcmd(acmd, afile_list):
    for afile in afile_list:
        cmd = acmd + str(afile)
        print('cmd',cmd)
        process = Popen( shlex_split(cmd), stdout=PIPE, stderr=PIPE, cwd=exif_directory)
        stdout, stderr = process.communicate()
        print('stdout',stdout)#.decode().replace('\n',''))
        print('stderr',stderr)#.decode().replace('\n',''))

loopcmd(vid_cmd, video_file_list )
loopcmd(img_cmd, image_file_list )


