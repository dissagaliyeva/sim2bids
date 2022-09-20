# load necessary python modules
import numpy
import scipy
import os
# load TVB library
from tvb.simulator.lab import *
from tvb.basic.readers import FileReader


# set up the simulation

# select the SJHMR3D model as the local model and define its parameters
# for delta series choose 
oscilator = models.ReducedSetHindmarshRose(r=[0.006], a=[1.0], b=[3.0], c=[1.0], d=[5.0], s=[4.0], xo=[-1.6], K11=[0.5], K12=[0.1], K21=[0.15], sigma=[0.3], mu=[2.2], variables_of_interest=["xi","alpha"])
oscilator.configure()

# for alpha series uncomment the below code
# oscilator = models.ReducedSetHindmarshRose(r=[0.006], a=[1.0], b=[3.0], c=[1.0], d=[5.0], s=[4.0], xo=[-1.6], K11=[4.0], K12=[1.6], K21=[0.15], sigma=[0.4], mu=[2.2], variables_of_interest=["xi","alpha"])
# oscilator.configure()

# set up the structural connectivity
mypath=""  # insert the path to where all subjects connectivities are stored
subject="" # specify which subject to load

# load connectivity weights
reader = FileReader(file_path= mypath +'/' + subject +'/weights.txt')
w= reader.read_array(dtype=numpy.float64, skip_rows=0, use_cols=None, matlab_data_name=None)

# load region centers
reader = FileReader(file_path=mypath +'/' + subject +'/centres.txt')    
rl= reader.read_array( dtype="string", skip_rows=0, use_cols=(0,), matlab_data_name=None)
c= reader.read_array(dtype=numpy.float64, skip_rows=0, use_cols=(1, 2, 3), matlab_data_name=None)

# load connectivity tract lengths
reader = FileReader(file_path=mypath +'/' + subject +'/tract_lengths.txt')
tl= reader.read_array(dtype=numpy.float64, skip_rows=0, use_cols=None, matlab_data_name=None)

# confige the connectivity
white_matter = connectivity.Connectivity(region_labels=rl, weights=w, tract_lengths=tl, centres=c)        

# specify the coupling function
# here a linear scaling function was used
# csf --> global coupling scaling factor
# is one of the parameters explored in this study
# for delta series it was varied from 0.05 to 0.25 in steps of 0.01
# for alpha series it was varied from 0.025 to 0.04 in steps of 0.001
# in this simulation one one value is chosen, but loop across all values to reproduce the findings of the paper
csf = 0.05
white_matter_coupling = coupling.Linear(a=csf, b=[0.0])
white_matter_coupling.configure()

# specify a conduction speed to calculate time delays in the network 
# the 2nd parameter that was explored in this study
# for delta series it was varied from 20 to 100 in steps of 100
# for alpha series it was varied from 10 to 100 in steps of 10
# in this simulation one one value is chosen, but loop across all values to reproduce the findings of the paper
speed=100

# set up the integration scheme to solve the differential equations
# for delta series choose
heunint = integrators.HeunStochastic(dt=0.01220703125, noise=noise.Additive(nsig=array([1.0])))

# for alpha series uncomment the below code
heunint = integrators.HeunStochastic(dt=0.05, noise=noise.Additive(nsig=array([0.001])))


# specify what data to record from the simulation using tvb monitory
# choose subsampling of the neural signal
p=3.90625 #<-- 256Hz
momo = monitors.SubSample(period=p)

# choose to generate BOLD signal using a hemodynamic response function
hrffunction=equations.MixtureOfGammas()
pb=500
mama = monitors.Bold(period=pb, hrf_kernel=hrffunction)

# put both monitors together
what_to_watch = (momo, mama)

# configure the simulation
sim = simulator.Simulator(model=oscilator, connectivity=white_matter,
                          coupling=white_matter_coupling, conduction_speed=speed,
                          integrator=heunint, monitors=what_to_watch)

sim.configure()

# specify simulation length
# for delta series choose
sim_length = 180000

# for alpha series uncomment the below code
# sim_length = 300000

# for alpha series 22min simulation length use
sim_length = 1320000

# perform the simulation
subs_data = []
subs_time = []
bold_data = []
bold_time = []

for subs, bold in sim(simulation_length=sim_length):
    if not subs is None:
        subs_time.append(subs[0])
        subs_data.append(subs[1])
    
    if not bold is None:
        bold_time.append(bold[0])
        bold_data.append(bold[1])


# save the simulated time series
# declare a path where data should be saved
save_path=""
SUBS  = numpy.sum(numpy.array(subs_data),axis=3)
TSUBS = numpy.array(subs_time)
BOLD  = numpy.array(bold_data)
TBOLD = numpy.array(bold_time)
subsfile =save_path+'/'+subject+'csf_'+str(csf) +'_speed_' +str(speed)
scipy.io.savemat(subsfile, mdict={'subs_data': SUBS, 'subs_time': TSUBS ,'bold_data': BOLD, 'bold_time': TBOLD })


##################################
# load necessary python modules
import numpy as np
import scipy as scp
import scipy.io
import scipy.signal
import rpy2.robjects as rp

subject = '';  # specify subject to analyse
speed = 10     # specify which speed to analyse, this was done to split analysis across multiple cores


# specify where all empirical functional connectivities can be found
path_to_all_empirical_FCs 
# load the empirical FC as a numpy array, i.e. a 2D matrix with dimensions [68,68]
empFC      = scipy.io.loadmat(path_to_all_empirical_FCs)

# initialis arrays to store analysis data
all_simFC  = np.zeros((151,68,68)) # to store simulated FCs
sim_empFC  = np.zeros((151,1))     # to store the results of simulated to empirical FC comparison

avg_bimod = np.zeros((151,4))     # store statistics of bimodality tests for the average across all region signal, csf*[ p_dip, stat_Dip, p_dip_log, stat_Dip_log]
avg_freq  = np.zeros((151))       # store dominant frequency for the average across all region signal
reg_bimod = np.zeros((151,68,4))  # store statistics of bimodality tests for each region, csf*region*[p_dip, stat_Dip, p_dip_log, stat_Dip_log]
reg_freq  = np.zeros((151,68))    # store dominant frequency for each region

# global coupling scaling factor to loop across
CSF = np.arange(0.025,0.0401,0.0001)

# importing Hartigan's diptest for bimodality from R
# this package needs to be installed in the R distribution
d   = rp.r('diptest::dip.test')

# specify where simulations are stored
sim_results_path = ''
for csf in range(len(CSF)):
    
    #load simulated timeseries, subsampled neural signal and BOLD/fMRI
    subs = scp.io.loadmat(sim_results_path + subject +'_csf_'+str(CSF[csf])+'_speed_'+str(speed)+'.mat')['subs_data'].mean(axis=1)
    subs = subs[2*200:,:]
    bold = scp.io.loadmat(sim_results_path + subject +'_csf_'+str(CSF[csf])+'_speed_'+str(speed)+'.mat')['Bold_data']
    bold = np.squeeze(bold[40:,:,:,:].mean(axis=(1,3))).T
    
    # calculate simulated to empirical FC fit
    all_simFC[csf,:,:] = np.corrcoef(bold)
    
    sim_empFC[csf] = np.corrcoef(all_simFC[csf,:,:].flatten(),empFC.flatten())[0,1]
    
    # calculate statistics for average signal
    f, t, Sxx  = scp.signal.spectrogram(subs.mean(axis=1), fs=200, window=('tukey', 0.25), nperseg=128, noverlap=110, nfft=4*200)
    mean_power = np.mean(Sxx, axis=1)
    # dominant frquency
    avg_freq[csf]   = f[np.argmax(mean_power)]

    # bimodality
    dip = d(rp.FloatVector((Sxx[np.argmax(mean_power),:])))
    avg_bimod[csf,0] = dip[1][0]
    avg_bimod[csf,1] = dip[0][0]
    
    # now for log(power)
    dip = d(rp.FloatVector((np.log(Sxx[np.argmax(mean_power),:]))))
    avg_bimod[csf,2] = dip[1][0]
    avg_bimod[csf,3] = dip[0][0]
    
    
    # calculate statistis for each region
    for i in range(68):
        # dominant frequency
        f, t, Sxx = scp.signal.spectrogram(subs[:,i], fs=200, window=('tukey', 0.25), nperseg=128, noverlap=110, nfft=4*200)
        mean_power = np.mean(Sxx, axis=1)
        reg_freq[csf,i]   = f[np.argmax(mean_power)]

        # bimdality test                       
        dip = d(rp.FloatVector((Sxx[np.argmax(mean_power),:])))
        reg_bimod[csf,i,0] = dip[1][0]
        reg_bimod[csf,i,1] = dip[0][0]
        
        #now for log(power)
        dip = d(rp.FloatVector((np.log(Sxx[np.argmax(mean_power),:]))))
        reg_bimod[csf,i,2] = dip[1][0]
        reg_bimod[csf,i,3] = dip[0][0]


#save results, specify a path here
file = save_path+subject+"_speed_"+str(speed)+".mat"
scipy.io.savemat(file,mdict={'all_simFC': all_simFC, 'sim_empFC':sim_empFC, 'avg_bimod':avg_bimod, 
                             'avg_freq': avg_freq, 'reg_bimod': reg_bimod, 'reg_freq ':reg_freq})

#############################

# load necessary python modules
import scipy.io as sio
import numpy as np
import rpy2.robjects as rp
import rpy2.robjects.numpy2ri
rpy2.robjects.numpy2ri.activate()

# define a function to calculate FCD
def FCD(BOLD, window_length, overlap):
    """
    BOLD singal   ....[regions * samples]
    window length ....[samples]
    overlap       ....[samples] 

    output: 
    FCD           ....[number_windows * number_windows]
    """
    import numpy as np
    n_regions = BOLD.shape[0]
    window_steps_size = window_length - overlap;
    n_windows = int(np.round((BOLD.shape[1] - window_length) / window_steps_size + 1))

    #compute FC for each window
    FC_t = np.zeros((n_regions,n_regions,n_windows))
    for i in range(n_windows):
        FC_t[:,:,i] = np.corrcoef(BOLD[:,window_steps_size*i:window_length+window_steps_size*i])
    
    
    # transform FC matrix into vector by just taking the upper triangle
    a,b =np.triu_indices(n_regions,1)
    tFC = FC_t[a,b,:].T
    
    
    # compute FCD, correlate the FCs with each other
    FCD = np.corrcoef(tFC);
    
    return FCD, FC_t

# calculate all empirical FCDs
subj_list = ['']          # specify a list of subject IDs here
path_to_empirical_fmri = ""  # path to find empirical fmri data
all_FCDs = np.zeros((len(subj_list),64,64)) # initialise array to store FCDs

# parameters for the FCD
window_length = 30; #[samples]
overlap       = 20; #[samples] 
for i in range(len(subj_list)):    
    #load empirical BOLD data from matlab format
    BOLD = sio.loadmat(path_to_empirical_fmri + '/' + subj_list[i] + '.mat')    
    #compute empirical FCD
    
    all_FCDs[i,:,:], _      = FCD(BOLD,window_length,overlap)
    #print(i)

# only 4 subjects were simulated with 22 min
# calculate simulated FCDs for each global coupling scaling factor
CSF = np.arange(0.025,0.0401,0.0001)
window_length = 30; #[samples]
overlap       = 20; #[samples]
all_simFCDs = np.zeros((4,151,63,63))
path_to_22min_simulation = ""
for i in range(len(subj_list)):
    for n in range(len(CSF)):
        mat = sio.loadmat(path_to_22min_simulation+subj_list[i]+"/"
                          +subj_list[ind[i]]+"_"+str(np.round(CSF[n],4))+".mat",
                         variable_names="Bold_data")
        BOLD = np.squeeze(mat['Bold_data'])
        BOLD = BOLD[40::4,:].T # cut out first 20s due to gradient, downsample to 0.5 Hz
        
        #compute sim FCD
        all_simFCDs[i,n,:,:], _      = FCD(BOLD,window_length,overlap)

# compare FCDs using the Kolmogorov-Smirnof distance measure
# import test from R
ks_dist = rp.r('ks.test')
all_KS_dist = np.zeros((4,151))
a,b = np.triu_indices(63,1)
for n in range(4):
    for i in range(151):
        all_KS_dist[n,i] = ks_dist(all_simFCDs[i,a,b],all_FCDs[i,a,b])[0][0]

# save results 
path_to_save = "" # specify where to save results
sio.savemat(path_to_save+"/FCD_KS_distance.mat",mdict={"all_KS_dist":all_KS_dist})


