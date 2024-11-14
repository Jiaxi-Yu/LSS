import numpy as np
np.random.seed(20241028)
import random

c = 299792 # speed of light in km/s

# define the lognormal catastrophics with inverse transform sampling
def lognorm(uniform,lnG_param):
    from scipy.special import erfinv
    return lnG_param[0]-np.exp((erfinv(1-uniform/lnG_param[1])+lnG_param[2])/lnG_param[3])

# generate dv that represent catastrophics 
def dv_catas_exp(uni, lnG_param=None, dvcatas=None, dvcatasmax=None):
    ## implement lognormal distribution with inverse transform sampling      
    lnG = lognorm(uni,lnG_param)
    ## remove the catastrophics dv that is too small/large or is infinite
    rest      = (lnG<np.log10(dvcatas))|(lnG>np.log10(dvcatasmax))|(~np.isfinite(lnG))
    while np.sum(rest)>0:
        lnG[rest] = lognorm(np.random.rand(np.sum(rest)), lnG_param)
        rest  = (lnG<np.log10(dvcatas))|(lnG>np.log10(dvcatasmax))|(~np.isfinite(lnG))     
    return lnG

# implement catastrophics
def catas_mock(dd, survey='Y1', tracer='ELG',catas_type='realistic'):
    # initialise the columns
    dd[f'Z_{catas_type}']= dd['Z'].copy()

    if catas_type == 'slitless':
        ## hypothetical 5% catatrophics
        frac_tot  = 5
        survey    = 'Y1'
        tracer    = 'ELG'
    elif catas_type == 'failures':
        ## hypothetical 1% catatrophics
        frac_tot  = 1   
    # the threshold to be a catastrophics
    dvcatas   = 1000

    # implement catastrophics dv
    if survey == 'Y1':
        if tracer == 'ELG':
            lnG_param = [6.62128,0.495102,1.84552,2.86614]
            dvcatasmax= 10**5.65
            ## implement realistic catastrophics measured from repeated observations
            if catas_type == 'realistic':
                ### ELG Y1 has lnG distribution and z=1.32 catastrophics
                frac_tot  = 0.26 # the tocal catastrophics rate in percent
                frac_nores= 0.751 # the fraction of random failures in the catastropjics
        else:
            raise ValueError("Catastrophics not available for survey='Y1' but should be available for survey='Y3' ")
    elif survey == 'Y3':
        if tracer == 'ELG':
            lnG_param = [7.99976,0.490065,5.697480,4.66429]
            dvcatasmax= 10**5.625
            if catas_type == 'realistic':
                frac_tot  = 0.24 # the tocal catastrophics rate in percent
                frac_nores= 0.751 # the fraction of random failures in the catastropjics
        elif tracer == 'LRG':
            lnG_param = [5.70227,0.494945,0.00062810,1.23157]
            dvcatasmax= 10**5.625
            frac_tot  = 0.62
        elif tracer == 'QSO':
            raise ValueError("survey='Y3' not ready")        
        elif tracer == 'BGS':
            raise ValueError("survey='Y3' not ready")        
    else:
        raise ValueError("'survey' should be Y1, Y3")  
  
    if (tracer == 'ELG')&(catas_type == 'realistic'):
        ### ELG has lnG distribution and z=1.32 catastrophics
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
        ## implement the random failures
        Nfail     = int(len(dd)*frac_tot/100) if int(len(dd)*frac_tot/100)%2==0 else int(len(dd)*frac_tot/100)+1
        inds      = random.sample(range(0, len(dd)), Nfail)
        exponent  = dv_catas_exp(np.random.rand(int(Nfail/2)), lnG_param=lnG_param, dvcatas=dvcatas, dvcatasmax=dvcatasmax)
        dv        = np.append(10**exponent,-10**exponent)
        random.shuffle(dv)
        dd[f'Z_{catas_type}'][inds] += dv/c*(1+dd['Z'][inds])  
    return dd
