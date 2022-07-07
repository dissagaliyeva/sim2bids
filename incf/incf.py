import os

import pandas as pd
import param
import panel as pn
import incf.preprocess.generate as gen
import incf.preprocess.preprocess as prep
import json


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
    text_input = pn.widgets.TextInput(name='Insert Path')

    def __init__(self, path):
        super().__init__()
        self.path = path
        self.cross_select = pn.widgets.CrossSelector(options=os.listdir())
        self.static_text = pn.widgets.StaticText(margin=(50, 0, 0, 0))
        self.sid = None

    @pn.depends('text_input.value', watch=True)
    def _select_path(self):
        if os.path.exists(self.text_input.value):
            self.cross_select.options = os.listdir(self.text_input.value)
            self.static_text.value = ''

    @pn.depends('cross_select.value', watch=True)
    def _generate_path(self):
        self.static_text.value = ''

        if len(self.cross_select.value) > 0:
            gen.SID = prep.create_uuid()
            self.sid = gen.SID
            self.static_text.value = gen.check_file(og_path=self.text_input.value,
                                                    values=self.cross_select.value,
                                                    output='../output', save=False)

    def _generate_files(self, event=None):
        gen.SID = self.sid
        _ = gen.check_file(og_path=self.text_input.value,
                           values=self.cross_select.value,
                           output='../output', save=True)

    def view(self):
        main = pn.Tabs(
            ('Select Files', pn.Column(pn.pane.Markdown(GET_STARTED),
                                       self.text_input,
                                       self.cross_select,
                                       self.static_text,
                                       pn.Param(self, parameters=['gen_btn'],
                                                show_name=False, widgets={'gen_btn': {'button_type': 'primary'}}))),
            ('View Results', ViewResults(self.path).view()),
            ('User Guide', UserGuide().view()),
            # ('Settings', Settings().view())
        )

        return pn.template.FastListTemplate(
            title='Visualize | Transform | Download',
            sidebar=Settings().view(),
            site='INCF',
            main=main
        )


class Settings(param.Parameterized):
    sub_options = ['Single subject', 'Multiple subjects']
    sub_select = pn.widgets.RadioButtonGroup(options=sub_options, button_type='default',
                                             value=[], margin=(-20, 0, 0, 0))

    @pn.depends('sub_select.value', watch=True)
    def _change_selection(self):
        pass

    def view(self):
        return pn.Column(
            '## Settings',
            '#### Select subject count',
            self.sub_select
        )


#     def __init__(self):
#         """
#         checkbox_group = pn.widgets.CheckBoxGroup(
#     name='Checkbox Group', value=['Apple', 'Pear'], options=['Apple', 'Banana', 'Pear', 'Strawberry'],
#     inline=True)
#
# checkbox_group
#         """
#         super().__init__(select=pn.widgets.Select(options=self.sel_options, ))

class ViewResults(param.Parameterized):
    options = ['JSON files', 'TSV files']
    file_selection = pn.widgets.RadioButtonGroup(options=options, button_type='primary', value=[])
    select_options = pn.widgets.Select()

    def __init__(self, path):
        super().__init__()
        self.path = path
        self.layout = None
        self.widget = pn.WidgetBox('### Select File', self.select_options)

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
                print(f'File `{self.select_options.value}` is empty!')
            else:
                self.widget.append(pn.widgets.JSONEditor(value=file, height=350))

        elif self.file_selection.value == 'TSV files':
            try:
                file = pd.read_csv(self.select_options.value, sep='\t', header=None, index_col=None)
            except Exception:
                print(f'File `{self.select_options.value}` is empty!')
            else:
                self.widget.append(pn.widgets.Tabulator(file))

    def view(self):
        return pn.Column(self.file_selection, self.widget)


# class ViewResults(param.Parameterized):
#     options = ['JSON files', 'TSV files']
#
#     def __init__(self, path):
#         super().__init__(file_selection=pn.widgets.RadioButtonGroup(options=self.options,
#                                                                     button_type='primary', value=[]),
#                          select_options=pn.widgets.Select())
#         self.path = path
#         self.layout = None
#         self.widget = pn.WidgetBox('### Select File', self.select_options)
#
#     @pn.depends('file_selection.value', watch=True)
#     def _change_filetype(self):
#         if self.file_selection.value == 'JSON files':
#             self.select_options.options = get_files(path=self.path)
#         elif self.file_selection.value == 'TSV files':
#             self.select_options.options = get_files(path=self.path, ftype='.tsv')
#
#     @pn.depends('select_options.value', watch=True)
#     def _change_file(self):
#         if len(self.widget) > 2:
#             self.widget.pop(-1)
#
#         if self.file_selection.value == 'JSON files':
#             try:
#                 file = json.load(open(self.select_options.value))
#             except Exception:
#                 print(f'File `{self.select_options.value}` is empty!')
#             else:
#                 self.widget.append(pn.widgets.JSONEditor(value=file, height=350))
#
#         elif self.file_selection.value == 'TSV files':
#             try:
#                 file = pd.read_csv(self.select_options.value, sep='\t', header=None, index_col=None)
#             except Exception:
#                 print(f'File `{self.select_options.value}` is empty!')
#             else:
#                 self.widget.append(pn.widgets.Tabulator(file))
#
#     def view(self):
#         return pn.Column(self.file_selection, self.widget)


# def verify_keys(json1, json2):
#     diff = set(json1).difference(set(json2))
#     return diff == set(), diff
# class ShowFiles(param.Parameterized):
#     options = ['JSON files', 'TSV files']
#     json_files = get_files()
#     tsv_files = get_files(ftype='.tsv')
#
#     def __init__(self, **params):
#         super().__init__(file_selection=pn.widgets.RadioButtonGroup(options=self.options,
#                                                                     button_type='primary', value=[]),
#                          select_options=pn.widgets.Select(),
#                          json=pn.widgets.JSONEditor(),
#                          tsv=pn.widgets.Tabulator())
#
#         self.layout = None
#         self.json_keys = None
#         self.widget = pn.WidgetBox('### Select File', self.select_options)
#
#     @pn.depends('file_selection.value', watch=True)
#     def _change_filetype(self):
#         if self.file_selection.value == 'JSON files':
#             self.select_options.options = self.json_files
#         elif self.file_selection.value == 'TSV files':
#             self.select_options.options = self.tsv_files
#
#     @pn.depends('select_options.value', watch=True)
#     def _change_file(self):
#         if len(self.widget) > 2:
#             self.widget.pop(-1)
#
#         if self.file_selection.value == 'JSON files':
#             try:
#                 file = json.load(open(self.select_options.value))
#                 self.json_items = file.items()
#
#             except Exception:
#                 print(f'File `{self.file_selection.value}` is empty!')
#             else:
#                 self.json.value = file
#                 self.widget.append(self.json)
#
#         elif self.file_selection.value == 'TSV files':
#             try:
#                 file = pd.read_csv(self.select_options.value, sep='\t', header=None, index_col=None)
#             except Exception:
#                 print(f'File `{self.file_selection.value}` is empty!')
#             else:
#                 self.tsv.value = pn.widgets.Tabulator(file)
#                 self.widget.append(self.tsv)
#
#     @pn.depends('json.value', watch=True)
#     def _change_json_file(self):
#         #         equal, diff = verify_keys(self.json_keys, self.json.value.keys())
#         #         print(equal, diff)
#         #         print(self.json.value.values())
#         print(self.json.value.items())
#         print(self.json_keys)
#
#     #         if equal:
#     #             with open(os.path.join(self.select_options.value), 'a') as f:
#     #                 json.dump(self.json.value, f)
#     #         else:
#     #             print(f'Not saving the results; `{diff}` columns are missing')
#     def view(self):
#         return pn.Column(self.file_selection, self.widget)
#
#
# sf = ShowFiles(path='../output')
# pn.serve(sf.view())

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
