#!/bin/env bash
#"${1}/exiftool" -api largefilesupport -ee -q -m -p insv_gpx.fmt -ext insv $2 > "${2}/insv.gpx"
"${1}/exiftool" -api largefilesupport -ee -q -m -p insp_gpx.fmt -ext insp $2 > "${2}/insp.gpx"
