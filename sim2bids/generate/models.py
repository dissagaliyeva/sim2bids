import os
import shutil
import numpy as np
import lems.api as lems
from sim2bids.templates import model_params
from sim2bids.generate import structure
from sim2bids.app import app


class Model:
    def __init__(self, model_name, rhythms=None, **kwargs):
        self.model_name = model_name
        self.possible_params = kwargs
        self.params = self.get_params()

        # pylems model parameters
        self.id = 1

        # check output structure and create folders if necessary
        structure.check_folders(app.OUTPUT)

        self.set_params()

    def get_params(self):
        if self.model_name == 'reduced_wong_wang':
            return model_params.reduced_wong_wang
        elif self.model_name == 'hindmarsh_rose':
            return model_params.hindmarsh_rose
        elif self.model_name == 'generic2doscillator':
            return model_params.g2dos

    def set_params(self):
        for k, v in self.possible_params.items():
            if not isinstance(v, float) and self.params.get(k, None) is not None:
                self.save_params(k, v)

    def save_params(self, k, v):
        # save equations

        # ==================================================================
        # NOTE: IF YOU'RE USING A LOCAL VERSION FORKED/DOWNLOADED FROM
        # GITHUB, UNCOMMENT THE LINE BELOW AND COMMENT OUT THE FILE LOCATION
        # THIS WILL ALLOW YOU READING THE DEFAULT XML MODELS
        # ==================================================================

        # COMMENT OUT THESE LINES OF CODE IF YOU'RE USING A LOCAL VERSION OF THE APP
        xml = os.path.join(f'../sim2bids/models/{self.model_name}.xml')

        # UNCOMMENT THESE LINES OF CODE IF YOU'RE USING LOCAL VERSION OF THE APP
        # here = os.path.dirname(os.path.abspath(__file__))
        # xml = os.path.join(here, 'models', self.model_name + '.xml')

        # copy the default equations xml file
        shutil.copy(xml, os.path.join(app.OUTPUT, 'eq', f'desc-{app.DESC}_eq.xml'))

        path = os.path.join(app.OUTPUT, 'param')

    def add_components(self, value):
        # instantiate a LEMS model
        model = lems.Model()

        # supply values
        model.add(lems.Component(id_=self.id, type_=self.comp_type, **self.model))

        # increase the id value
        self.id += 1


def save_json(path, content):
    with open(path, 'w') as f:
        json.dump(content, path)