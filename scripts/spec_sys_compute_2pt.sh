#!/bin/bash

# load the environment
source /global/common/software/desi/users/adematti/cosmodesi_environment.sh main
source activate spec_sys

survey=Y1
specver=iron
mockver=v4_1
weight=default_FKP
#_angular_pip maybe for later
export OMP_NUM_THREADS=64

tracers=(ELG_LOPnotqso LRG QSO)
names=(ELG_LOP LRG QSO)
nran=(10 8 4)
zfin=('1.1_1.6' '0.8_1.1' '0.8_2.1')

# the directory to save the mocks
your_choice=test

# the suffix of redshift column without the redsihft error
remove_zerror=None

# implement the spectroscopic systematics
for tp in `seq 0 2`; do
    if [ "$tracers[${tp}]" == "ELG_LOPnotqso" ]; then
        catas_types=(realistic failures slitless)
    else
        catas_types=(realistic failures)
    fi
    for MOCKNUM in `seq 0 0`; do
        fn=${SCRATCH}/${your_choice}/altmtl${MOCKNUM}/${specver}/mock${MOCKNUM}/LSScats

        # standard 2pcf
        outputs=${fn}/smu/xipoles_${tracers[${tp}]}_GCcomb_${zfin[${tp}]}_${weight}_lin10_njack0_nran${nran[${tp}]}_split20.txt
        if [ ! -f "${outputs}" ]; then
            echo "calculate clustering ${outputs}"
            echo srun -N 1 -C gpu -t 04:00:00 --gpus 4 --qos interactive --account desi_g python ${LSSCODE}/LSS/scripts/xirunpc.py --gpu --tracer ${tracers[${tp}]} --region NGC SGC --corr_type smu --weight_type ${weight} --njack 0 --nran ${nran[${tp}]} --basedir ${fn}  --outdir ${fn}
        fi
        # 2pcf without 1.31<z<1.33
        outputs=${fn}/smu/xipoles_${tracers[${tp}]}_GCcomb_${zfin[${tp}]}elgzcatas_${weight}_lin10_njack0_nran18_split20.txt
        if [ ! -f "${outputs}" ]; then
            echo "calculate clustering ${outputs}"
            echo srun -N 1 -C gpu -t 04:00:00 --gpus 4 --qos interactive --account desi_g python ${LSSCODE}/LSS/scripts/xirunpc.py --gpu --tracer ${tracers[${tp}]} --region NGC SGC --corr_type smu --weight_type ${weight} --njack 0 --nran ${nran[${tp}]} --basedir ${fn}  --outdir ${fn} --option elgzcatas
        fi
        # standard pk
        outputs=${fn}/pk/pkpoles_${tracers[${tp}]}_GCcomb_${zfin[${tp}]}_${weight}_lin.npy
        if [ ! -f "${outputs}" ]; then
            if [ ${MOCKNUM} == "0" ]; then
                echo "calculate with window clustering ${outputs}"
                echo srun -N 1 -n 64 -C cpu -t 04:00:00 --qos interactive --account desi python ${LSSCODE}/LSS/scripts/pkrun.py --tracer ${tracers[${tp}]} --region NGC SGC --weight_type ${weight} --rebinning y --nran ${nran[${tp}]} --basedir ${fn} --outdir ${fn}  --calc_win y
            else
                echo "calculate without window clustering ${outputs}"
                echo srun -N 1 -n 64 -C cpu -t 04:00:00 --qos interactive --account desi python ${LSSCODE}/LSS/scripts/pkrun.py --tracer ${tracers[${tp}]} --region NGC SGC --weight_type ${weight} --rebinning y --nran ${nran[${tp}]} --basedir ${fn} --outdir ${fn}        
            fi
        fi
        # pk without 1.31<z<1.33
        outputs=${fn}/pk/pkpoles_${tracers[${tp}]}_GCcomb_${zfin[${tp}]}elgzcatas_${weight}_lin.npy
        if [ ! -f "${outputs}" ]; then
            if [ ${MOCKNUM} == "0" ]; then
                echo "calculate with window clustering ${outputs}"
                echo srun -N 1 -n 64 -C cpu -t 04:00:00 --qos interactive --account desi python ${LSSCODE}/LSS/scripts/pkrun.py --tracer ${tracers[${tp}]} --region NGC SGC --weight_type ${weight} --rebinning y --nran ${nran[${tp}]} --basedir ${fn} --outdir ${fn} --option elgzcatas  --calc_win y
            else
                echo "calculate without window clustering ${outputs}"
                echo srun -N 1 -n 64 -C cpu -t 04:00:00 --qos interactive --account desi python ${LSSCODE}/LSS/scripts/pkrun.py --tracer ${tracers[${tp}]} --region NGC SGC --weight_type ${weight} --rebinning y --nran ${nran[${tp}]} --basedir ${fn} --outdir ${fn} --option elgzcatas        
            fi
        fi
        # 3 types of catastrophics 2pt
        for catas in "${catas_types[@]}"; do
            outputs=${fn}/smu/xipoles_${tracers[${tp}]}_GCcomb_${zfin[${tp}]}_${weight}_lin10_njack0_nran18_split20_${catas}.txt
            if [ ! -f "${outputs}" ]; then 
                echo "calculate clustering ${outputs}"
                echo srun -N 1 -C gpu -t 04:00:00 --gpus 4 --qos interactive --account desi_g python ${LSSCODE}/LSS/scripts/xirunpc.py --gpu --tracer ${tracers[${tp}]} --region NGC SGC --corr_type smu --weight_type ${weight} --njack 0 --nran ${nran[${tp}]} --basedir ${fn}  --outdir ${fn} --catas_type ${catas}
            fi
            outputs=${fn}/pk/pkpoles_${tracers[${tp}]}_GCcomb_${zfin[${tp}]}_${weight}_lin_${catas}.npy
            if [ ! -f "${outputs}" ]; then 
                if [ ${MOCKNUM} == "0" ]; then
                    echo "calculate with window clustering ${outputs}"
                    echo srun -N 1 -n 64 -C cpu -t 04:00:00 --qos interactive --account desi python ${LSSCODE}/LSS/scripts/pkrun.py --tracer ${tracers[${tp}]} --region NGC SGC --weight_type ${weight} --rebinning y --nran ${nran[${tp}]} --basedir ${fn}  --outdir ${fn} --catas_type ${catas} --calc_win y
                else
                    echo "calculate without window clustering ${outputs}"
                    echo srun -N 1 -n 64 -C cpu -t 04:00:00 --qos interactive --account desi python ${LSSCODE}/LSS/scripts/pkrun.py --tracer ${tracers[${tp}]} --region NGC SGC --weight_type ${weight} --rebinning y --nran ${nran[${tp}]} --basedir ${fn}  --outdir ${fn} --catas_type ${catas}
                fi
            fi
        done 
    done
done
# TODO: remove the effect of the redshift uncertainties



