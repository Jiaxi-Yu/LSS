import numpy as np
np.random.seed(20241028)
import random
from scipy.special import erfinv

c = 299792 # speed of light in km/s

# generate dv that represent catastrophics 
def dv_catas_exp(uni, lnG_param=None, dvcatas=None, dvcatasmax=None):
    ## implement lognormal distribution with inverse transform sampling      
    lnG = lnG_param[0]-np.exp((erfinv(1-lnG_param[1]*uni)*lnG_param[2]+lnG_param[3])/lnG_param[4])
    ## remove the catastrophics dv that is too small/large or is infinite
    rest      = (lnG<np.log10(dvcatas))|(lnG>np.log10(dvcatasmax))|(~np.isfinite(lnG))
    while np.sum(rest)>0:
        lnG[rest] = inv_trans(np.random.rand(np.sum(rest))) 
        rest  = (lnG<np.log10(dvcatas))|(lnG>np.log10(dvcatasmax))|(~np.isfinite(lnG))            
    return lnG

# implement catastrophics
def catas_mock(dd, survey='Y1', tracer='ELG',catas_type='realistic'):
    # initialise the columns
    dd[f'Z_{catas_type}']= dd['Z'].copy()

    if catas_type == 'slitless':
        frac_tot  = 5
        survey    = 'Y1'
        tracer    = 'ELG'

    # implement catastrophics dv
    if survey == 'Y1':
        if tracer == 'ELG':
            lnG_param = [3321/500,200/99,243*np.sqrt(2),657,1000]
            ## implement realistic catastrophics measured from repeated observations
            if catas_type == 'realistic':
                ### ELG Y1 has lnG distribution and z=1.32 catastrophics
                dvcatas   = 1000
                dvcatasmax= 10**5.65
                frac_tot  = 0.26
                frac_nores= 0.751
                Nreal     = int(len(dd)*frac_tot/100)
                Nrealnores= int(Nreal*frac_nores) if int(Nreal*frac_nores)%2==0 else int(Nreal*frac_nores)-1
                ### frac_tot% of catastrophics rate
                inds      = np.array(random.sample(range(0, len(dd)), Nreal))
                random.shuffle(inds) # we need this shuffling because AbacusSummit "Z" was sorted
                
                ### frac_nores*100% ordinary zfailures due to various reasons
                exponent  = dv_catas_exp(np.random.rand(int(Nrealnores/2)), lnG_param=lnG_param, dvcatas=dvcatas, dvcatasmax=dvcatasmax)
                dv        = np.append(10**exponent,-10**exponent)
                random.shuffle(dv)
                dd[f'Z_{catas_type}'][inds[:Nrealnores]] += dv/c*(1+dd['Z'][inds[:Nrealnores]])
                ## (1-frac_nores)*100% extra zfailures due to z=1.32 sky residuals
                dd[f'Z_{catas_type}'][inds[Nrealnores:]]  = np.random.normal(1.32,0.006, size=Nreal-Nrealnores)
        else:
            raise ValueError("Catastrophics not available for survey='Y1' but should be available for survey='Y3' ")
    elif survey == 'Y3':
        raise ValueError("survey='Y3' not ready")        
        if tracer == 'ELG':
            raise ValueError("survey='Y3' not ready")        
        elif tracer == 'LRG':
            raise ValueError("survey='Y3' not ready")                
        elif tracer == 'QSO':
            raise ValueError("survey='Y3' not ready")        
        elif tracer == 'BGS':
            raise ValueError("survey='Y3' not ready")  
    else:
        raise ValueError("'survey' should be Y1, Y3")  

    # implement lognormal-profile failures
    ## hypothetical 1% catatrophics
    if catas_type == 'failures':
        frac_tot  = 1   
    
    ## implement the random failures
    Nfail     = int(len(dd)*frac_tot/100) if int(len(dd)*frac_tot/100)%2==0 else int(len(dd)*frac_tot/100)+1
    inds      = random.sample(range(0, len(dd)), Nfail)
    exponent  = dv_catas_exp(np.random.rand(int(Nfail/2)), lnG_param=lnG_param, dvcatas=dvcatas, dvcatasmax=dvcatasmax)
    dv        = np.append(10**exponent,-10**exponent)
    random.shuffle(dv)
    dd[f'Z_{catas_type}'][inds] += dv/c*(1+dd['Z'][inds])    
    
    return dd
