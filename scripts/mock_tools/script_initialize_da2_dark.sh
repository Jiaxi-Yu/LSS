#!/bin/bash
#SBATCH --time=04:00:00
#SBATCH --qos=shared
##SBATCH --nodes=1
#SBATCH --cpus-per-task=32
#SBATCH --constraint=cpu
#SBATCH --array=10,15,18
#SBATCH --account=desi
#SBATCH --mem=200G
#SBATCH --ntasks=1

source /global/common/software/desi/desi_environment.sh main
#source /global/common/software/desi/users/adematti/cosmodesi_environment.sh main
PYTHONPATH=$PYTHONPATH:$HOME/LSS/py

srun python initialize_amtl_mocks_da2.py $DESI_ROOT/survey/catalogs/DA2/mocks/SecondGenMocks/AbacusSummit_v4_1/forFA$SLURM_ARRAY_TASK_ID.fits $DESI_ROOT/survey/catalogs/DA2/mocks/SecondGenMocks/AbacusSummit_v4_1/altmtl$SLURM_ARRAY_TASK_ID DARK
