import os, sys
import pandas as pd
import incf.preprocess.generate as gen
import incf.templates.templates as temp
import incf.preprocess.preprocess as prep


def save(path, subs):
    # check and create folders & return paths to them
    sub, net, spatial, ts = gen.create_sub_struct(path, subs)

    #
