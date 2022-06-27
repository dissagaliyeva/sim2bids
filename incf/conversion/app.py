import os
import param
import panel as pn
# from incf import defaults


# class App(param.Parameterized):
#     pass


# class Markdown(param.Parameterized):
#


class GetStarted(param.Parameterized):
    # input file selector
    inp_fls = param.Parameter()
    

    # button to generate files
    gen_btn = pn.widgets.Button(name='Generate files',
                                button_type='primary')

    # markdown to show generated files
    gen_txt = param.String()

#     def __init__(self, dir_path, **params):
#         self.file_selector = 
#         self.text = pn.widgets.StaticText()
#         self.md = pn.pane.Markdown(GET_STARTED)


    @pn.depends('file_selector.value', watch=True)
    def _parse_file_selector(self):
        value = self.inp_fls.value
        fname = self.inp_fls.filename

    def view(self):
        return pn.Column(
            self.md,
            self.inp_fls,
            '### Generated folder structure',
            self.gen_txt,
            self.gen_btn
        )




GET_STARTED = """
## Welcome!
Here you can select the folder(s) that you want to transform. Beware that we are using recursive walk to select all the content available in the specified folder. That means if the folder contains a sub-folder, we will transform the content if it falls into the accepted file formats.
Below you will see the generated folder with content as specified at [BIDS Computational Model Specification](https://docs.google.com/document/d/1NT1ERdL41oz3NibIFRyVQ2iR8xH-dKY-lRCB4eyVeRo/edit?usp=sharing). If you are happy with the results, press `Transform Files` button at the bottom of the screen. We will not start generation until you press the button below.
"""






















