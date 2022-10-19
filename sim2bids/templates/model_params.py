"""
Model parameters based on The Virtual Brain (TVB)'s parameters. Details can be found here:
https://docs.thevirtualbrain.org/_modules/tvb/simulator/models

Currently supported models: ReducedWongWang, HindmarshRose, Generic2dOscillator

"""

# ReducedWongWang model
wong_wang = dict(a=270, b=108, d=0.154, gamma=0.000641, tau_s=100., w=0.9, J_N=0.2609,
                 I_o=0.3, G=2., sigma_noise=1.e-09, tau_rin=100)

# HindmarshRose model
hindmarsh_rose = dict(r=0.001, a=1., b=3., c=1., d=5., s=1., x_1=-1.6)

# Generic2dOscillator
g2dos = dict(tau=1.25, a=1.05, b=0.2, omega=1., upsilon=1., gamma=1., eta=1.)
