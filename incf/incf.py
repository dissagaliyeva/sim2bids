import json
import os
from collections import OrderedDict

import pandas as pd
import panel as pn
import param

import incf.generate.subjects as subj
import incf.preprocess.preprocess as prep
from incf import utils
from incf.app import app
from incf.convert import convert
from incf.templates import user_guide as ug
from incf.validate import validate

JE_FIELDS = ['Units', 'Description', 'CoordsRows', 'CoordsColumns', 'ModelEq', 'ModelParam', 'SourceCode',
             'SourceCodeVersion', 'SoftwareVersion', 'SoftwareName', 'SoftwareRepository', 'Network']
UNITS = ['s', 'm', 'ms', 'degrees', 'radians']

REQUIRED = None

AUTOFILL = True


class MainArea(param.Parameterized):
    # generate files button
    gen_btn = param.Action(lambda self: self._generate_files(), label='Generate Files')

    # generate structure button
    gen_struct = param.Action(lambda self: self._generate_struct(), label='Show Folder Structure')

    # rename files button
    rename_btn = param.Action(lambda self: self._rename(), label='Rename Files')

    # sidebar components
    output_path = pn.widgets.TextInput(value='../output', margin=(-20, 10, 0, 10))
    app.OUTPUT = output_path.value

    desc = pn.widgets.TextInput(value='default', max_length=30, margin=(-20, 10, 0, 10))
    app.DESC = desc.value

    checkbox_options = ['Traverse subfolders', 'Autocomplete columns', 'Copy input folder']
    checkbox_group = pn.widgets.CheckBoxGroup(value=['Traverse subfolders', 'Autocomplete columns'],
                                              options=checkbox_options,
                                              margin=(-20, 10, 0, 10))
    rename_files = pn.WidgetBox()

    def __init__(self, **params):
        super().__init__(text_input=pn.widgets.TextInput(name='Insert Path'),
                         cross_select=pn.widgets.CrossSelector(options=os.listdir()),
                         **params)
        self.structure = pn.widgets.StaticText(margin=(5, 0, 50, 20))
        self.subjects = None
        self.length = 0
        self.struct = ''

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

        if len(self.cross_select.value) == 0:
            utils.reset_values()

            for _ in self.rename_files:
                self.rename_files.pop(-1)

        if self.length != len(self.cross_select.value):
            utils.reset_values()

            for _ in self.rename_files:
                self.rename_files.pop(-1)

        if len(self.cross_select.value) > 0:
            # Step 1: traverse files and check for problems
            # appert.check_input(path=self.text_input.value, files=self.cross_select.value)
            self.subjects, self.struct = app.main(path=self.text_input.value,
                                                  files=self.cross_select.value,
                                                  save=False, layout=False)

            self.length = len(self.cross_select.value)

    def _generate_files(self, event=None):
        _ = app.main(path=self.text_input.value, files=self.cross_select.value,
                     subs=self.subjects, save=True, layout=True)
        subj.TO_RENAME = None
        app.ALL_FILES = None

    def _generate_struct(self, event=None):
        self.subjects, self.struct = app.main(path=self.text_input.value,
                                              files=self.cross_select.value,
                                              save=False, layout=True)

        if subj.TO_RENAME is not None:
            if len(subj.TO_RENAME) > len(self.rename_files):
                self.rename_files += [*utils.append_widgets(subj.TO_RENAME)]
                self.rename_files.append(pn.Param(self, parameters=['rename_btn'],
                                                  show_name=False,
                                                  widgets={'rename_btn': {'button_type': 'primary'}}))
        else:
            for _ in self.rename_files:
                self.rename_files.pop(-1)

        self.structure.value = self.struct

    @pn.depends('checkbox_group.value', watch=True)
    def _change_checkbox(self):
        global AUTOFILL

        # whether to traverse sub-folders
        app.TRAVERSE_FOLDERS = True if self.checkbox_options[0] in self.checkbox_group.value else False

        # whether to autofill all files
        AUTOFILL = True if self.checkbox_options[1] in self.checkbox_group.value else False

        # whether to not alter original input folder
        if self.checkbox_options[2] in self.checkbox_group.value:
            self.text_input.value = app.duplicate_folder(self.text_input.value)

    @pn.depends('output_path.value', watch=True)
    def _store_output(self):
        output = self.output_path.value

        if len(output) > 0:
            if not os.path.exists(output):
                pn.state.notifications.error(f'Folder `{output}` does not exist!')
            else:
                pn.state.notifications.success(f'Folder `{output}` is selected as output folder')
                app.OUTPUT = output

    def _rename(self, event=None):
        validate.validate(self.rename_files, app.ALL_FILES)

    @pn.depends('desc.value', watch=True)
    def _change_desc(self):
        old, new = app.DESC, self.desc.value

        if old != new:
            app.DESC = new
            pn.state.notifications.success(f'Changed description from `{old}` to `{new}`.')

    def view(self):
        main = pn.Tabs(
            ('Select Files', pn.Column(pn.pane.Markdown(GET_STARTED),
                                       self.text_input,
                                       self.cross_select,
                                       pn.Row(
                                           pn.Param(self, parameters=['gen_struct'],
                                                    show_name=False,
                                                    widgets={'gen_struct': {'button_type': 'primary'}}),
                                           pn.Param(self, parameters=['gen_btn'],
                                                    show_name=False, widgets={'gen_btn': {'button_type': 'primary'}}),
                                           sizing_mode='stretch_width', margin=(50, 0, 0, 0)
                                       ),
                                       self.structure)),
            ('Preprocess Data', self.rename_files),
            ('View Results', ViewResults().view()),
            ('User Guide', UserGuide().view()),
            dynamic=True, active=0
        )

        sidebar = pn.Column(
            '## Settings',
            '#### Provide output path',
            self.output_path,
            '#### Provide short description (max 30 chars)',
            self.desc,
            '#### Select additional settings',
            self.checkbox_group,
        )

        return pn.template.FastListTemplate(
            title='Visualize | Transform | Download',
            sidebar=sidebar,
            site='INCF',
            main=main,
            sizing_mode="stretch_both"
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

                je = pn.widgets.JSONEditor(value=file, height=350, mode='view')
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
        contents = {}
        to_remove = []

        for idx, inputs in enumerate(txt_inputs):
            value = inputs.value
            name = inputs.name.split(' ')[-2]
            self.je_widget[0][0].value[name] = value

            if self.je_widget[0][0].value[name] == '':
                to_remove.append(name)

            contents[name] = value

        if utils.verify_complete(txt_inputs):
            content = {}

            self.widget.pop(-1)
            self.widget.append(self.je_widget)

            # remove empty columns
            for k, v in contents.items():
                if v == '' or k in to_remove:
                    del self.je_widget[0][0].value[k]
                else:
                    content[k] = v

            # autocomplete the files with the same ending
            if AUTOFILL:
                for path in self.select_options.options:
                    if self.file.split('.')[-2].split('_')[-1] in path:
                        file = json.load(open(path))
                        temp = {}

                        for k, v in file.items():
                            if k in content.keys():
                                temp[k] = content[k]
                        temp['NumberOfColumns'] = file['NumberOfColumns']
                        temp['NumberOfRows'] = file['NumberOfRows']

                        with open(path, 'w') as f:
                            json.dump(OrderedDict(temp), f)

            # save output
            with open(self.select_options.value, 'w') as f:
                json.dump(OrderedDict(self.je_widget[0][0].value), f)
        else:
            pn.state.notifications.error('Please fill in ALL required fields.', duration=5000)

    def view(self):
        return pn.Column(self.file_selection, self.widget)


class UserGuide(param.Parameterized):
    user_guide = pn.widgets.ToggleGroup(name='User Guide', value='App 101', behavior='radio',
                                        options=['App 101', 'Preprocess data', 'Supported files',
                                                 'Functionality', 'BEP034'])

    def __init__(self, **params):
        super().__init__(**params)
        self.map = {'App 101': ug.how_to_use,
                    'Preprocess Data': ug.preprocess,
                    'Format & Files': ug.supported,
                    'Functionality': ug.functionality,
                    'BEP034': ug.bep034}
        self.text = pn.widgets.StaticText(value=self.map['App 101'])

    @pn.depends('user_guide.value', watch=True)
    def _change_sel(self):
        self.text.value = self.map[self.user_guide.value]

    def view(self):
        return pn.Column(self.user_guide, self.text, scroll=True, height=600)


def get_files(path='../output', ftype='.json'):
    f = []

    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            if ftype in name:
                f.append(os.path.join(root, name))
    return f


SELECT_FILES = """
### Select file(s)

This widgets lets you select multiple files without specifying the folder. There's no limit on the file numbers. However,
note that the accepted file types are `.mat`, `.txt`, `.zip`, `.h5`. If you select other files, they will be simply ignored
without errors.
"""

SELECT_FOLDERS = """
### Select folder(s)

This widgets lets you select multiple folders. Unfortunately, the input with current path doesn't get updated if specified.
However, you can use the arrows to find the folders.
"""

GET_STARTED = """
## Welcome!
Here you can select the folder(s) that you want to transform. Beware that we are using recursive walk to select all the
content available in the specified folder. That means if the folder contains a sub-folder, we will transform the content
if it falls into the accepted file formats.
Below you will see the generated folder with content as specified at [BIDS Computational Model Specification](https://docs.google.com/document/d/1NT1ERdL41oz3NibIFRyVQ2iR8xH-dKY-lRCB4eyVeRo/edit?usp=sharing){:target="_blank"}.
If you are happy with the results, press `Transform Files` button at the bottom of the screen. We will not start
generation until you press the button below.
"""
