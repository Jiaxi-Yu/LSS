from astropy.table import Table,join
import fitsio
import os,sys
import numpy as np

gal  = 'LRG'
source= '/dvs_ro/cfs/cdirs/desi/survey/catalogs'
output= os.environ['SCRATCH']

# match the M* by TARGETID
## read the stellar mass file
data = Table(fitsio.read("/global/cfs/projectdirs/desi/users/jiaxiyu/SHAM/SV3_stellar_mass/edav1/LRG_clustering.dat.fits"))

def matching(args):
    input, outdir, tracer, GC, dind, dtype = args  # Unpack the arguments from the tuple
    if os.path.exists(filename.format(outdir, tracer+'_low', GC, dind, dtype)):
        return
    else:
        clustering = Table(fitsio.read(filename.format(input, tracer, GC, dind, dtype)))
        tmp = join(clustering, data, keys='Z', join_type='left')  # ensure 'data' is defined
        
        # Check if every galaxy has a Mstellar measurement
        if isinstance(tmp['Mstellar'], np.ma.MaskedArray) and tmp['Mstellar'].mask.any():
            raise ValueError("Error: 'Mstellar' contains missing values. Exiting.")
        
        # Remove extra columns and rename the redshift column
        tmp.remove_columns(['CAP', 'TARGETID_2'])
        tmp.rename_column('TARGETID_1', 'TARGETID')

        # Split the M* files and save them to scratch
        sel = tmp['Mstellar'] > np.median(tmp['Mstellar'])
        tmp[sel].write(filename.format(outdir, tracer+'_high', GC, dind, dtype), overwrite=True)
        tmp[~sel].write(filename.format(outdir, tracer+'_low', GC, dind, dtype), overwrite=True)
        
        print('M*-split data saved')

# matching the clustering-Mstellar for data
filename='{}/edav1/sv3/LSScats/clustering/{}_{}{}_clustering.{}.fits'
matching(source,output,gal,'N','','dat')
matching(source,output,gal,'S','','dat')
# matching the clustering-Mstellar for randomes
tasks = [[source, output, gal, gc, f'_{find}', 'ran'] for gc in ["N", "S"] for find in range(18)]
from multiprocessing import Pool
with Pool() as pool:
    pool.map(matching, tasks)

# check how to generate n(z) and FKP again, do it
## Ashley et al. 2012 didn't do this
import LSS.common_tools as common    
dz = 0.02
zmin = 0.01
zmax = 1.61
P0 = 10000

for reg in ["N","S"]:
    fcr = filename.format(output,gal,reg,'_0','ran')
    fcd = filename.format(output,gal,reg,'','dat')
    fout= filename.format(output,gal,reg,'','')[:-17]+'_nz.txt'
    common.mknz(fcd,fcr,fout,bs=dz,zmin=zmin,zmax=zmax)
    common.addnbar(filename.format(output,gal,reg,'','')[:-17],bs=dz,zmin=zmin,zmax=zmax,P0=P0)


# bash xiSV3edav1_split.sh
