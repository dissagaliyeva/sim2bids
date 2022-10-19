import os
import json
import shutil
import numpy as np
import lems.api as lems
from sim2bids.templates import model_params
from sim2bids.generate import structure
from sim2bids.app import app
from sim2bids.convert import convert
from sim2bids.templates import templates


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
        path = os.path.join(app.OUTPUT, 'eq', f'desc-{app.DESC}_eq.xml')
        shutil.copy(xml, path)
        convert.to_json(path.replace('xml', 'json'), shape=None,
                        desc=templates.file_desc['eq'].format(self.model_name.upper()), key='eq')

        # save params
        # TODO: ADD DIFFERENT RHYTHMS TRAVERSAL

        # iterate over values
        for value in v:
            path = os.path.join(app.OUTPUT, 'param', f'desc-{app.DESC}-{k}{str(format(value, ".4f"))}.xml')
            save_json(path, self.add_components(dict(k=float(value))), use_json=False)
            convert.to_json(path.replace('xml', 'json'), shape=None,
                            desc=templates.file_desc['param'].format(self.model_name.upper()), key='param')

    def add_components(self, value):
        # instantiate a LEMS model
        model = lems.Model()

        # supply values
        model.add(lems.Component(id_=self.id, type_=self.model_name, **value))

        # increase the id value
        self.id += 1

        return model


def save_json(path, model=None, use_json=True):
    if model:
        model.export_to_file(path)

    with open(path, 'w') as f:
        if use_json:
            json.dump(model, f)

