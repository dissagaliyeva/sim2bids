alt = """<br>
Using the app was created to ease your computational simulation conversion! Before passing your files to the
conversion tool, make sure to <strong>run the preprocessing pipeline beforehand</strong>. We know that manually
renaming your files is too time-consuming and, let’s be honest, annoying! Please run the cell under "Preprocess data"
and follow the instructions there.

From now on we assume the files are preprocessed and ready to be used. There are several steps you need to take:

<h3>Step 1: Insert path</h3>
Go to the "Select files" tab, provide a path to your files under "Insert Path", and make sure to <strong>press "Enter"</strong>
or click on any space <strong>outside</strong> of the input box where you provided your path. If you provided the path and pressed
"Enter", but no files are shown below on the left-hand side, make sure to do it once again and/or check your
input folder to verify files exist.

<h3>Step 2: Select files</h3>
Select files you want to convert. You have three options:

<center><h4>Go back one level and select the whole folder containing the files</h4></center>
<center><img src="https://raw.githubusercontent.com/dissagaliyeva/incf/main/static/user_guide/folder.gif" width="70%"/><br></center>

<center><h4>Select all files one-by-one</h4></center>
<center><img src="https://raw.githubusercontent.com/dissagaliyeva/incf/main/static/user_guide/one-by-one.gif" width="70%"/><br></center>

<center><h4>Select-scroll the files</h4></center>
<center><img src="https://raw.githubusercontent.com/dissagaliyeva/incf/main/static/user_guide/select-scroll.gif" width="70%"/><br></center>

<h3>Step 3: Check out preliminary results</h3>
Check out the automatically generated folder structure. Don't worry, no files are generated at this stage.
The structure just shows the possible output. You might see some empty folders there, they will be removed when
the structure gets generated. This conversion follows the BEP034 specification, therefore, we need to keep the
structure as minimal as possible. For more information, check out "BEP034" above.

<h3>Step 4: Verify settings parameters </h3>
There are several settings on the left-hand side that you might consider crucial. Here's the explanation of each:

<ul>
    <li><strong>Provide output path</strong></li>
    By default, the app stores all conversion output in the local folder (on the same level as "requirements.txt"). In case
    you want to change the destination, simply provide a new path. If the folder doesn't exist, the app creates it ;)

    <li><strong>Provide a short description (max 30 chars)</strong></li>
    Here you can give the description to your files that will distinguish each simulation; it will be used in all of
    the files! For example, if you leave the description as "default", the files are going to look like this:
    <pre><code>
    |__ sub-01/
        |__ coord/
            |__ sub-01_desc-default_areas.json
            |__ sub-01_desc-default_areas.tsv
            .
            .
            .
    </code></pre>

    <li><strong>Select additional settings</strong></li>
    <ul>
        <li><strong>Traverse folders</strong></li>
        By default, all folders get traversed. For example, if you pass in a folder that has sub-folders, the app
        traverses the sub-folders as well. If you don't want that behavior, simply click on the checkbox.
        <li><strong>Autocomplete columns</strong></li>
        After file conversion, you will be able to see the generated JSON and TSV files in the "View Results" tab.
        If you specify the REQUIRED or RECOMMENDED fields, say, for "weights", then all the other "weights"
        files will inherit the same information. Columns "NumberOfRows" and "NumberOfColumns" won't be affected.
    </ul>
</ul>

<h3>Step 5: Generate the files! </h3>
If you’re happy with the possible structure and sure about the settings, click "Generate Files" button.

<h3>Step 6 (OPTIONAL): Check out the JSON/TSV conversions in the "View Results" tab </h3>

<h3>Step 7 (OPTIONAL): Check out visualizations! (TO BE IMPLEMENTED...) </h3>

"""

how_to_use = alt

preprocess = alt

supported = alt

functionality = alt

bep034 = alt
