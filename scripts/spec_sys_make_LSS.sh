#!/bin/bash
export LSSCODE=${HOME}/codes
cd ${LSSCODE}/LSS
PYTHONPATH=$PYTHONPATH:${LSSCODE}/LSS/py
PATH=$PATH:${LSSCODE}/LSS/bin

survey=Y1
tracers=(ELG_LOPnotqso LRG QSO)
names=(ELG_LOP LRG QSO)
nran=(10 8 4)
mockver='v4_1'
mockdir=/dvs_ro/cfs/cdirs/desi/survey/catalogs/${survey}/mocks/SecondGenMocks/AbacusSummit_${mockver}
for tp in `seq 0 0`; do
    for MOCKNUM in `seq 0 0`; do
        fn=${SCRATCH}/test/altmtl${MOCKNUM}/mock${MOCKNUM}/LSScats
        # get the SecondGen AbacusSummit mocks (25 realisations in total)
        if [ ! -d "${fn}" ]; then
            echo echo "home directory ${fn} do not exists, creating it..."
            echo mkdir -p ${fn}
            echo cp ${mockdir}/altmtl${MOCKNUM}/mock${MOCKNUM}/LSScats/${tracers[${tp}]}_*full_HPmapcut.*.fits ${fn}
            echo cp ${mockdir}/altmtl${MOCKNUM}/mock${MOCKNUM}/LSScats/${tracers[${tp}]}_frac_tlobs.fits ${fn}
        else
            echo "home directory ${fn} exists, continue to check the clustering catalogues..."
        fi

        # From the AbacusSummit mocks (as the real Universe without any selection) to LSS clustering mocks
        ## implement the catastrophics in this step
        outputs=${fn}/ELG_LOPnotqso_SGC_17_clustering.ran.fits
        if [ ! -f "${outputs}" ]; then
            echo "clustering ${outputs} are not complete, making the clustering*fits files"
            echo srun -N 1 -n 1 -c 64 -C cpu -t 04:00:00 --qos interactive --account desi python ${LSSCODE}/LSS/scripts/mock_tools/mkCat_SecondGen_amtl.py --base_output ${SCRATCH}/test/altmtl${MOCKNUM} --mockver ab_secondgen --mocknum ${MOCKNUM}  --survey ${survey} --add_gtl y --specdata iron --tracer ${names[${tp}]} --notqso y --minr 0 --maxr ${nran[${tp}]} --fulld n --fullr n --apply_veto n --use_map_veto _HPmapcut --mkclusran y  --nz y --mkclusdat y --splitGC y --targDir ${mockdir} --outmd 'notscratch' 
        else
            echo "clustering ${outputs} are complete, continue to the next mock"
        fi

        # update the WEIGHT_FKP column in the LSS catalogues 
        echo srun -N 1 -n 1 -c 64 -C cpu -t 04:00:00 --qos interactive --account desi python catas_FKP.py ${SCRATCH}/test/altmtl${}/mock${}/LSScats/
    done
done







