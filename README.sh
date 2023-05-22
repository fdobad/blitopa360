#!/bin/env bash
# 78 : bad
# 79 : good
# 80 : good
# 81 : bad
# 82 : good
# 83 : bad
# -c "%+.5f" -d "%s"

file_prefix='IMG_20230520_121213_00_0'
gb=''
for i in {78..83}; do
  if [[ $i -eq 79 || $i -eq 80 || $i -eq 82 ]]; then
    echo "good file $i"
    gb='good'
  else
    echo "bad file $i"
    gb='bad'
  fi
  ../exiftool -ee -n "$file_prefix$i.insp" > ee$i$gb.txt
  ../exiftool -ee -n -p '${gpslatitude},${gpslongitude},${gpsaltitude}' $file_prefix$i.insp 2>/dev/null > latlonele$i$gb.txt
done

head -n 2 force*

for i in {79..83}; do
  if [[ $i -eq 79 || $i -eq 80 || $i -eq 82 ]]; then
    gb='good'
  else
    gb='bad'
  fi
  echo -e "$gb file $i \t Accelerometer $(grep Accelerometer ee$i$gb.txt | wc -l) \t GPS Speed $(grep 'GPS Speed' ee$i$gb.txt | wc -l) \t forced_lat-1 $(cat latlonele$i$gb.txt | wc -l)"
done

cd ..
./exiftool -ee -n -p '${gpslatitude},${gpslongitude},${gpsaltitude}' -ext insp test 2>/dev/null > all_dir.txt
cat all_dir.txt | wc -l
# 66
./exiftool -ee -n -p '$ImageDescription,${gpslatitude},${gpslongitude},${gpsaltitude}' -ext insp test 2>/dev/null > one_dir.txt
cat one_dir.txt | wc -l
# 6 
./exiftool -ee -n -p '${gpsdatetime},${gpslatitude},${gpslongitude},${gpsaltitude}' -ext insp test 2>/dev/null > ok_dir.txt
cat ok_dir.txt | wc -l
# 60
./exiftool -ee -n -j -g:7:8 -gpsdatetime -gpslatitude -gpslongitude -gpsaltitude -ext insp test 2>/dev/null > test_dir.txt
cat test_dir.txt | wc -l
head -n 12 test_dir.txt
# 2 per file

exit

  #../exiftool -ee -f -p '${gpsdatetime},${gpslatitude},${gpslongitude},${gpsaltitude}' $file_prefix$i.insp 2>/dev/null | grep -v -e '-,-,-,-' > force$i$gb.txt
  #../exiftool -ee -gpsposition -gpsaltitude $file_prefix$i.insp > pos$i$gb.txt
  #../exiftool -ee -p '$gpslatitude $gpslongitude $gpsaltitude' "$file_prefix$i.insp" > pos$i$gb.txt
  #../exiftool -ee -gpslatitude -gpslongitude -gpsaltitude "$fileprefix$i.insp" > pos$i.txt

$ ../exiftool -ee -c "%+.5f" -d "%s" -p '$ImageDescription,$CreateDate,${gpslatitude},${gpsposition},${gpslongitude}' IMG_20230520_121213_00_080.insp 2>/dev/null
IMG_20230520_121213_00_080.insp,1684599378,-33.44925,-33.44925, -70.57045,-70.57045

$ ../exiftool -ee -c "%+.5f" -d "%s" -p '$ImageDescription,$CreateDate,${gpslatitude},${gpsposition},${gpslongitude}' IMG_20230520_121213_00_081.insp 2>/dev/null
IMG_20230520_121213_00_081.insp,1684599383,-33.43704,-33.43704, -70.58236,-70.58236

$ ../exiftool -ee -c "%+.6f" -p '${gpslatitude} ${gpslongitude}' IMG_20230520_121213_00_080.insp 2>/dev/null
-33.449247 -70.570451
-33.449247 -70.582382
-33.449247 -70.582382
-33.449247 -70.582382
-33.449247 -70.582382
-33.449247 -70.582382
-33.449247 -70.582382
-33.449247 -70.582382
-33.449188 -70.582377
-33.449188 -70.582377
-33.449188 -70.582377

$ ../exiftool -ee -c "%+.6f" -p '${gpslatitude} ${gpslongitude}' IMG_20230520_121213_00_081.insp 2>/dev/null
-33.437036 -70.582362
-33.448967 -70.582362
-33.448967 -70.582362
-33.448967 -70.582362
-33.448967 -70.582362
-33.448967 -70.582362
-33.448967 -70.582362
-33.448967 -70.582362
-33.448967 -70.582362
-33.448918 -70.582358
-33.448918 -70.582358
