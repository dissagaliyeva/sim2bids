# SIM2BIDS: convert computational data to BIDS standard

---

This app is created to convert computational data to BIDS standard as proposed by [Michael Schirner and Petra Ritter](https://docs.google.com/document/d/1NT1ERdL41oz3NibIFRyVQ2iR8xH-dKY-lRCB4eyVeRo/edit?usp=sharing).
The specification proposes a data structure schema for neural network computer models that aims to be generically applicable to all kinds of neural network simulation software, mathematical models, computational models, and data models, but with a focus on dynamic circuit models of brain activity. Importantly, they not only propose suggestions for a BIDS schema for computer models, but they also propose extensions to the entire BIDS standard that solve several other problems.

### Installation

Simply run the following command to get the app up and running:

```
pip install sim2bids
```

Alternatively, either fork or obtain the latest sim2bids version by running the following:

```
git clone https://github.com/dissagaliyeva/sim2bids

cd sim2bids

python setup.py install
```

Then, open up your notebook and import the following packages:

```
import param

import io
import panel as pn
import numpy as np
import pandas as pd

import sim2bids
from sim2bids.sim2bids import MainArea

import warnings

warnings.filterwarnings('ignore')
pn.extension('tabulator', 'ace', 'jsoneditor', 'ipywidgets', sizing_mode='stretch_width', notifications=True)
```

There are two options to proceed:

1. Run the app locally (yields the best user experience) by calling `pn.serve(MainArea().view())`. This will take you to 
a localhost page where you'll see the app. 

2. Run the app inline (might have small differences in layout) by calling `MainArea().view().servable()`. 

### Important

Since there is a huge number of descriptions, parameters, and other variables, the app gives you the right to provide additional description.
By default, all the parameters are linked to [TheVirtualBrain]() 


### Resources

We want to ensure you have the best user experience. Therefore, on top of documentation page, we have included a presentation
that covers the main functionality; it also includes a step-by-step image/video walk-through with different datasets. [The link is right here](https://docs.google.com/presentation/d/12sUkOP7iv3CEn1pecu3ABiBBhPIFromMwfJXmnjbebQ/edit?usp=sharing).
