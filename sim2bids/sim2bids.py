import json
import os
from collections import OrderedDict

import pandas as pd
import panel as pn
import param

from sim2bids import utils
from sim2bids.app import app, utils as app_utils
from sim2bids.templates import user_guide as ug, templates
from sim2bids.validate import validate

# import comp_validator.comp_validator as val


JE_FIELDS = ['Units', 'Description', 'CoordsRows', 'CoordsColumns', 'ModelEq', 'ModelParam', 'SourceCode',
             'SourceCodeVersion', 'SoftwareVersion', 'SoftwareName', 'SoftwareRepository', 'Network']
UNITS = ['s', 'm', 'ms', 'degrees', 'radians']
OPTIONS = ['App 101', 'Preprocess data', 'BEP034']
REQUIRED = None
AUTOFILL = True

rhythms = pn.Column('#### Specify rhythms', pn.widgets.CheckBoxGroup(
    value=[], options=['Alpha', 'Beta', 'Delta', 'Gamma', 'Theta'],
    inline=True, margin=(-10, 0, 0, 0)))

speed = pn.Column('#### Specify `conduction speed` folder name',
                  pn.widgets.TextInput(value='cspeed', margin=(-10, 0, 0, 0)))

global_coupling = pn.Column('#### Specify `global coupling scaling factor` folder name',
                            pn.widgets.TextInput(value='csf', margin=(-10, 0, 0, 0)))


class MainArea(param.Parameterized):
    # generate files button
    gen_btn = param.Action(lambda self: self._generate_files(), label='Generate Files')

    # validate files
    val_btn = param.Action(lambda self: self._show_bids(), label='Validate Conversions')

    # generate structure button
    gen_struct = param.Action(lambda self: self._generate_struct(), label='Show Structure')

    # rename files button
    rename_btn = param.Action(lambda self: self._rename(), label='Rename Files')

    # sidebar components
    output_path = pn.widgets.TextInput(value=app.OUTPUT, margin=(-20, 10, 0, 10))
    # app.OUTPUT = output_path.value

    input_path = pn.widgets.TextInput(value=app.INPUT, margin=(-20, 10, 0, 10))
    # app.OUTPUT = output_path.value

    desc = pn.widgets.TextInput(value='default', max_length=30, margin=(-20, 10, 0, 10))
    app.DESC = desc.value

    checkbox_options = ['Traverse subfolders', 'Autocomplete columns', 'Copy input folder']
    checkbox_group = pn.widgets.CheckBoxGroup(value=['Traverse subfolders', 'Autocomplete columns'],
                                              options=checkbox_options,
                                              margin=(-20, 10, 0, 10))

    speed = pn.Column('#### Specify `conduction speed` folder name',
                      pn.widgets.TextInput(value=app.COND_SPEED, margin=(-10, 0, 0, 0)))

    global_coupling = pn.Column('#### Specify `global coupling scaling factor` folder name',
                                pn.widgets.TextInput(value=app.GLB_COUP_SF, margin=(-10, 0, 0, 0)))

    rename_files = pn.WidgetBox()

    def __init__(self, **params):
        super().__init__(text_input=pn.widgets.TextInput(name='Insert Path'),
                         cross_select=pn.widgets.CrossSelector(options=os.listdir()),
                         **params)
        self.structure = pn.widgets.StaticText(margin=(5, 0, 50, 20))
        self.subjects = None
        self.length = 0
        self.struct = ''
        self.to_rename = []

    @pn.depends('text_input.value', watch=True)
    def _select_path(self):
        if os.path.exists(self.text_input.value):
            # whether to not alter original input folder
            if self.checkbox_options[2] in self.checkbox_group.value:
                self.text_input.value = app.duplicate_folder(self.text_input.value)

            self.cross_select.options = os.listdir(self.text_input.value)
            self.cross_select.value = []
            self.structure.value = ''
            utils.reset_values()

    @pn.depends('cross_select.value', watch=True)
    def _generate_path(self):
        self.structure.value = ''
        selected = self.cross_select.value

        if len(selected) == 0:
            utils.reset_values()
            app.ALL_FILES = None
            app.ADDED_FILES = []
            app.CODE = None
            self.to_rename = []
            self.to_rename_path = []
            self.structure.value = []
            self.rename_files = pn.WidgetBox()
            self.to_rename = None
            self.to_rename_path = None

        if len(selected) > 0:
            # check files for preprocessing step
            utils.reset_values()
            app.ALL_FILES = None
            app.ADDED_FILES = []
            path = self.text_input.value
            app.preprocess_input(path, selected)

            self.to_rename = validate.filter(app_utils.get_content(path, selected, basename=True))
            self.to_rename_path = validate.filter(app_utils.get_content(path, selected), self.to_rename)

            if len(self.to_rename) > len(self.rename_files) + 1:
                self.rename_files += [*utils.append_widgets(self.to_rename)]
                self.rename_files.append(pn.Param(self, parameters=['rename_btn'], show_name=False,
                                                  widgets={'rename_btn': {'button_type': 'primary'}}))
            else:
                self.rename_files = pn.WidgetBox()

            self.length = len(selected)

    def _generate_files(self, event=None):
        if app.ALL_FILES and app.ADDED_FILES and len(app.ALL_FILES) != len(app.ADDED_FILES):
            # continue converting the files
            _ = app.main(path=self.text_input.value,
                         files=list(set(app.ALL_FILES).difference(set(app.ADDED_FILES))),
                         subs=self.subjects, save=True, layout=True)

        else:
            if validate.IS_RENAMED:
                _ = app.main(path=self.text_input.value,
                             files=validate.RENAMED,
                             # files=utils.get_all_files(validate.RENAMED, self.cross_select.value, self.text_input.value),
                             subs=self.subjects, save=True, layout=True)
            else:
                _ = app.main(path=self.text_input.value, files=self.cross_select.value,
                             subs=self.subjects, save=True, layout=True)

    def _show_bids(self, event=None):
        if not os.path.exists(app.OUTPUT):
            pn.state.notifications.error('Please convert files first.')
        else:
            validate.validate(app.OUTPUT)

    def view_ew(self):
        files = os.listdir()
        if 'errors.md' in files and 'warnings.md' in files:
            return pn.Tabs(('See errors', pn.pane.Markdown('\n'.join(open('errors.md').readlines()))),
                           ('See warnings', pn.pane.Markdown('\n'.join(open('warnings.md').readlines()))))
        return 'Please click on `Validate Conversions` button to see errors/warnings.'


    def _generate_struct(self, event=None):
        self.subjects, self.struct = app.main(path=self.text_input.value,
                                              files=self.cross_select.value,
                                              save=False, layout=True)
        self.structure.value = self.struct

    @pn.depends('checkbox_group.value', watch=True)
    def _change_checkbox(self):
        global AUTOFILL

        # whether to traverse sub-folders
        app.TRAVERSE_FOLDERS = True if self.checkbox_options[0] in self.checkbox_group.value else False

        # whether to autofill all files
        AUTOFILL = True if self.checkbox_options[1] in self.checkbox_group.value else False

        # TODO: add copy folder functionality
        # whether to not alter original input folder
        # if self.checkbox_options[2] in self.checkbox_group.value:
        #     self.text_input.value = app.duplicate_folder(self.text_input.value)

    @pn.depends('input_path.value', watch=True)
    def _store_input(self):
        inputs = self.input_path.value

        if len(inputs) > 0:
            if not os.path.exists(inputs):
                pn.state.notifications.success(f'Folder {inputs} is created...')
                os.mkdir(inputs)

            pn.state.notifications.success(f'Folder `{inputs}` is selected as input folder...')
            app.INPUT = inputs

    @pn.depends('output_path.value', watch=True)
    def _store_output(self):
        output = self.output_path.value

        if len(output) > 0:
            if not os.path.exists(output):
                pn.state.notifications.success(f'Folder {output} is created...')
                os.mkdir(output)

            pn.state.notifications.success(f'Folder `{output}` is selected as output folder...')
            app.OUTPUT = output

    def _rename(self, event=None):
        validate.validate(self.rename_files, self.to_rename_path, self.text_input.value, self.cross_select.value)
        self.rename_files = pn.WidgetBox()
        self.to_rename = None
        self.to_rename_path = None

    @pn.depends('desc.value', watch=True)
    def _change_desc(self):
        app.DESC = self.desc.value
        pn.state.notifications.success(f'Description {app.DESC} has been saved...')

    def view(self):
        main = pn.Tabs(
            ('Select Files', pn.Column(pn.pane.Markdown(GET_STARTED),
                                       self.text_input,
                                       self.cross_select,
                                       pn.Param(self, parameters=['gen_btn'],
                                                show_name=False, widgets={'gen_btn': {'button_type': 'primary'}}),
                                       pn.Param(self, parameters=['val_btn'],
                                                show_name=False, widgets={'val_btn': {'button_type': 'primary'}}),
                                       # pn.Row(
                                       #     pn.Param(self, parameters=['gen_struct'],
                                       #              show_name=False,
                                       #              widgets={'gen_struct': {'button_type': 'primary'}}),
                                       #     pn.Param(self, parameters=['gen_btn'],
                                       #              show_name=False, widgets={'gen_btn': {'button_type': 'primary'}}),
                                       #     sizing_mode='stretch_width', margin=(50, 0, 0, 0)
                                       # ),
                                       )),
            ('Preprocess Data', pn.Column(PREPROCESS, self.rename_files)),
            ('View Results', ViewResults().view()),
            ('Validate Conversions', self.view_ew()),
            ('Advanced Settings', ViewResults().view()),
            ('User Guide', UserGuide().view()),
            dynamic=True, active=0
        )

        sidebar = pn.Column(
            '## Settings',
            '#### Provide output path',
            self.output_path,
            # '#### Provide short description (max 30 chars)',
            # self.desc,
            # '#### Select additional settings',
            # self.checkbox_group,
            # # '#### Specify simulation information',
            # self.speed, self.global_coupling
        )

        return pn.template.MaterialTemplate(
            title='Preprocess | Transform | Download',
            # sidebar=sidebar,
            site='sim2bids',
            main=main,
            header_background='#4488c4'
        )


class ViewResults(param.Parameterized):
    options = ['JSON files', 'TSV files']
    file_selection = pn.widgets.RadioButtonGroup(options=options, button_type='primary', value=[])
    select_options = pn.widgets.Select()
    je_btn = param.Action(lambda self: self._update_je(), label='Update JSON file')

    def __init__(self):
        super().__init__()
        self.path = app.OUTPUT
        self.layout = None
        self.widget = pn.WidgetBox('### Select File', self.select_options)
        self.je_widget = pn.WidgetBox()

    @pn.depends('file_selection.value', watch=True)
    def _change_filetype(self):
        if self.file_selection.value == 'JSON files':
            self.select_options.options = get_files(path=self.path)
        elif self.file_selection.value == 'TSV files':
            self.select_options.options = get_files(path=self.path, ftype='.tsv')

    @pn.depends('select_options.value', watch=True)
    def _change_file(self):
        if len(self.widget) > 2:
            self.widget.pop(-1)

        if self.file_selection.value == 'JSON files':
            try:
                file = json.load(open(self.select_options.value))
                self.file = self.select_options.value
            except Exception:
                pn.state.notifications.error(f'File `{self.select_options.value}` is empty!')
            else:
                if len(self.je_widget) > 0:
                    self.je_widget = pn.WidgetBox()

                je = pn.widgets.JSONEditor(value=file, height=500, mode='view')
                je_widget = utils.get_settings(OrderedDict(je.value), self.select_options.value)
                self.je_widget.append(pn.Row(je, pn.Column(je_widget,
                                                           pn.Param(self, parameters=['je_btn'], show_name=False,
                                                                    widgets={'je_btn': {'button_type': 'primary'}}))))
                self.widget.append(self.je_widget)
        elif self.file_selection.value == 'TSV files':
            try:
                file = pd.read_csv(self.select_options.value, sep='\t', header=None, index_col=None)
            except Exception:
                pn.state.notifications.error(f'File `{self.select_options.value}` is empty!')
            else:
                self.widget.append(pn.widgets.Tabulator(file))

    def _update_je(self, event=None):
        txt_inputs = self.je_widget[0][1][0]
        file = json.load(open(self.file))

        if utils.verify_complete(txt_inputs):
            # instantiate a new dictionary
            content = OrderedDict(file.items())

            # iterate over inputs and add new values if supplemented
            for inp in txt_inputs:
                if inp.value != '':
                    name = inp.name.split(' ')[1]
                    content[name] = inp.value

            update_files(content)

            # save values
            with open(self.file, 'w') as f:
                json.dump(content, f)

            # update layout
            je = pn.widgets.JSONEditor(value=json.load(open(self.file)), height=350, mode='view')
            je_widget = utils.get_settings(OrderedDict(je.value), self.select_options.value)
            self.widget[-1] = pn.Row(je, pn.Column(je_widget, pn.Param(self, parameters=['je_btn'], show_name=False,
                                                                       widgets={'je_btn': {'button_type': 'primary'}})))

        else:
            pn.state.notifications.error('Please fill in ALL required fields.', duration=5000)

    def view(self):
        return pn.Column(self.file_selection, self.widget)


class UserGuide(param.Parameterized):
    user_guide = pn.widgets.ToggleGroup(name='User Guide', value='App 101', behavior='radio',
                                        options=OPTIONS)

    def __init__(self, **params):
        super().__init__(**params)
        self.map = {OPTIONS[0]: ug.how_to_use,
                    OPTIONS[1]: ug.preprocess,
                    OPTIONS[-1]: ug.bep034}
        self.text = pn.widgets.StaticText(value=self.map[OPTIONS[0]])

    @pn.depends('user_guide.value', watch=True)
    def _change_sel(self):
        self.text.value = self.map[self.user_guide.value]

    def view(self):
        return pn.Column(self.user_guide, self.text, scroll=True, height=800)


def update_files(content):
    to_ignore = [*templates.required, 'Units', 'ModelEq', 'ModelParam',
                 'ModelParam', 'SourceCode', 'SoftwareName', 'SoftwareRepository', 'Network']

    for file in get_files():
        # get keys for the existing json file in the output folder
        file_json = json.load(open(file))

        # get the folder name to get the 'recommended' fields
        folder = os.path.basename(os.path.dirname(file))
        keys = templates.struct.get(folder, None)

        # filter out only json files
        if keys:
            for k, v in content.items():
                if (k in keys['required'] or k in keys['recommend']) and content[k] and \
                        (file_json[k] is None or file_json[k] != content[k]) and k not in to_ignore:
                    if v is not None:
                        file_json[k] = content[k]

        # save new fields
        with open(file, 'w') as f:
            json.dump(file_json, f)


def get_files(path=app.OUTPUT, ftype='.json'):
    f = []

    for root, dirs, files in os.walk(path, topdown=False):
        for file in files:
            if ftype in file and '.ipynb_checkpoints' not in file and 'tvb-framework' not in root and 'tvb_framework' not in root:
                f.append(os.path.join(root, file))
    return f


GET_STARTED = """
## Welcome!
Here you can select the folder(s) that you want to transform. Beware that we are using recursive walk to select all the
content available in the specified folder. That means if the folder contains a sub-folder, we will transform the content
if it falls into the accepted file formats.

Click on **Generate Files** button to physically save the results. After that, please 
**make sure to give user-specific input** by clicking on **View Results** tab and selecting JSON files. You'll see a lot
of required and recommended fields that can be updated. By default, all required fields are already provided. However,
you have all the rights to change them. See further details in **User Guide**. 
"""

PREPROCESS = """
### Preprocessing pipeline
You will see the file names only if there are files that don't match the existing ones. 
"""