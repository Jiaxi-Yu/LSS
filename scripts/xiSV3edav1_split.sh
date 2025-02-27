#!/bin/bash
source /global/common/software/desi/users/adematti/cosmodesi_environment.sh main

source activate spec_sys
export LSSCODE=${HOME}/codes_mine
PYTHONPATH=$PYTHONPATH:${LSSCODE}/LSS/py
PATH=$PATH:${LSSCODE}/LSS/bin
cd $LSSCODE/LSS
git checkout split

SURVEY=sv3
WT='default_angular_bitwise_FKP'
BASEDIR=$SCRATCH/edav1/sv3/LSScats/
OUTDIR=$BASEDIR/xi/
#REGIONS="NGC SGC"
REGIONS="NGC"

# copy full and change their names
#cp /dvs_ro/cfs/cdirs/desi/survey/catalogs/edav1/sv3/LSScats/full/LRG_full.dat.fits $SCRATCH/edav1/sv3/LSScats/LRG_high_full.dat.fits
#cp /dvs_ro/cfs/cdirs/desi/survey/catalogs/edav1/sv3/LSScats/full/LRG_full.dat.fits $SCRATCH/edav1/sv3/LSScats/LRG_low_full.dat.fits
#for g in `seq 0 17`; do 
#    cp /dvs_ro/cfs/cdirs/desi/survey/catalogs/edav1/sv3/LSScats/full/LRG_${g}_full.ran.fits $SCRATCH/edav1/sv3/LSScats/full/LRG_high_${g}_full.ran.fits
#    cp /dvs_ro/cfs/cdirs/desi/survey/catalogs/edav1/sv3/LSScats/full/LRG_${g}_full.ran.fits $SCRATCH/edav1/sv3/LSScats/full/LRG_low_${g}_full.ran.fits
#done
srun -N 1 -C gpu --gpus 4 -t 04:00:00 --qos interactive --account desi_g  python xirunpc.py --gpu --tracer LRG_high --basedir $BASEDIR --outdir $OUTDIR --survey $SURVEY --region $REGIONS --weight_type $WT --nran 18 --bin_type log --corr_type smu 
srun -N 1 -C cpu -n 1 -c 64 -t 04:00:00 --qos interactive --account desi  python xirunpc.py --tracer LRG_high --basedir $BASEDIR --outdir $OUTDIR --survey $SURVEY --region $REGIONS --weight_type $WT --nran 18 --bin_type log --corr_type smu 

--njack 128 &
srun -N 1 -C gpu --gpus 4 -t 04:00:00 --qos interactive --account desi_g  python xirunpc.py --gpu --tracer LRG_low --basedir $BASEDIR --outdir $OUTDIR --survey $SURVEY --region $REGIONS --weight_type $WT --nran 18 --bin_type log --corr_type smu --njack 128 &

srun -N 1 -C gpu --gpus 4 -t 04:00:00 --qos interactive --account desi_g  python xirunpc.py --gpu --tracer LRG_high LRG_low --basedir $BASEDIR --outdir $OUTDIR --survey $SURVEY --region $REGIONS --weight_type $WT --nran 18 --bin_type log --corr_type smu --njack 128
