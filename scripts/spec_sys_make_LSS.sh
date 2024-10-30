#!/bin/bash

source /global/common/software/desi/users/adematti/cosmodesi_environment.sh main
source activate spec_sys

survey=Y1
specver=iron
mockver='v4_1'
mockdir=/dvs_ro/cfs/cdirs/desi/survey/catalogs/${survey}/mocks/SecondGenMocks/AbacusSummit_${mockver}
export OMP_NUM_THREADS=64

tracers=(ELG_LOPnotqso LRG QSO)
notqso=(y n n)
names=(ELG_LOP LRG QSO)
nran=(10 8 2)

# the directory to save the mocks
your_choice=test

# the suffix of redshift column without the redsihft error
remove_zerror=None

for tp in `seq 2 2`; do
    if [ "$tracers[${tp}]" == "ELG_LOPnotqso" ]; then
        catas="realistic failures slitless"
    else
        catas="realistic failures"
    fi
    for MOCKNUM in `seq 0 0`; do
        fn=${SCRATCH}/${your_choice}/altmtl${MOCKNUM}/${specver}/mock${MOCKNUM}/LSScats
        # get the SecondGen AbacusSummit mocks (25 realisations in total)
        if [ ! -e "${fn}" ]; then
            echo "home directory ${fn} does not exists, creating it..."
            mkdir -p ${fn}
        fi
        if [ ! -e "${fn}/${tracers[${tp}]}_full_HPmapcut.dat.fits" ]; then
            echo "Abacus mocks do not exists, copying them from the official directory ..."
            cp ${mockdir}/altmtl${MOCKNUM}/mock${MOCKNUM}/LSScats/${tracers[${tp}]}_*full_HPmapcut.*.fits ${fn}
            cp ${mockdir}/altmtl${MOCKNUM}/mock${MOCKNUM}/LSScats/${tracers[${tp}]}_frac_tlobs.fits ${fn}
        fi
        echo "All files are ready. Let's create the clustering catalogues with spectroscopic systematics"

        # From the AbacusSummit mocks (as the real Universe without any selection) to LSS clustering mocks
        ## implement the catastrophics in this step
        outputs=${fn}/${tracers[${tp}]}_SGC_0_clustering.ran.fits
        echo $outputs
        if [ ! -e "${outputs}" ]; then
            echo "clustering catalogues do not exists. Let's make them from scratch"
            srun -N 1 -n 1 -c 64 -C cpu -t 04:00:00 --qos interactive --account desi python ${LSSCODE}/LSS/scripts/mock_tools/mkCat_SecondGen_amtl.py --base_output ${SCRATCH}/test/altmtl${MOCKNUM} --mockver ab_secondgen --mocknum ${MOCKNUM}  --survey ${survey} --add_gtl y --specdata ${specver} --tracer ${names[${tp}]} --notqso ${notqso[${tp}]} --minr 0 --maxr ${nran[${tp}]} --fulld n --fullr n --apply_veto n --use_map_veto _HPmapcut --mkclusran y  --nz y --mkclusdat y --splitGC y --targDir ${mockdir} --outmd 'notscratch' --addcatas ${catas} --remove_zerror ${remove_zerror}
        fi
        echo "clustering ${outputs} are complete, continue to the next mock"

        # update the WEIGHT_FKP column in the LSS catalogues 
        #echo srun -N 1 -n 1 -c 64 -C cpu -t 04:00:00 --qos interactive --account desi python catas_FKP.py ${SCRATCH}/test/altmtl${}/mock${}/LSScats/
    done
done







