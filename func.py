import numpy as np
import pandas as pd
import time
from datetime import datetime
from tkinter import Tk     
from tkinter.filedialog import askopenfilename


##Import partial parameters
Tpp=4
synccount=0
dt=0.2
##plaing with tags
now = datetime.now()
#creating dictionary for the group
tags={'MeasDesc_GlobalResolution':0.6,
      "MeasDesc_AcquisitionTime":200,
      "CreatorSW_Name":"Dayne",
      "HW_Type":"Manual scripting",
      "CreatorSW_Version":"v.alpha",
      "record_type":"rtPicoHarpT3",
      "MeasDesc_Resolution":50e-3,
      "TTResult_SyncRate":80e6
    }
#####Read and extract detector id,timetag and sst


Tk().withdraw() 
fileloc = askopenfilename() 

Start=time.time()
with open(fileloc, 'rb') as infile:
    a = np.fromfile(infile, dtype=np.uint32)
#detectors
ind=np.zeros((len(a)),dtype="uint8")

#nanoseconds
sstime=np.zeros((len(a)),dtype="uint16")

#timestamps
timetag=np.zeros((len(a)))                                                                                                                                                                                                 




#encoding the data with 16bit coding 
nsync= a & 65535

temp= a >> 28
# to reach the channel information ,the upper 4 bits
chan= temp & 15
#(chan= (a^2/28) & 15)more efficient but not 'safe'

#to reach the channel information ,the upper 16 bits
temp= a >> 16
sst= temp & 4095


''''
for i in range(len(a)):
    #when the channel is the acceptor, and there is the naotime is 0

    if chan[i]==15 & nsync[i]+sst[i]== 0:
        synccount=synccount+1 #number of photon
        timetag[i]=0 #don't count 
        sstime[i]=sst[i] #nanotime
        ind[i]=chan[i] #tell the channel id, detectors or not

    #when the channel is the acceptor,and there is the nanotime is not 0
    elif chan[i]==15 & sst[i]!= 0 :
        ind[i]=15-sst[i] #either 11 (15-3) or 13 (15-2) since special marker 1 is reserved for stage
        sstime[i]=0 #nanotime
        timetag[i]=(synccount*65536 + (nsync[i]))*Tpp
    
    #after all the special case
    else:
        ind[i]=chan[i]
        sstime[i]=sst[i]
        timetag[i]=(synccount*65536 + (nsync[i]))*Tpp +(sst[i])*dt;
        '''
for i in range(len(a)):
    ind[i]=chan[i]
    sstime[i]=sst[i]
    timetag[i]=(synccount*65536 + (nsync[i]))*Tpp +(sst[i])*dt;



Finish=time.time()-Start
print(Finish)






#####Conversion to HDF5

# Get the metadata
acquisition_duration = tags['MeasDesc_AcquisitionTime'] * 1e-3


creation_time = now.strftime("%m/%d/%Y, %H:%M:%S")
#print(creation_time)


hw_type = tags['HW_Type']
#if isinstance(hw_type, list):
    #hw_type = hw_type[0]
meta = {'timestamps_unit': tags['MeasDesc_GlobalResolution'], 
        'acquisition_duration': acquisition_duration,
        'software': tags['CreatorSW_Name'],
        'software_version': tags['CreatorSW_Version'],
        'creation_time': creation_time,
        'hardware_name': hw_type,
        'record_type': tags['record_type']}#,'tags': _convert_multi_tags(tags)
#add  this part only if you are worrkning with T3 file format
meta['nanotimes_unit'] = tags['MeasDesc_Resolution']
meta['laser_repetition_rate'] = tags['TTResult_SyncRate']


#####Last step before HDF5
###crutch
metadata=meta
filename=fileloc
timestamps=timetag
detectors=ind
nanotimes=sstime
donor=0
acceptor=1
alex_period_donor=(150, 1500)
alex_period_acceptor=(1540, 3050)
excitation_wavelengths=(523e-9, 628e-9)
detection_wavelengths=(580e-9, 680e-9)
#####

software = metadata.pop('software')
software_version = metadata.pop('software_version')
laser_repetition_rate = float(metadata.pop('laser_repetition_rate'))
acquisition_duration = float(metadata.pop('acquisition_duration'))
timestamps_unit = float(metadata.pop('timestamps_unit'))
tcspc_unit = float(metadata.pop('nanotimes_unit'))
tcspc_num_bins = 4096
tcspc_range = tcspc_num_bins * tcspc_unit

# Creation time from the file header

creation_time = metadata.pop('creation_time')

provenance = dict(
    filename=filename,
    creation_time=creation_time,
    software=software,
    software_version=software_version,
)

photon_data = dict(
    timestamps=timestamps,
    timestamps_specs=dict(timestamps_unit=timestamps_unit),
    detectors=detectors,
    nanotimes=nanotimes,

    nanotimes_specs=dict(
        tcspc_unit=tcspc_unit,
        tcspc_range=tcspc_range,
        tcspc_num_bins=tcspc_num_bins),

    measurement_specs=dict(
        measurement_type='smFRET-nsALEX',
        laser_repetition_rate=laser_repetition_rate,
        alex_excitation_period1=alex_period_donor,
        alex_excitation_period2=alex_period_acceptor,
        detectors_specs=dict(spectral_ch1=np.atleast_1d(donor),
                                spectral_ch2=np.atleast_1d(acceptor))),
)

setup = dict(
    num_pixels=4,
    num_spots=1,
    num_spectral_ch=2,
    num_polarization_ch=1,
    num_split_ch=1,
    modulated_excitation=True,
    lifetime=True,
    excitation_wavelengths=excitation_wavelengths,
    excitation_cw=[False, False],
    detection_wavelengths=detection_wavelengths,
    excitation_alternated=[False, False])

data = dict(
    _filename=filename,
    acquisition_duration=acquisition_duration,
    photon_data=photon_data,
    setup=setup,
    provenance=provenance)
