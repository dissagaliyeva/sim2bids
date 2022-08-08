import json
import os
from collections import OrderedDict

import pandas as pd
import panel as pn
import param

import incf.preprocess.preprocess as prep
import incf.templates.templates as temp
from incf.convert import convert


JE_FIELDS = ['Units', 'Description', 'CoordsRows', 'CoordsColumns', 'ModelEq', 'ModelParam', 'SourceCode',
             'SourceCodeVersion', 'SoftwareVersion', 'SoftwareName', 'SoftwareRepository', 'Network']
UNITS = ['s', 'm', 'ms', 'degrees', 'radians']


def get_files(path='../output', ftype='.json'):
    f = []

    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            if ftype in name:
                f.append(os.path.join(root, name))
    return f


class MainArea(param.Parameterized):
    # generate files button
    gen_btn = param.Action(lambda self: self._generate_files(), label='Generate Files')

    # sidebar components
    output_path = pn.widgets.TextInput(value='../output', margin=(-20, 10, 0, 10))
    convert.OUTPUT = output_path.value

    desc = pn.widgets.TextInput(value='default', max_length=30, margin=(-20, 10, 0, 10))
    convert.DESC = desc.value

    checkbox_options = ['Traverse subfolders', 'Option 2', 'Option 3']
    checkbox_group = pn.widgets.CheckBoxGroup(value=['Traverse subfolders'],
                                              options=checkbox_options,
                                              margin=(-20, 10, 0, 10))

    def __init__(self, **params):
        super().__init__(text_input=pn.widgets.TextInput(name='Insert Path'),
                         cross_select=pn.widgets.CrossSelector(options=os.listdir()),
                         **params)
        self.structure = pn.widgets.StaticText(margin=(50, 0, 50, 20))
        self.subjects = None
        self.length = 0

    @pn.depends('text_input.value', watch=True)
    def _select_path(self):
        if os.path.exists(self.text_input.value):
            self.cross_select.options = os.listdir(self.text_input.value)
            self.cross_select.value = []
            self.structure.value = ''
            prep.reset_index()

    @pn.depends('cross_select.value', watch=True)
    def _generate_path(self):
        self.structure.value = ''

        if len(self.cross_select.value) == 0:
            prep.reset_index()

        if self.length != len(self.cross_select.value):
            prep.reset_index()

        if len(self.cross_select.value) > 0:
            # Step 1: traverse files and check for problems
            # convert.check_input(path=self.text_input.value, files=self.cross_select.value)
            self.subjects, self.structure.value = convert.check_file(path=self.text_input.value,
                                                                     files=self.cross_select.value,
                                                                     save=False)
            self.length = len(self.cross_select.value)

    def _generate_files(self, event=None):
        _ = convert.check_file(path=self.text_input.value, files=self.cross_select.value,
                               subs=self.subjects, save=True)

    @pn.depends('checkbox_group.value', watch=True)
    def _change_checkbox(self):
        # set whether to traverse sub-folders
        convert.TRAVERSE_FOLDERS = True if self.checkbox_options[0] in self.checkbox_group.value else False

    @pn.depends('output_path.value', watch=True)
    def _store_output(self):
        output = self.output_path.value

        if len(output) > 0:
            if not os.path.exists(output):
                pn.state.notifications.error(f'Folder `{output}` does not exist!', duration=convert.DURATION)
            else:
                pn.state.notifications.success(f'Folder `{output}` is selected as output folder',
                                               duration=convert.DURATION)
                convert.OUTPUT = output

    @pn.depends('desc.value', watch=True)
    def _change_desc(self):
        old, new = convert.DESC, self.desc.value

        if old != new:
            convert.DESC = new
            pn.state.notifications.success(f'Changed description from `{old}` to `{new}`.', duration=convert.DURATION)

    def view(self):
        main = pn.Tabs(
            ('Select Files', pn.Column(pn.pane.Markdown(GET_STARTED),
                                       self.text_input,
                                       self.cross_select,
                                       self.structure,
                                       pn.Param(self, parameters=['gen_btn'],
                                                show_name=False, widgets={'gen_btn': {'button_type': 'primary'}}))),
            ('View Results', ViewResults().view()),
            ('User Guide', UserGuide().view()),
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
            main=main
        )


class ViewResults(param.Parameterized):
    options = ['JSON files', 'TSV files']
    file_selection = pn.widgets.RadioButtonGroup(options=options, button_type='primary', value=[])
    select_options = pn.widgets.Select()
    je_btn = param.Action(lambda self: self._update_je(), label='Update JSON file')

    def __init__(self):
        super().__init__()
        self.path = convert.OUTPUT
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
            except Exception:
                pn.state.notifications.error(f'File `{self.select_options.value}` is empty!')
            else:
                if len(self.je_widget) > 0:
                    self.je_widget = pn.WidgetBox()

                je = pn.widgets.JSONEditor(value=file, height=350, mode='view')
                je_widget = get_settings(OrderedDict(je.value), self.select_options.value)
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
        json_editor = self.je_widget[0][0]

        for idx, inputs in enumerate(txt_inputs):
            value = inputs.value
            name = inputs.name.split(' ')[-1].replace(':', '')
            self.je_widget[0][0].value[name] = value
            self.widget.pop(-1)
            self.widget.append(self.je_widget)

            # save output
            with open(self.select_options.value, 'w') as f:
                json.dump(OrderedDict(self.je_widget[0][0].value), f)

    def view(self):
        return pn.Column(self.file_selection, self.widget)


def get_settings(json_editor, selected):
    widget = pn.WidgetBox()

    for k, v in json_editor.items():
        specs = temp.struct
        reqs = temp.required
        root = os.path.basename(os.path.dirname(selected))
        req = k in specs[root]['required']

        if k in reqs or req:
            name = f'Specify {k} (REQUIRED):'
        else:
            name = f'Specify {k} (RECOMMENDED):'

        if k == 'Units':
            widget.append(pn.widgets.Select(name=name, options=UNITS, value=''))
        elif k not in ['NumberOfColumns', 'NumberOfRows', 'Units']:
            if len(v) > 0 and k in ['CoordsColumns', 'CoordsRows']:
                continue
            widget.append(pn.widgets.TextInput(name=name))

    # append button
    return widget


class UserGuide(param.Parameterized):
    # TODO: Try out 'Select' option from HoloViz

    # content buttons
    intro = pn.widgets.Button(name='Introduction', button_type='light', value=True, width=100)
    sup_files = pn.widgets.Button(name='Supported Files', button_type='light', width=100)
    transform = pn.widgets.Button(name='Transforming Data', button_type='light', width=100)
    how_to = pn.widgets.Button(name='How to use the app', button_type='light', width=100)
    bep034 = pn.widgets.Button(name='BIDS Computational Data Standard', button_type='light', width=100)

    def view(self):
        return pn.Tabs(
            ('Introduction', INTRO),
            ('Supported Files', INTRO),
            ('Transforming Data', INTRO),
            ('How to Use the App', INTRO),
            ('BEP034', INTRO)
        )


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
Here you can select the folder(s) that you want to transform. Beware that we are using recursive walk to select all the content available in the specified folder. That means if the folder contains a sub-folder, we will transform the content if it falls into the accepted file formats.
Below you will see the generated folder with content as specified at [BIDS Computational Model Specification](https://docs.google.com/document/d/1NT1ERdL41oz3NibIFRyVQ2iR8xH-dKY-lRCB4eyVeRo/edit?usp=sharing). If you are happy with the results, press `Transform Files` button at the bottom of the screen. We will not start generation until you press the button below.
"""

INTRO = """
#### Introduction <a name="intro"></a>

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Et ultrices neque ornare aenean euismod elementum nisi. Tincidunt ornare massa eget egestas purus viverra. Quis blandit turpis cursus in hac. Dictum varius duis at consectetur lorem donec. Phasellus faucibus scelerisque eleifend donec pretium vulputate sapien nec. Ipsum nunc aliquet bibendum enim facilisis gravida neque. Odio aenean sed adipiscing diam donec. Massa tincidunt nunc pulvinar sapien et. Nibh nisl condimentum id venenatis a condimentum. Congue quisque egestas diam in arcu cursus. Aenean vel elit scelerisque mauris. Sit amet justo donec enim. Habitant morbi tristique senectus et.


Praesent elementum facilisis leo vel fringilla est ullamcorper. Urna molestie at elementum eu facilisis sed. Maecenas pharetra convallis posuere morbi leo urna molestie. Ultricies lacus sed turpis tincidunt id aliquet risus feugiat in. Facilisi cras fermentum odio eu feugiat pretium nibh ipsum. Sem integer vitae justo eget magna fermentum iaculis. Sollicitudin tempor id eu nisl nunc mi ipsum faucibus vitae. Mauris augue neque gravida in fermentum. Scelerisque eu ultrices vitae auctor eu augue. Sed cras ornare arcu dui.


In mollis nunc sed id semper risus. Velit ut tortor pretium viverra suspendisse. Viverra adipiscing at in tellus integer. Ultricies lacus sed turpis tincidunt. Vitae purus faucibus ornare suspendisse. Arcu cursus vitae congue mauris rhoncus aenean vel elit. Vestibulum lorem sed risus ultricies tristique. A erat nam at lectus urna duis convallis. Etiam erat velit scelerisque in dictum non. Sit amet facilisis magna etiam tempor. Purus gravida quis blandit turpis cursus in hac. Ultricies tristique nulla aliquet enim tortor at auctor.


Quam vulputate dignissim suspendisse in est. Adipiscing tristique risus nec feugiat. Faucibus interdum posuere lorem ipsum dolor sit amet consectetur. Et leo duis ut diam quam nulla porttitor massa. Nisl nisi scelerisque eu ultrices vitae. Sit amet cursus sit amet dictum. Sodales ut eu sem integer vitae justo eget magna. Arcu vitae elementum curabitur vitae. Lobortis elementum nibh tellus molestie. Sit amet est placerat in egestas erat imperdiet sed euismod. Quis enim lobortis scelerisque fermentum dui faucibus in. Nunc mattis enim ut tellus. Accumsan tortor posuere ac ut consequat semper viverra nam libero.


Est velit egestas dui id ornare arcu. A arcu cursus vitae congue mauris. Semper feugiat nibh sed pulvinar proin gravida hendrerit lectus. Malesuada fames ac turpis egestas sed tempus urna et pharetra. Tortor posuere ac ut consequat semper. Etiam dignissim diam quis enim. Leo vel orci porta non pulvinar neque laoreet suspendisse interdum. Ligula ullamcorper malesuada proin libero nunc consequat interdum varius. Eu scelerisque felis imperdiet proin fermentum leo vel. Auctor elit sed vulputate mi sit amet mauris. Et netus et malesuada fames ac turpis egestas. Nisl vel pretium lectus quam id. Amet risus nullam eget felis eget nunc. Tincidunt dui ut ornare lectus sit amet est. Eu consequat ac felis donec et odio pellentesque. Aliquam nulla facilisi cras fermentum odio eu feugiat pretium nibh. Et netus et malesuada fames ac turpis. Mi proin sed libero enim sed. Et malesuada fames ac turpis egestas integer eget aliquet."""
