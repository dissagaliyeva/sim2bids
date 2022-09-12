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
