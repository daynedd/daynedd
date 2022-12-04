import os
import numpy as np
import phconvert as phc
import matplotlib.pyplot as plt
import sys, os
from numba import jit, cuda

sys.path.append(os.path.join(sys.path[0],'functions'))
location=os.path.dirname(os.path.abspath(__file__))
print("Test started")
#import controlling_functions as control
import func as control

d=control.data
meta=control.metadata


detectors = d['photon_data']['detectors']
print("Detector    Counts")
print("--------   --------")

plt.figure()
q=phc.plotter.alternation_hist(d)

plt.savefig("alternation_hist.png")
for det, count in zip(*np.unique(detectors, return_counts=True)):
    print("%8d   %8d" % (det, count))

author = 'Dayne Dai'
author_affiliation = ' University of Toronto'
description = 'accurate test'
sample_name = 'something '
dye_names = 'cy3 and 5'
buffer_name = '50% sucrose solution'
# Remove some empty groups that may cause errors on saving
_ = meta.pop('dispcurve', None)
_ = meta.pop('imghdr', None)
d['user'] = {'picoquant': meta}
d['description']=description
phc.hdf5.save_photon_hdf5(d, overwrite=True)





