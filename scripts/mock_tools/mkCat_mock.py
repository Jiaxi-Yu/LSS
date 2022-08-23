#standard python
import sys
import os
import shutil
import unittest
from datetime import datetime
import json
import numpy as np
import fitsio
import glob
import argparse
from astropy.table import Table,join,unique,vstack
from matplotlib import pyplot as plt
from desitarget.io import read_targets_in_tiles
from desitarget.mtl import inflate_ledger
from desitarget import targetmask
from desitarget.internal import sharedmem
from desimodel.footprint import is_point_in_desi
from desitarget import targetmask

import LSS.main.cattools as ct
import LSS.common_tools as common
#import LSS.mkCat_singletile.fa4lsscat as fa
#from LSS.globals import main

if os.environ['NERSC_HOST'] == 'cori':
    scratch = 'CSCRATCH'
elif os.environ['NERSC_HOST'] == 'perlmutter':
    scratch = 'PSCRATCH'
else:
    print('NERSC_HOST is not cori or permutter but is '+os.environ['NERSC_HOST'])
    sys.exit('NERSC_HOST not known (code only works on NERSC), not proceeding') 


parser = argparse.ArgumentParser()
parser.add_argument("--tracer", help="tracer type to be selected")
parser.add_argument("--mockver", help="type of mock to use",default='ab_firstgen')
parser.add_argument("--mockmin", help="number for the realization",default=1,type=int)
parser.add_argument("--mockmax", help="number for the realization",default=2,type=int)
parser.add_argument("--base_output", help="base directory for output",default='/global/cfs/cdirs/desi/survey/catalogs/main/mocks/')
parser.add_argument("--survey", help="e.g., main (for all), DA02, any future DA",default='DA02')
parser.add_argument("--version", help="catalog version; use 'test' unless you know what you are doing!",default='test')
parser.add_argument("--combd", help="combine the data tiles together",default='n')
parser.add_argument("--combr", help="combine the random tiles together",default='n')
parser.add_argument("--combdr", help="combine the random tiles info together with the assignment info",default='n')
parser.add_argument("--fulld", help="make the 'full' data files ",default='n')
parser.add_argument("--fullr", help="make the random files associated with the full data files",default='n')
parser.add_argument("--add_veto", help="add veto column to the full files",default='n')
parser.add_argument("--apply_veto", help="apply vetos to the full files",default='n')
parser.add_argument("--clus", help="make the data/random clustering files; these are cut to a small subset of columns",default='n')
parser.add_argument("--nz", help="get n(z) for type and all subtypes",default='n')
parser.add_argument("--minr", help="minimum number for random files",default=1,type=int)
parser.add_argument("--maxr", help="maximum for random files, default is 1, but 40 are available (use parallel script for all)",default=2,type=int) 
parser.add_argument("--par", help="run different random number in parallel?",default='n')

parser.add_argument("--notqso",help="if y, do not include any qso targets",default='n')
parser.add_argument("--newspec",help="if y, merge in redshift info even if no new tiles",default='n')

args = parser.parse_args()
print(args)

rm = int(args.minr)
rx = int(args.maxr)
par = True
if args.par == 'n':
    par = False

notqso = ''
if args.notqso == 'y':
    notqso = 'notqso'

tracer = args.tracer
survey = args.survey

if tracer[:3] == 'BGS' or tracer == 'bright' or tracer == 'MWS_ANY':
    pr = 'BRIGHT'
    pdir = 'bright'
else:
    pr = 'DARK'
    pdir = 'dark'

pd = pdir

if args.mockver == 'ab_firstgen':
    mockdir = 'FirstGenMocks/AbacusSummit/'

maindir = args.base_output +mockdir+args.survey+'/'

tiles = fitsio.read( '/global/cfs/cdirs/desi/survey/catalogs/'+survey+'/LSS/tiles-'+pr+'.fits')

def docat(mocknum,rannum):

    lssdir = maindir+'mock'+str(mocknum)+'/'
    if not os.path.exists(lssdir):
        os.mkdir(lssdir)
        print('made '+lssdir)

    dirout = lssdir+'LSScats/'
    if not os.path.exists(dirout):
        os.mkdir(dirout)
        print('made '+dirout)


    if args.tracer == 'BGS_BRIGHT':
        bit = targetmask.bgs_mask[args.tracer]
        desitarg='BGS_TARGET'
    else:
        bit = targetmask.desi_mask[args.tracer]
        desitarg='DESI_TARGET'


    if args.combr == 'y' and mocknum == 1:
        fbadir = maindir+'random_fba'+str(rannum)
        outdir = fbadir
        tarf = fbadir+'/targs.fits'
        common.combtiles_pa_wdup(tiles,fbadir,outdir,tarf,addcols=['TARGETID','RA','DEC'],fba=True,tp=pdir)

    if args.combd == 'y' and rannum == 1:
        fbadir = maindir+'fba'+str(mocknum)
        outdir = fbadir
        tarf = fbadir+'/targs.fits'
        asn = common.combtiles_assign_wdup(tiles,fbadir,outdir,tarf,tp=pdir)
        #if using alt MTL that should have ZWARN_MTL, put that in here
        asn['ZWARN_MTL'] = np.copy(asn['ZWARN'])
        pa = common.combtiles_pa_wdup(tiles,fbadir,outdir,tarf,addcols=['TARGETID','RA','DEC'],fba=True,tp=pdir,ran='dat')

        pa['TILELOCID'] = 10000*pa['TILEID'] +pa['LOCATION']
        tj = join(pa,asn,keys=['TARGETID','LOCATION','TILEID'],join_type='left')
        outfs = lssdir+'datcomb_'+pdir+'_tarspecwdup_zdone.fits'
        tj.write(outfs,format='fits', overwrite=True)
        tc = ct.count_tiles_better('dat',pdir,specrel='',survey=args.survey,indir=lssdir) 
        outtc =  lssdir+'Alltiles_'+pdir+'_tilelocs.dat.fits'
        tc.write(outtc,format='fits', overwrite=True)
    
    if args.combdr == 'y':
        fbadir_data = maindir+'fba'+str(mocknum)
        fbadir_ran = maindir+'random_fba'+str(rannum)
        specf = Table(fitsio.read(fbadir_data+'/datcomb_'+pdir+'assignwdup.fits'))
        specf['TILELOCID'] = 10000*specf['TILEID'] +specf['LOCATION']
        specf.remove_columns(['TARGETID'])
        fgu = Table(fitsio.read(fbadir_ran+'/rancomb_'+pdir+'wdup.fits'))
        print(len(fgu))
        fgu = join(fgu,specf,keys=['LOCATION','TILEID'],join_type='left')
        print(len(fgu))
        print(fgu.dtype.names)
        fgu.sort('TARGETID')
        outf = lssdir+'/rancomb_'+str(rannum)+pdir+'wdupspec_zdone.fits'
        print(outf)
        fgu.write(outf,format='fits', overwrite=True)
        tc = ct.count_tiles_better('ran',pdir,rannum,specrel='',survey=args.survey,indir=lssdir)
        tc.write(lssdir+'/rancomb_'+str(rannum)+pdir+'_Alltilelocinfo.fits',format='fits', overwrite=True)

    specver = 'mock'    
        
    if args.fulld:
        imbits = []
        ftar = None
        dz = lssdir+'datcomb_'+pdir+'_tarspecwdup_zdone.fits'
        tlf = lssdir+'Alltiles_'+pdir+'_tilelocs.dat.fits'
        ct.mkfulldat(dz,imbits,ftar,args.tracer,bit,dirout+args.tracer+notqso+'_full_noveto.dat.fits',tlf,desitarg=desitarg,specver=specver,notqso=notqso)

    return True
        
    if mkfullr:
        maxp = 3400
        if type[:3] == 'LRG' or notqso == 'notqso':
            maxp = 3200
        if type[:3] == 'BGS':
            maxp = 2100

#         if specrel == 'everest':
#             #specf = Table.read('/global/cfs/cdirs/desi/spectro/redux/everest/zcatalog/ztile-main-'+pdir+'-cumulative.fits')
#             #wt = np.isin(specf['TILEID'],ta['TILEID']) #cut spec file to dark or bright time tiles
#             #specf = specf[wt]
#             fbcol = 'COADD_FIBERSTATUS'
#         if specrel == 'daily':
#             #specf = Table.read(ldirspec+'datcomb_'+pdir+'_specwdup_Alltiles.fits')
#             fbcol = 'FIBERSTATUS'

        outf = dirout+type+notqso+'_'+str(ii)+'_full_noveto.ran.fits'
        
        ct.mkfullran(gtl,lznp,ldirspec,ii,imbits,outf,type,pdir,notqso=notqso,maxp=maxp,min_tsnr2=tsnrcut,tlid_full=tlid_full,badfib=badfib)
        
    #logf.write('ran mkfullran\n')
    #print('ran mkfullran\n')
    if args.add_veto == 'y':
        fin = dirout+type+notqso+'_'+str(ii)+'_full_noveto.ran.fits'
        common.add_veto_col(fin,ran=True,tracer_mask=type[:3].lower(),rann=ii)


    if args.apply_veto == 'y':
        print('applying vetos')
        maxp = 3400
        if type[:3] == 'LRG' or notqso == 'notqso':
            maxp = 3200
        if type[:3] == 'BGS':
            maxp = 2100
        fin = dirout+type+notqso+'_'+str(ii)+'_full_noveto.ran.fits'
        fout = dirout+type+notqso+'_'+str(ii)+'_full.ran.fits'
        common.apply_veto(fin,fout,ebits=ebits,zmask=False,maxp=maxp)
        #print('random veto '+str(ii)+' done')



    if mkclusran:
#         tsnrcol = 'TSNR2_ELG'
#         tsnrcut = 0
#         if type[:3] == 'ELG':
#             #dchi2 = 0.9 #This is actually the OII cut criteria for ELGs
#             tsnrcut = 80
#         if type == 'LRG':
#             #dchi2 = 16  
#             tsnrcut = 80          
#         if type[:3] == 'BGS':
#             tsnrcol = 'TSNR2_BGS'
#             dchi2 = 40
#             tsnrcut = 1000

        ct.mkclusran(dirout+type+notqso+'_',ii,zmask=zma,tsnrcut=tsnrcut,tsnrcol=tsnrcol)
    print('done with random '+str(ii))
    return True
        #ct.mkclusran(dirout+type+'Alltiles_',ii,zmask=zma)
    #logf.write('ran mkclusran\n')
    #print('ran mkclusran\n')
    
if __name__ == '__main__':
    rx = args.maxr
    rm = args.minr
    mockmin = args.mockmin
    mockmax = args.mockmax
    if args.par == 'y':
        from multiprocessing import Pool
        from desitarget.internal import sharedmem
        
        N = rx-rm+1
        inds = []
        for i in range(rm,rx):
            inds.append(i)
        pool = sharedmem.MapReduce(np=N)
        with pool:
        
            def reduce( r):
                print('chunk done')
                return r
            pool.map(prep,inds,reduce=reduce)

        #p.map(doran,inds)
    else:
        for mn in range(mockmin,mockmax):
            for i in range(rm,rx):
                print('processing mock '+str(mn)+' and random '+str(i))
                docat(mn,i)