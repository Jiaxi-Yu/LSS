#!/bin/bash
#script to run main/daily randoms through for a given tracer type
#to be run after getting interaction node (e.g., via salloc -N 1 -C haswell -t 04:00:00 --qos interactive --account desi)
#1st argument should be tracer type and 2nd should be whether or not to reject qso targets

python mkCat_main_ran_px.py  --type $1  --basedir /global/cfs/cdirs/desi/survey/catalogs/ --verspec daily --rfa n --combhp n --combfull n --fullr y --notqso $2
python mkCat_main_ran_px.py  --type $1  --basedir /global/cfs/cdirs/desi/survey/catalogs/ --verspec daily --rfa n --combhp n --combfull y --fullr n --notqso $2 --minr 9
python mkCat_main_ran_px.py  --type $1  --basedir /global/cfs/cdirs/desi/survey/catalogs/ --verspec daily --rfa n --combhp n --combfull y --fullr n --notqso $2 --maxr 9
