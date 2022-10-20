import os
import json
import shutil

import lems.api as lems
from sim2bids.templates import model_params
from sim2bids.generate import structure
from sim2bids.app import app
from sim2bids.convert import convert
from sim2bids.templates import templates


MODELS = ['reduced_wong_wang', 'hindmarsh_rose', 'generic2doscillator']
RHYTHMS = ['alpha', 'beta', 'delta', 'gamma', 'theta', None]


def set_params(model_name, conversion_name='default', rhythm=None, **kwargs):
    # set the default name for the conversion
    app.DESC = conversion_name

    join = lambda x: ', '.join(x)

    # verify model names and rhythms
    assert model_name in MODELS, f'Please select one of the accepted models: {join(MODELS)}'
    assert rhythm in RHYTHMS, f'Please select one of the accepted rhythms: {join(RHYTHMS)}'

    # check output structure and create folders if necessary
    structure.check_folders(app.OUTPUT)

    # instantiate a model class
    model = Model(model_name, rhythm, **kwargs)

    # set new parameters and save them in 'param' and 'eq' folders
    model.set_params()


class Model:
    def __init__(self, model_name, rhythms, **kwargs):
        self.model_name = model_name
        self.params = self.get_params()
        self.rhythms = rhythms
        self.possible_params = kwargs

        # pylems model parameters
        self.id = 1

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

        if not os.path.exists(path):
            shutil.copy(xml, path)
            convert.to_json(path.replace('xml', 'json'), shape=None,
                            desc=templates.file_desc['eq'].format(self.model_name.upper()), key='eq')

        # save params
        # TODO: ADD DIFFERENT RHYTHMS TRAVERSAL

        # iterate over values
        for value in v:
            path = os.path.join(app.OUTPUT, 'param', f'desc-{app.DESC}-{k}{str(format(value, ".4f"))}.xml')
            save_json(path, self.get_model(k, float(value)), use_json=False)
            convert.to_json(path.replace('xml', 'json'), shape=None,
                            desc=templates.file_desc['param'].format(self.model_name.upper()), key='param')

    def get_model(self, k, v):
        # instantiate a LEMS model
        model = lems.Model()

        if k == 'G':
            # create a nested G constant inside global parameters ComponentType
            ct = lems.ComponentType(name='global_parameters')
            ct.add(lems.Constant(name=k, value=v))

            # append the structure to the model
            model.add(ct)

        # increase the id value
        self.id += 1

        return model


def save_json(path, model=None, use_json=True):
    if model:
        model.export_to_file(path)

    if use_json:
        with open(path, 'w') as f:
            json.dump(model, f)


