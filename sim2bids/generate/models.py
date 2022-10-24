import os
import json
import re
import shutil

import lems.api as lems
from sim2bids.templates import model_params
from sim2bids.generate import structure
from sim2bids.app import app
from sim2bids.convert import convert
from sim2bids.templates import templates
from sim2bids.generate import utils


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

    if app.CODE is None:
        # instantiate a model class
        model = NoCodeModel(model_name, rhythm, **kwargs)

        # set new parameters and save them in 'param' and 'eq' folders
        model.set_params()

    else:
        XML(inp=app.CODE, output_path=os.path.join(app.OUTPUT, 'code'), uid=app.DESC, suffix=None, params=kwargs)


class NoCodeModel:
    def __init__(self, model_name, rhythm, **kwargs):
        self.model_name = model_name.lower()
        self.params = self.get_params()
        self.rhythm = rhythm
        self.possible_params = kwargs

        # pylems model parameters
        self.id = 1

    def get_params(self):
        if self.model_name == 'reduced_wong_wang':
            return model_params.reduced_wong_wang
        elif self.model_name in ['hindmarsh_rose', 'sjhm3d']:
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


class XML:
    """
    Main class that reads Python code, finds the model used, preprocesses parameters
    specified in the code and passes to the Models class to change the default values
    and saves XML files.

    Parameters
    ----------
    inp :               str (default='../examples/50healthy_code.py')
        Path to the Python code that contains one of the models (HindmarshRose, WongWang, etc)

    output_path :       str, dict (default='../examples')
        Path to a folder that will store converted XML files OR
        Dictionary containing model parameters & model keyword that specifies the model being used

    unit :              str (default='s' (seconds))
        # TODO: add description here

    uid :               str (default = 'default')
        Unique identifier that is used in lems.Component construction

    app:              bool (default=False)
        Whether the user is using this conversion through BEP034 conversion app (https://github.com/dissagaliyeva/incf).
        If True, the conversions will follow BIDS format. For that you will need to supplement "uid" and "suffix" fields.

    store_numeric :     bool (default=True)
        Whether to store only numeric values. For example, if you want to disregard
        'variables_of_interest' = ['xi', 'alpha'] in the final XML file, you should leave the default True value.

    suffix :            str (default=None)
        Suffix used in the final XML name. By default, two files get saved: model's equations (e.g., SJHM3D for
        HindmarshRose model -> model-SJHM3D_{uid}.xml) and parameters (e.g., {suffix}_param.xml).

    """

    def __init__(self, inp: [str, dict] = '../examples/50healthy_code.py', output_path='../examples',
                 unit='s', uid='default', suffix=None, save=True, params=None):
        # define passed-in parameters
        self.input = inp
        self.output = output_path
        self.unit = unit
        self.uid = uid
        self.app = app
        self.suffix = suffix
        self.save = save
        self.input_params = params

        # create placeholder for to-be-supplemented variables
        self.model_name = None
        self.params = None
        self.model = None
        self.temp_params = None

        # self.models = ['hindmarsh_rose', 'wongwang', 'oscillator']  # supported models

        if isinstance(inp, str):
            self.content = utils.open_file(inp)  # get content from the input path
            self.get_model()
            self.check_params()
        elif isinstance(inp, dict):
            model = inp['model']
            del inp['model']

            if app and save:
                self.check_params()
                self.model = CodeModel(model, self.output, self.uid, suffix=self.suffix, **inp)

    def get_model(self):
        """
        Function that finds models and their parameters used in Python code.
        """

        # combine list to form string literal
        pattern = ''.join(self.content)

        # find models used and their parameters ignoring upper-, lower-case
        match = re.findall(r'(?:hindmarsh|wongwang|oscillator)[a-zA-Z0-9=()\]\[\'\"\.\,\s\-\_]+',
                           pattern, flags=re.IGNORECASE)

        # only if there's a match, traverse parameters and get their 'cleaned' version
        if len(match) > 0:
            # get only parameters
            self.model_name = re.match('[a-zA-Z]+', match[0])[0].lower()

            # clean further to get parameters
            self.temp_params = [x.strip(',') for x in re.findall(r'[a-zA-Z0-9]+\=[0-9\,\.\-\'\"\[\]]+', match[0])
                                if x.endswith('],')]

            # traverse cleaned parameters to get a dictionary of parameters
            self.split_params()

            if self.save:
                # call the Models class to save XML files
                self.model = CodeModel(self.model_name, self.output, self.uid, suffix=self.suffix, **self.params)

    def check_params(self):
        if 'hindmarsh' in self.model_name.lower():
            comp_name = 'SJHM3D'
        elif 'wongwang' in self.model.lower():
            comp_name = 'RWW'
        else:
            comp_name = 'G2DOS'

        for k, v in self.input_params.items():
            if k in RHYTHMS:
                for value in v:
                    speed, csf = value[0], value[1]

                    model = lems.Model()
                    ct = lems.ComponentType(name='global_parameters')
                    ct.add(lems.Constant(name='global_speed', value=speed))
                    ct.add(lems.Constant(name='global_coupling', value=csf))
                    model.add(ct)

                    path = f'desc-{app.DESC}_{k}-{speed}-G{csf}.xml'
                    model.export_to_file(os.path.join(app.OUTPUT, 'param', path))
                    convert.to_json(path.replace('xml', 'json'), shape=None,
                                    desc=utils.TVB_MODELS[comp_name]['desc'], key='param')


            # if isinstance(v, dict) and k in RHYTHMS:
            #     for k2, v2 in v.items():
            #         model = lems.Model()
            #         ct = lems.ComponentType(name='global_parameters')

                    # if len(v2) > 0:
                    #     name = 'global_coupling' if k2 == 'csf' else 'global_speed' if k2 == 'speed' else None
                    #     if name:
                    #         for value in v2:
                    #             ct.add(lems.Constant(name=name, value=value))

    def split_params(self):
        """
        Preprocess the result of regex traversal and store parameters in a dictionary.
        These parameters need to be stored in a dictionary because the default model's
        parameters will be altered with the new values (hence, these cleaned values
        in a dictionary).

        For example, if input is: ['r=[0.006]', 'a=[1.0]', 'b=[3.0]', 'c=[1.0]'], the
        output will become: {'r': [0.006], 'a': [1.0], 'b': [3.0], 'c': [1.0]}
        """
        # create an empty dictionary that will store new values
        struct = {}

        # traverse over list of parameters
        for param in self.temp_params:
            k = re.match(r'[a-zA-Z0-9]+', param)[0]
            v = re.findall(r'[0-9\.]+', re.findall(r'\[[0-9\.\-]+', param)[0])[0]
            struct[k] = [float(v)]

        self.params = struct


class CodeModel:
    """
    Create an XML model using PyLEMS and supplemented Python code, change default parameters,
    and save files in the specified folder.

    Parameters
    ----------
    model_name :        str (default = 'hindmarshRose')
        Name of the model found in Python code. Supported model(s): HindmarshRose.

    output:             str (default='../examples')
        Path to the folder where conversions need to be stored.

    uid:                str (default = 'default')
        Unique identifier that is used in lems.Component construction

    app:              bool (default=False)
        Whether the user is using this conversion through BEP034 conversion app (https://github.com/dissagaliyeva/incf).
        If True, the conversions will follow BIDS format. For that you will need to supplement "uid" and "suffix" fields.

    unit:               str (default='s')
        # TODO: add description here

    store_numeric :     bool (default=True)
        Whether to store only numeric values. For example, if you want to disregard
        'variables_of_interest' = ['xi', 'alpha'] in the final XML file, you should leave the default True value.

    suffix :            str (default=None)
        Suffix used in the final XML name. By default, two files get saved: model's equations (e.g., SJHM3D for
        HindmarshRose model -> model-SJHM3D_{uid}.xml) and parameters (e.g., {suffix}_param.xml).

    **params:           dict
        Parameters derived from Python code, already preprocessed in main.py.

    """
    def __init__(self, model_name: str = 'hindmarshrose', output: str = 'examples', uid: str = 'default',
                 rhythm: [str, None] = None, unit: [str, None] = None, suffix: str = None, **params):
        self.model_name = model_name                    # chosen model
        self.output = output                            # path to store output results
        self.uid = uid                                  # lems.Component's id_ parameter
        self.rhythm = rhythm                            # rhythm used, default=None
        self.unit = unit                                # time unit, default=None
        self.suffix = suffix                            # suffix to use in file naming
        self.params = params                            # parameters derived from supplemented Python code

        self.path = None                                # full path (with file name)
        self.model = None                               # lems model
        self.comp_type = uid                            # model name (SJHM3D, WongWang)

        self.models = {
            # define default values of HindmarhRose from TVB model's package
            # https://github.com/the-virtual-brain/tvb-root/blob/master/tvb_library/tvb/simulator/models/stefanescu_jirsa.py
            'hindmarshrose': utils.TVB_MODELS['SJHM3D']['params'],
            'g2dos': utils.TVB_MODELS['G2DOS']['params'],
            'reduced_wong_wang': utils.TVB_MODELS['RWW']['params']
        }

        # run the steps to save files
        self.execute_steps()

    def execute_steps(self):
        """
        Define the steps to verify, preprocess, and save XML files.
        """
        # change default model values with values found in Python code
        self.change_params()

        # save XML files
        if self.model is not None:
            # get LEMS model and Components
            model = self.create_params()

            # save the default parameters and model
            self.save_xml(model)

            self.save_xml(model, 'model')

    def change_params(self):
        """
        Iterate over newly-found parameters and change the default values.
        """

        # copy the existing model
        temp = self.models[self.model_name].copy()

        # change default values and store in a new variable
        self.model = {key: self.params.get(key, temp[key]) for key in temp.keys()}

    def create_params(self):
        """
        Create lems.Model and add the components.
        """

        # instantiate lems.Model
        model = lems.Model()

        # define model's type
        if self.model_name == 'hindmarshrose':
            self.comp_type = 'SJHM3D'
        elif self.model_name == 'reduced_wong_wang':
            self.comp_type = 'RWW'
        elif self.model_name == 'generic2doscillator':
            self.comp_type = 'G2DOS'

        if self.comp_type is not None:
            # remove brackets and store only numeric values
            self.model = {k: v[0] for k, v in self.model.items() if isinstance(v, list) and len(v) == 1}

            # store only those parameters that have numeric values,
            # this will be used and stored in ../output/param folder
            if self.suffix:
                model.add(lems.Component(id_=self.uid, type_=self.comp_type, **self.model))
            else:
                model.add(lems.Component(id_=self.uid, type_=self.comp_type,
                                         **utils.preprocess_params(utils.TVB_MODELS[self.comp_type]['params'])))

        return model

    def save_xml(self, model, ftype='default'):
        """
        Save the model to XML file.

        Parameters
        ----------
        model :     lems.api.Model
            Model with parameters, equations, or parameters & equations

        ftype :     str (default='default')
            How the results need to be stored
            # TODO: give examples

        """
        if not os.path.exists(self.output):
            os.mkdir(self.output)

        # save the default model
        if ftype == 'default':
            if self.suffix:
                self.path = os.path.join(self.output, f'desc-{self.suffix}_param.xml')
            else:
                if self.uid != 'default':
                    self.uid = self.uid.split('_')[0]
                self.path = os.path.join(self.output, f'{self.uid}_param.xml')

            model.export_to_file(self.path)
            self.model = model
        elif ftype == 'model':
            self.merge_xml()

    def merge_xml(self):
        """
        Function that merges model's equations found in 'data/[hindmarshRose|wongwang].xml'
        and parameters found in Python code.
        """
        # here = os.path.dirname(os.path.abspath(__file__))
        if self.model_name == 'hindmarshrose':
            model_name = 'hindmarsh_rose'
        elif self.model_name == 'reducedwongwang':
            model_name = 'reduced_wong_wang'
        else:
            model_name = 'generic2doscillator'

        if os.path.exists(self.path):
            xml1 = self.path
            xml2 = f'../sim2bids/models/{model_name}.xml'
            file = os.path.join(self.output, f'model-{self.comp_type}_{self.uid}.xml')

            exists = False

            if os.path.exists(file):
                os.remove(file)

            for fname in [xml2, xml1]:
                with open(file, 'a') as outfile:
                    with open(fname) as infile:
                        for line in infile:
                            if line.startswith('<Lems') or line.startswith('<?xml'):
                                if not exists:
                                    outfile.write(line)
                            else:
                                if not exists and line.startswith('</Lems>'):
                                    continue
                                outfile.write(line)
                exists = True

            # save eq xml
            shutil.copy(xml2, os.path.join(self.output, f'desc-{self.suffix}_eq.xml'))
