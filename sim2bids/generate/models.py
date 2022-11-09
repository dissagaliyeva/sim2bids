import os
import json
import re
import shutil

import lems.api as lems
import numpy as np

from sim2bids.templates import model_params
from sim2bids.generate import structure
from sim2bids.app import app
from sim2bids.convert import convert
from sim2bids.templates import templates
from sim2bids.generate import utils
import panel as pn
from sim2bids.app import app, utils as app_utils


MODELS = ['reduced_wong_wang', 'hindmarsh_rose', 'generic2doscillator']
RHYTHMS = ['alpha', 'beta', 'delta', 'gamma', 'theta', None]


def set_params(conversion_name='default', rhythm=None, **kwargs):
    # set the default name for the conversion
    app.DESC, model_name = conversion_name, None

    join = lambda x: ', '.join(x)

    # verify model names and rhythms
    if app.MODEL_NAME == 'ReducedWongWang':
        model_name = MODELS[0]
    elif app.MODEL_NAME == 'HindmarshRose':
        model_name = MODELS[1]
    elif app.MODEL_NAME in ['Generic2dOscillator', 'G2DOS']:
        model_name = MODELS[2]

    assert model_name in MODELS, f'{model_name} doesn\'t match existing models. Please select one of the accepted models: {join(MODELS)}'
    #     assert rhythm in RHYTHMS, f'Please select one of the accepted rhythms: {join(RHYTHMS)}'

    # check output structure and create folders if necessary
    structure.check_folders(app.OUTPUT)

    if app.CODE is None or isinstance(app.CODE, list):
        # instantiate a model class
        model = NoCodeModel(model_name, rhythm, **kwargs)

        # set new parameters and save them in 'param' and 'eq' folders
        model.set_params()

    else:
        CreateModel(app.CODE, os.path.join(app.OUTPUT, 'param'), params=kwargs)


class NoCodeModel:
    def __init__(self, model_name, rhythm, **kwargs):
        self.model_name = model_name.lower()
        self.rhythm = rhythm
        self.params = self.get_params()
        self.possible_params = kwargs

        # model specific - do not change
        self.changed = False
        self.eq_saved = False
        self.eq_desc = 'default'
        self.param_desc = 'default'
        self.abbreviation = 'default'

        # ==================================================================
        # NOTE: IF YOU'RE USING A LOCAL VERSION FORKED/DOWNLOADED FROM
        # GITHUB, UNCOMMENT THE LINE BELOW AND COMMENT OUT THE FILE LOCATION
        # THIS WILL ALLOW YOU READING THE DEFAULT XML MODELS
        # ==================================================================

        # COMMENT OUT THESE LINES OF CODE IF YOU'RE USING A LOCAL VERSION OF THE APP
        # self.xml_path = os.path.join(f'../sim2bids/models/{self.model_name}.xml')

        # UNCOMMENT THESE LINES OF CODE IF YOU'RE USING LOCAL VERSION OF THE APP
        here = os.path.dirname(os.path.abspath(__file__))
        self.xml_path = os.path.join(here, 'models', self.model_name + '.xml')

        self.get_params()

    def get_params(self):
        if self.model_name in ['reduced_wong_wang', 'reducedwongwang', 'rww']:
            self.model_name = 'reduced_wong_wang'
            self.eq_desc = utils.TVB_MODELS['RWW']['desc']

            if self.rhythm:
                self.param_desc = templates.file_desc['param'].format(self.rhythm, 'ReducedWongWang')
            else:
                self.param_desc = templates.file_desc['param'].format('global', 'ReducedWongWang')

            self.abbreviation = 'RWW'
            return model_params.reduced_wong_wang

        elif self.model_name in ['hindmarsh_rose', 'sjhm3d', 'hindmarshrose']:
            self.model_name = 'hindmarsh_rose'
            self.eq_desc = utils.TVB_MODELS['SJHM3D']['desc']

            if self.rhythm:
                self.param_desc = templates.file_desc['param'].format(self.rhythm, 'HindmarshRose')
            else:
                self.param_desc = templates.file_desc['param'].format('global', 'HindmarshRose')

            self.abbreviation = 'SJHM3D'
            return model_params.hindmarsh_rose

        elif self.model_name in ['generic2doscillator', 'gs2dos', 'oscillator']:
            self.model_name = 'generic2doscillator'
            self.eq_desc = utils.TVB_MODELS['G2DOS']['desc']

            if self.rhythm:
                self.param_desc = templates.file_desc['param'].format(self.rhythm, 'Generic2dOscillator')
            else:
                self.param_desc = templates.file_desc['param'].format('global', 'Generic2dOscillator')

            self.abbreviation = 'G2DOS'
            return model_params.g2dos

    def set_params(self):
        self.change_params()

        if self.possible_params:
            for k, v in self.possible_params.items():
                if not isinstance(v, float):
                    self.save_params(k, v)

        if self.changed:
            paths = [os.path.join(app.OUTPUT, 'param', f'{self.rhythm}_param.xml'),
                     os.path.join(app.OUTPUT, 'eq', f'eq.xml')]

            # remove existing files
            for idx in range(len(paths)):
                if os.path.exists(paths[idx]):
                    os.remove(paths[idx])

        # save equations
        self.save_eq()

        # save params
        self.save_model_params()

    def save_eq(self):
        # copy the default equations xml file
        if self.rhythm:
            path = os.path.join(app.OUTPUT, 'eq', f'eq.xml')
        else:
            path = os.path.join(app.OUTPUT, 'eq', f'eq.xml')

        if not os.path.exists(path):
            shutil.copy(self.xml_path, path)
            convert.to_json(path.replace('xml', 'json'), shape=None, desc=self.eq_desc, key='eq')

    def save_model_params(self):
        model = lems.Model()

        if self.rhythm:
            model.add(lems.Component(id_=f'{self.rhythm}_times', type_=self.abbreviation, **self.params))
            path = os.path.join(app.OUTPUT, 'param', f'{self.rhythm}_param.xml')
        else:
            path = os.path.join(app.OUTPUT, 'param', f'param.xml')
            model.add(lems.Component(id_=app.DESC, type_=self.abbreviation, **self.params))

        if not os.path.exists(path):
            model.export_to_file(path)
            convert.to_json(path.replace('xml', 'json'), shape=None, desc=self.param_desc, key='param')

    def change_params(self):
        for k, v in self.possible_params.items():
            if isinstance(v, float):
                self.changed = True
                self.params[k] = v

    def save_params(self, k, v):
        # iterate over values
        if (isinstance(v, list) or isinstance(v, np.ndarray)) and k != 'variables_of_interest':
            self.save_list_params(k, v)

    def save_list_params(self, k, v):
        for value in v:
            if self.rhythm:
                path = os.path.join(app.OUTPUT, 'param',
                                    f'{self.rhythm}-{k}{str(format(value, ".3f"))}_param.xml')
            else:
                if isinstance(value, np.float) or isinstance(value, float):
                    path = os.path.join(app.OUTPUT, 'param', f'{k}{format(value, ".3f")}_param.xml')
                else:
                    path = os.path.join(app.OUTPUT, 'param', f'{k}{format(value, ".3f")}_param.xml')

            save_json(path, self.get_model(k, v), use_json=False)
            convert.to_json(path.replace('xml', 'json'), shape=None, desc=self.param_desc, key='param')

    def get_model(self, k, v):
        # instantiate a LEMS model
        model = lems.Model()

        if k == 'G':
            # create a nested G constant inside global parameters ComponentType
            ct = lems.ComponentType(name='global_parameters')
            ct.add(lems.Constant(name=k, value=str(v)))

            # append the structure to the model
            model.add(ct)

        return model


def save_json(path, model=None, use_json=True):
    if model:
        model.export_to_file(path)

    if use_json:
        with open(path, 'w') as f:
            json.dump(model, f)


# open file and prepare the dataset
def open_file(path: str) -> list:
    """

    :param path:
    :return:
    """

    # verify the path exists
    assert os.path.exists(path), f'File at location {path} does not exist'
    contents = []

    # open file
    with open(path) as file:
        for line in file.readlines():
            contents.append(line.strip('\n') + '\n')

    return ''.join(contents)


class CreateModel:
    def __init__(self, input_path: [str, dict], output_folder, rhythm=None, params=None):
        self.temp_params = None
        self.input_path = input_path
        self.output_folder = output_folder
        self.rhythm = rhythm
        self.init_params = params

        # model specific information
        self.model_name = None
        self.comp_type = None
        self.params = None

        # read parameters from python code
        if isinstance(input_path, str):
            self.get_params()

    def get_params(self):
        """
        Read parameters from source code. Check if multiple rhythms are present.
        If true, send the notification to specify parameters for each rhythm.
        For example:

                from sim2bids.app import app
                app.MODEL_PARAMS = dict(alpha=dict(r=0.006, a=1., b=3., c=1., d=5., s=4.),
                                        delta=dict(r=0.006, a=1., b=2., c=1., d=4.)))

        Otherwise, read the parameters from code and supplement default model's values.
        """

        # check if multiple rhythms are present
        self.content = open_file(self.input_path)
        self.rhythms = list(set(re.findall(r'(alpha|beta|delta|gamma|theta)', self.content)))

        # if there are multiple rhythms, raise a notification and error asking to
        # supplement values manually
        if len(self.rhythms) > 1 and app.MODEL_PARAMS is None:
            pn.state.notifications.error('Code contains multiple rhythms. Please specify values for each')
            return

        app_utils.infer_model()

        if app.MODEL_NAME == 'HindmarshRose':
            self.model_name = 'hindmarsh_rose'
        elif app.MODEL_NAME == 'ReducedWongWang':
            self.model_name = 'reduced_wong_wang'
        else:
            self.model_name = 'generic2doscillator'

        if len(self.rhythms) > 1 and app.MODEL_PARAMS:
            for k, v in app.MODEL_PARAMS.items():
                model = NoCodeModel(self.model_name, k, **v)
                model.set_params()

        elif len(self.rhythms) <= 1:
            self.get_model_params()

    def get_model_params(self):
        match = re.findall(r'(?:HindmarshRose|ReducedWongWang|Generic2dOscillator)[a-zA-Z0-9=()\]\\[\'\"\.\,\s\-\_]+', self.content)

        if len(match) > 0:
            self.temp_params = [x.strip(',') for x in re.findall(r'[a-zA-Z0-9]+\=[0-9\,\.\-\'\"\[\]]+', match[0])
                                if x.endswith('],')]
            if self.temp_params:

                self.params = {}

                # traverse over list of parameters
                for param in self.temp_params:
                    k = re.match(r'[a-zA-Z0-9]+', param)[0]
                    v = re.findall(r'[0-9\.]+', re.findall(r'\[[0-9\.\-]+', param)[0])[0]
                    self.params[k] = float(v)

                if self.rhythms:
                    model = NoCodeModel(self.model_name, rhythm=self.rhythms[0], **self.params)
                    model.set_params()
                else:
                    model = NoCodeModel(self.model_name, rhythm=None, **self.params)
                    model.set_params()

            else:
                if self.rhythms:
                    model = NoCodeModel(self.model_name, rhythm=self.rhythms[0])
                    model.set_params()
                else:
                    model = NoCodeModel(self.model_name, rhythm=None)
                    model.set_params()
