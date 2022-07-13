import os, sys
import pandas as pd
import incf.preprocess.generate as gen
import incf.templates.templates as temp
import incf.preprocess.preprocess as prep


def save(subs: dict, output: str, center: bool = False):
    # check and create folders & return paths to them
    sub, net, spatial, ts = gen.create_sub_struct(output, subs)

    #
