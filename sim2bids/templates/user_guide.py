alt = """<br>
Using the app was created to ease your computational simulation appersion! Before passing your files to the
appersion tool, make sure to <strong>run the preprocessing pipeline beforehand</strong>. We know that manually
renaming your files is too time-consuming and, let’s be honest, annoying! Please run the cell under "Preprocess data"
and follow the instructions there. <br><br>

From now on we assume the files are preprocessed and ready to be used. There are several steps you need to take:

<h3>Step 1: Insert path</h3>
Go to the "Select files" tab, provide a path to your files under "Insert Path", and make sure to <strong>press "Enter"</strong>
or click on any space <strong>outside</strong> of the input box where you provided your path. If you provided the path and pressed
"Enter", but no files are shown below on the left-hand side, make sure to do it once again and/or check your
input folder to verify files exist.

<h3>Step 2: Select files</h3>
Select files you want to appert. You have three options:

<center><h4>Go back one level and select the whole folder containing the files</h4></center>
<center><img src="https://raw.githubusercontent.com/dissagaliyeva/incf/main/static/user_guide/folder.gif" width="70%"/><br></center>

<center><h4>Select all files one-by-one</h4></center>
<center><img src="https://raw.githubusercontent.com/dissagaliyeva/incf/main/static/user_guide/one-by-one.gif" width="70%"/><br></center>

<center><h4>Select-scroll the files</h4></center>
<center><img src="https://raw.githubusercontent.com/dissagaliyeva/incf/main/static/user_guide/select-scroll.gif" width="70%"/><br></center>

<h3>Step 3: Check out preliminary results</h3>
Check out the automatically generated folder structure. Don't worry, no files are generated at this stage.
The structure just shows the possible output. You might see some empty folders there, they will be removed when
the structure gets generated. This appersion follows the BEP034 specification, therefore, we need to keep the
structure as minimal as possible. For more information, check out "BEP034" above.

<h3>Step 4: Verify settings parameters </h3>
There are several settings on the left-hand side that you might consider crucial. Here's the explanation of each:

<ul>
    <li><strong>Provide output path</strong></li>
    By default, the app stores all appersion output in the local folder (on the same level as "requirements.txt"). In case
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
        After file appersion, you will be able to see the generated JSON and TSV files in the "View Results" tab.
        If you specify the REQUIRED or RECOMMENDED fields, say, for "weights", then all the other "weights"
        files will inherit the same information. Columns "NumberOfRows" and "NumberOfColumns" won't be affected.
    </ul>
</ul>

<h3>Step 5: Generate the files! </h3>
If you’re happy with the possible structure and sure about the settings, click "Generate Files" button.

<h3>Step 6 (OPTIONAL): Check out the JSON/TSV appersions in the "View Results" tab </h3>

<h3>Step 7 (OPTIONAL): Check out visualizations! (TO BE IMPLEMENTED...) </h3>

"""

how_to_use = alt

preprocess = alt

supported = alt

functionality = alt

bep034 = """
          <div class="md-content" data-md-component="content">
            <article class="md-content__inner md-typeset">



                <h1 id="computational-models"><a class="toclink" href="http://127.0.0.1:8000/en/stable/04-modality-specific-files/10-computational-models.html#computational-models">Computational Models</a></h1>
<p>Support for computational models was developed as a
<a href="https://docs.google.com/document/d/1NT1ERdL41oz3NibIFRyVQ2iR8xH-dKY-lRCB4eyVeRo/edit#heading=h.mqkmyp254xh6">BIDS Extension Proposal</a>. </p>
<h2 id="general-principles"><a class="toclink" href="http://127.0.0.1:8000/en/stable/04-modality-specific-files/10-computational-models.html#general-principles">General principles</a></h2>
<ol>
<li><strong>Short and intuitive filenames</strong>: Computational models and corresponding simulation
results are typically characterised by a large number of different parameters.
Distinguishing files on the basis of all these parameters would lead to extremely long
filenames, which are not supported by operating systems and which are hard to parse
visually.
Therefore, instead of long lists of key-value pairs to disambiguate files, the defining
characteristic of each file (or file bundle) is given through the <code>desc</code> key-value pair
in free-form, while JSON and XML files are used to exhaustively specify parameters.
Every file that contains computational model simulation results MUST have an accompanying
JSON sidecar of the same name except the suffix.
In this JSON there MUST be links to the underlying model (<code>"ModelParam"</code>) and parameters
(<code>"ModelEq</code>) files.
Note that because simulation results are not necessarily dependent on a specific subject
or space the filename keys <code>subject</code> and <code>space</code> are OPTIONAL, while <code>desc</code> is REQUIRED.</li>
<li><strong>Avoiding overspecialization and standard proliferation to increase
interoperability</strong>: With standardization efforts there are risks of overspecialization
and standard proliferation: because they (apparently) do not accommodate every use case,
there is a tendency for competing standards or substandards to arise and after a while
the market for competing standards or substandards gets messy and hard to use such that
the problem (interoperability) that the standardization tried to solve comes back in a
different form (instead of no standard there is then a flood of standards or very complex
standards).
For example: when the key-value pairs of file names are tuned to a narrow
class of software or concepts then they often cannot be practically used outside of that
specific framework.
Problematically, neural simulators often have a dedicated file format
although the underlying information to describe neural models is often very similar or
even identical.
This is in contrast to the idea of BIDS of providing a generically interoperable
specification that is independent of a specific product, concept or framework.
Therefore, instead of interpreting computational model simulation results from the
conceptual vantage point of a specific product or framework and to apperge towards a
common ground we introduce only highly <strong>generic datatypes</strong> to store computational models
and simulation results:<ul>
<li>network graphs (<code>net/</code>)</li>
<li>mathematical equations with physical interpretation (<code>eq/</code>)</li>
<li>parameters used to produce a particular result (<code>param/</code>)</li>
<li>computer code (<code>code/</code>)</li>
<li>time series data (temporal objects) (<code>ts/</code>)</li>
<li>spatial objects data (<code>spatial/</code>)</li>
<li>coordinates (<code>coord/</code>) to align <code>ts/</code>, <code>spatial/</code> and <code>net/</code> in common reference
spaces</li>
</ul>
</li>
</ol>
<p>These data types can all be expressed with</p>
<ul>
<li>tsv files</li>
<li>JSON sidecar files and</li>
<li>XML files for model equations and parameters using the
<a href="http://lems.github.io/LEMS"><strong>L</strong>ow <strong>E</strong>ntropy <strong>M</strong>odel <strong>S</strong>pecification (LEMS)</a>
format.</li>
</ul>
<p>In the following <code>n</code> refers to the number of nodes of a network graph, <code>t</code> to the number
of time points of a time series and <code>m</code> to the count of arbitrary entities like vertices,
faces, and so on.</p>
<h2 id="generic-metadata"><a class="toclink" href="http://127.0.0.1:8000/en/stable/04-modality-specific-files/10-computational-models.html#generic-metadata">Generic metadata</a></h2>
<p>These metadata keys MUST be used in all computational model JSON sidecar files.</p>
<div class="md-typeset__scrollwrap"><div class="md-typeset__table"><table>
<thead>
<tr>
<th><strong>Key name</strong></th>
<th><strong>Requirement Level</strong></th>
<th><strong>Data type</strong></th>
<th><strong>Description</strong></th>
</tr>
</thead>
<tbody>
<tr>
<td>NumberOfRows</td>
<td>REQUIRED</td>
<td><a href="https://www.w3schools.com/js/js_json_datatypes.asp">integer</a></td>
<td>Number of rows in the corresponding data file.</td>
</tr>
<tr>
<td>NumberOfColumns</td>
<td>REQUIRED</td>
<td><a href="https://www.w3schools.com/js/js_json_datatypes.asp">integer</a></td>
<td>Number of columns in the corresponding data file.</td>
</tr>
<tr>
<td>CoordsRows</td>
<td>REQUIRED</td>
<td><a href="https://www.w3schools.com/js/js_json_arrays.asp">array</a> of <a href="https://www.w3schools.com/js/js_json_datatypes.asp">strings</a> or <a href="https://www.w3schools.com/js/js_json_datatypes.asp">string</a></td>
<td>Link to <code>coord/</code> file(s) where the coordinates of each row are clarified. The  coordinates of each row are defined in the row with the same index in the linked file(s). Consequently, the number of rows must be identical to the number of rows in  the linked file(s).</td>
</tr>
<tr>
<td>CoordsColumns</td>
<td>REQUIRED</td>
<td><a href="https://www.w3schools.com/js/js_json_arrays.asp">array</a> of <a href="https://www.w3schools.com/js/js_json_datatypes.asp">strings</a> or <a href="https://www.w3schools.com/js/js_json_datatypes.asp">string</a></td>
<td>Link to <code>coord/</code> file(s) where the coordinates of each column are clarified. The  coordinates of each column are defined in the row with the same index in the linked file(s). Consequently, the number of columns must be identical to the number of rows in  the linked file(s).</td>
</tr>
<tr>
<td>Description</td>
<td>REQUIRED</td>
<td><a href="https://www.w3schools.com/js/js_json_datatypes.asp">string</a></td>
<td>Free-form natural language description.</td>
</tr>
</tbody>
</table></div></div>
<h2 id="network-graphs-net"><a class="toclink" href="http://127.0.0.1:8000/en/stable/04-modality-specific-files/10-computational-models.html#network-graphs-net">Network graphs (<code>net/</code>)</a></h2>
<p>The folder <code>net/</code> stores the graph structure of computational network models (that is, the
structural network model; not to be confused with functional networks like 'functional
connectivity', which can be an output of a computational model simulation that is stored
in the folder <code>spatial/</code>).
Graphs are stored as adjacency matrices in <code>.tsv</code> files.
Rows and columns are sorted according to <code>coord/</code> files that are linked in the JSON
sidecar files using the keys <code>"NumberOfRows"</code>, <code>"NumberOfColumns"</code>, <code>"CoordsRows"</code>,
<code>"CoordsColumns"</code>.
The minimally required information for neural network modelling is the coupling <code>weights</code>
matrix.
Note that information in <code>distances</code>, <code>delays</code> and <code>speeds</code> matrices can be
redundant so it is best practice to supply only one of them to avoid potential
ambiguity problems.</p>
<p>Template:
</p><div class="highlight"><pre id="__code_0"><span></span></button><pre><code>sub-&lt;label&gt;/
    [ses-&lt;label&gt;/]
        net/
            [sub-&lt;label&gt;][_space-&lt;label&gt;]_desc-&lt;label&gt;_delays.json
            [sub-&lt;label&gt;][_space-&lt;label&gt;]_desc-&lt;label&gt;_delays.tsv[.gz]
            [sub-&lt;label&gt;][_space-&lt;label&gt;]_desc-&lt;label&gt;_distances.json
            [sub-&lt;label&gt;][_space-&lt;label&gt;]_desc-&lt;label&gt;_distances.tsv[.gz]
            [sub-&lt;label&gt;][_space-&lt;label&gt;]_desc-&lt;label&gt;_speeds.json
            [sub-&lt;label&gt;][_space-&lt;label&gt;]_desc-&lt;label&gt;_speeds.tsv[.gz]
            [sub-&lt;label&gt;][_space-&lt;label&gt;]_desc-&lt;label&gt;_weights.json
            [sub-&lt;label&gt;][_space-&lt;label&gt;]_desc-&lt;label&gt;_weights.tsv[.gz]
</code></pre></div><p></p>
<p>Currently supported types of network graph files:</p>
<center><div class="md-typeset__scrollwrap"><div class="md-typeset__table"><table>
<thead>
<tr>
<th><strong>Name</strong></th>
<th><code>suffix</code></th>
<th><strong>Description</strong></th>
</tr>
</thead>
<tbody>
<tr>
<td>coupling weights</td>
<td><code>weights</code></td>
<td><code>nxn</code> matrix of connection weights.</td>
</tr>
<tr>
<td>coupling distances</td>
<td><code>distances</code></td>
<td><code>nxn</code> matrix of connection distances.</td>
</tr>
<tr>
<td>coupling delays</td>
<td><code>delays</code></td>
<td><code>nxn</code> matrix of connection delays.</td>
</tr>
<tr>
<td>coupling speeds</td>
<td><code>speeds</code></td>
<td><code>nxn</code> matrix of connection speeds.</td>
</tr>
</tbody>
</table></div></div></center>
<h2 id="coordinates-coord"><a class="toclink" href="http://127.0.0.1:8000/en/stable/04-modality-specific-files/10-computational-models.html#coordinates-coord">Coordinates (<code>coord/</code>)</a></h2>
<p>The files in the folder <code>coord/</code> define the spatial, respectively, the temporal
coordinates of the rows and columns in  <code>ts/</code>, <code>spatial/</code> and <code>net/</code> files.</p>
<p>Template:
</p><div class="highlight"><pre id="__code_1"><span></span><pre><code>
    [ses-&lt;label&gt;/]
        coord/
            [sub-&lt;label&gt;][_space-&lt;label&gt;]_desc-&lt;label&gt;_&lt;suffix&gt;.json
            [sub-&lt;label&gt;][_space-&lt;label&gt;]_desc-&lt;label&gt;_&lt;suffix&gt;.tsv[.gz]
</code></pre></div><p></p>
<p>The sorting of coordinates refers to the sorting of, for example,</p>
<ul>
<li>time points in time series, sampled at regular or irregular intervals (<code>ts/</code>)</li>
<li>locations of spatial objects (<code>spatial/</code>)</li>
<li>labels of network nodes (<code>net/</code>)</li>
</ul>
<p>Units (for example: <code>"s"</code>, <code>"m"</code>, <code>"ms"</code>, <code>"degrees"</code>, <code>"radians"</code>, ...) are specified in
<code>coord/</code> sidecar files using the key <code>"Units"</code>. <strong>The sorting of rows, respectively
columns, in a data file corresponds to the rows in the <code>coords/</code> files linked with the
keys <code>"CoordsColumns"</code>, respectively <code>"CoordsRows"</code>.</strong></p>
<p>Examples:</p>
<ol>
<li>The time steps in the first line (row 1) of a <code>ts/</code> file <code>&lt;ts_example&gt;_ts.tsv</code> happen
at the time specified in the first line (row 1) of a <code>coord/</code> file
<code>&lt;ts_example&gt;_times.tsv</code> that is linked from the field <code>"CoordsRows"</code> in the JSON sidecar
file <code>&lt;coord_example&gt;_ts.json</code>.
Furthermore, the labels of the nodes along columns in <code>&lt;ts_example&gt;_ts.tsv</code> may be
specified in an <code>&lt;coord_example&gt;_labels.tsv</code> file that is linked from the field
<code>"CoordsColumns"</code>.</li>
<li>The location, respectively the label, of the node corresponding to column 247 in the
file <code>net/&lt;example2&gt;_weights.tsv</code> is specified in row 247 of the linked
<code>../coord/*_nodes.json</code>, respectively <code>../coord/*_labels.json</code>, that are linked via the
key <code>"CoordsColumns"</code>.</li>
</ol>
<p>Example:
</p><div class="highlight"><pre id="__code_2"><span></span><pre><code><span class="s2">"CoordsColumns"</span><span class="err">:</span> <span class="p">[</span>
                        <span class="s2">"../coord/excoordsys_nodes.json"</span><span class="p">,</span>
                        <span class="s2">"../coord/excoordsys_labels.json"</span>
                     <span class="p">]</span>
</code></pre></div>
Currently supported types of coordinates:<p></p>
<center><div class="md-typeset__scrollwrap"><div class="md-typeset__table"><table>
<thead>
<tr>
<th><strong>Name</strong></th>
<th><code>suffix</code></th>
<th><strong>Description</strong></th>
</tr>
</thead>
<tbody>
<tr>
<td>Time points of a time series</td>
<td><code>times</code></td>
<td><code>nx1</code> vector of time points (default unit: s, seconds).  Both, sampling at regular and at irregular intervals is supported.</td>
</tr>
<tr>
<td>Locations of network node centres</td>
<td><code>nodes</code></td>
<td><code>nx3</code> matrix of cartesian coordinates.</td>
</tr>
<tr>
<td>Locations of surface vertices</td>
<td><code>vertices</code></td>
<td><code>nx3</code> matrix of cartesian coordinates.</td>
</tr>
<tr>
<td>Indices of face vertices</td>
<td><code>faces</code></td>
<td><code>nxm</code> matrix of vertex indices, referring to row indices (one-based numbering) in a corresponding <code>_vertices</code> file to form faces (triangles, rectangles, ...).</td>
</tr>
<tr>
<td>Normal vectors of vertices</td>
<td><code>vnormals</code></td>
<td><code>nx3</code> matrix of normal vectors, referring to row indices (one-based numbering) in a corresponding <code>_vertices</code> file.</td>
</tr>
<tr>
<td>Normal vectors of faces</td>
<td><code>fnormals</code></td>
<td><code>nx3</code> matrix of normal vectors, referring to row indices (one-based numbering) in a corresponding <code>_faces</code> file.</td>
</tr>
<tr>
<td>Textual identifier labels</td>
<td><code>labels</code></td>
<td><code>nxk</code> vector of strings to label the rows or columns of associated files.</td>
</tr>
<tr>
<td>Locations of sensors</td>
<td><code>sensors</code></td>
<td><code>nx3</code> matrix of cartesian coordinates.</td>
</tr>
<tr>
<td>Orientations of surfaces or vertices</td>
<td><code>orientations</code></td>
<td><code>nx3</code> matrix of unit vectors.</td>
</tr>
<tr>
<td>Mappings between coordinates</td>
<td><code>map</code></td>
<td><code>nxm</code> matrix where the coordinates along rows are mapped to the coordinates along columns. The types of coordinates are specified in sidecar JSON fields <code>"CoordsRows"</code> and <code>"CoordsColumns"</code>.</td>
</tr>
<tr>
<td>Projection matrix</td>
<td><code>app</code></td>
<td>like a <code>map</code>, but applied as appolution matrix (that is, multiplied with a <code>ts</code> or <code>spatial</code> object).</td>
</tr>
<tr>
<td>spatial extends of 2d objects</td>
<td><code>areas</code></td>
<td><code>nx1</code> matrix of areas (default unit: m<sup>2</sup>, square metre).</td>
</tr>
<tr>
<td>spaces enclosed by 3d objects</td>
<td><code>volumes</code></td>
<td><code>nx1</code> matrix of volumes (default unit: m<sup>3</sup>, cubic metre).</td>
</tr>
<tr>
<td>Generic 2d cartesian coordinates</td>
<td><code>cartesian2d</code></td>
<td><code>nx2</code> matrix of general purpose cartesian coordinates.</td>
</tr>
<tr>
<td>Generic 3d cartesian coordinates</td>
<td><code>cartesian3d</code></td>
<td><code>nx3</code> matrix of general purpose cartesian coordinates.</td>
</tr>
<tr>
<td>Generic 2d polar coordinates</td>
<td><code>polar2d</code></td>
<td><code>nx2</code> matrix of general purpose polar coordinates.</td>
</tr>
<tr>
<td>Generic 3d polar coordinates</td>
<td><code>polar3d</code></td>
<td><code>nx3</code> matrix of general purpose polar coordinates.</td>
</tr>
</tbody>
</table></div></center></div>
<h3 id="coord-specific-metadata"><a class="toclink" href="http://127.0.0.1:8000/en/stable/04-modality-specific-files/10-computational-models.html#coord-specific-metadata"><code>"coord""</code>-specific metadata</a></h3>
<div class="md-typeset__scrollwrap"><div class="md-typeset__table"><table>
<thead>
<tr>
<th><strong>Key name</strong></th>
<th><strong>Requirement Level</strong></th>
<th><strong>Data type</strong></th>
<th><strong>Description</strong></th>
</tr>
</thead>
<tbody>
<tr>
<td>Units</td>
<td>REQUIRED</td>
<td><a href="https://www.w3schools.com/js/js_json_datatypes.asp">string</a></td>
<td>Measurement units for the associated file. SI units in CMIXF formatting are RECOMMENDED (see <a href="http://127.0.0.1:8000/02-common-principles.html#units">Units</a>).</td>
</tr>
<tr>
<td>AnatomicalLandmarkCoordinates</td>
<td>RECOMMENDED</td>
<td><a href="https://www.json.org/json-en.html">object</a> of <a href="https://www.w3schools.com/js/js_json_arrays.asp">arrays</a></td>
<td>Key:value pairs of the labels and 3-D digitized locations of anatomical landmarks, interpreted following the <code>AnatomicalLandmarkCoordinateSystem</code> (for example, <code>{"NAS": [12.7,21.3,13.9], "LPA": [5.2,11.3,9.6], "RPA": [20.2,11.3,9.1]}</code>. Each array MUST contain three numeric values corresponding to x, y, and z axis of the coordinate system in that exact order.</td>
</tr>
<tr>
<td>AnatomicalLandmarkCoordinateSystem</td>
<td>RECOMMENDED</td>
<td><a href="https://www.w3schools.com/js/js_json_datatypes.asp">string</a></td>
<td>Defines the coordinate system for the anatomical landmarks. See <a href="http://127.0.0.1:8000/99-appendices/08-coordinate-systems.html">Appendix VIII</a> for a list of restricted keywords for coordinate systems. If <code>"Other"</code>, provide definition of the coordinate system in <code>AnatomicalLandmarkCoordinateSystemDescription</code>.</td>
</tr>
<tr>
<td>AnatomicalLandmarkCoordinateUnits</td>
<td>RECOMMENDED</td>
<td><a href="https://www.w3schools.com/js/js_json_datatypes.asp">string</a></td>
<td>Units of the coordinates of <code>AnatomicalLandmarkCoordinateSystem</code>. MUST be <code>"m"</code>, <code>"cm"</code>, or <code>"mm"</code>.</td>
</tr>
<tr>
<td>AnatomicalLandmarkCoordinateSystemDescription</td>
<td>RECOMMENDED</td>
<td><a href="https://www.w3schools.com/js/js_json_datatypes.asp">string</a></td>
<td>Free-form text description of the coordinate system. May also include a link to a documentation page or paper describing the system in greater detail.</td>
</tr>
</tbody>
</table></div></div>
<h2 id="time-series-data-ts"><a class="toclink" href="http://127.0.0.1:8000/en/stable/04-modality-specific-files/10-computational-models.html#time-series-data-ts">Time series data (<code>ts/</code>)</a></h2>
<p>The folder <code>ts/</code> stores time series.
For example, if a parameter space exploration was performed all resulting time series are
stored in this folder and their corresponding JSON sidecar files specify which <code>eq</code>,
<code>params</code>, <code>net</code> and <code>coord</code> files were used to produce the result.
The temporal dimension is always stored along rows and the entities that vary in time are
stored along columns.
The corresponding time points are defined in a <code>coord/</code> file that is linked in a sidecar
JSON with the exact same name as the time series file except for the file type suffix.
Every <code>ts/*_desc-&lt;label&gt;*_&lt;suffix&gt;.tsv</code> time series file MUST have an accompanying
sidecar JSON <code>ts/*_desc-&lt;label&gt;*_&lt;suffix&gt;.json</code> that links to the LEMS XML files that
contain the underlying model equations (<code>eq/</code>) and parameters (<code>params/</code>) using the keys
<code>"ModelEq"</code> and <code>"ModelParam"</code>.</p>
<p>Both, <code>ts/</code> and <code>spatial/</code> files can be grouped into file bundles using the filename key
entity <code>series</code>. For example, a series of <code>ts</code> files can be used to store a longer,
discontinuous time series in smaller files:
</p><div class="highlight"><pre id="__code_3"><span></span><pre><code>    ts/desc_Stimulustest4_series_00001_stimuli.tsv,
    ts/desc_Stimulustest4_series_00002_stimuli.tsv,
    ts/desc_Stimulustest4_series_00003_stimuli.tsv,
    ...
    ts/desc_Stimulustest4_series_09876_stimuli.tsv
</code></pre></div>
The coordinates of the series elements MUST be specified with the metadata key
<code>"CoordsSeries"</code>.<p></p>
<p>Note that the filetype <code>"spikes"</code> is the only data file filetype that allows jagged 2d
arrays: columns can have different lengths for efficient (sparse) storage of spike times.
Each row contains only the indices of the units that spiked at the times defined in the
linked <code>"CoordsRows"</code> file.
In contrast, the arrays in the filetype <code>"raster"</code> have a fixed dimensionality (that is,
no sparse storage).
A value of <code>0</code> in the array element <code>a&lt;sub&gt;ij&lt;/sub&gt;</code> indicates no spike of unit <code>j</code> at
time index <code>i</code>, while a value of <code>1</code> indicates a spike by that unit at the indexed time
(the time can be obtained from the linked <code>coords/</code> file).</p>
<p>Template:
</p><div class="highlight"><pre id="__code_4"><span></span><pre><code>sub-&lt;label&gt;/
    [ses-&lt;label&gt;/]
        ts/
            [sub-&lt;label&gt;][_space-&lt;label&gt;]_desc-&lt;label&gt;[_series-&lt;label&gt;]_&lt;suffix&gt;.json
            [sub-&lt;label&gt;][_space-&lt;label&gt;]_desc-&lt;label&gt;[_series-&lt;label&gt;]_&lt;suffix&gt;.tsv[.gz]
</code></pre></div><p></p>
<p>Currently supported types of time series:</p>
<center><div class="md-typeset__scrollwrap"><div class="md-typeset__table"><table>
<thead>
<tr>
<th><strong>Name</strong></th>
<th><code>suffix</code></th>
<th><strong>Description</strong></th>
</tr>
</thead>
<tbody>
<tr>
<td>Model simulation time series</td>
<td><code>vars</code></td>
<td><code>txn</code> matrix of (state) variable time series. The labels in the <code>coord/*_labels.tsv</code> file linked in the sidecar <code>"CoordsColumns"</code> field MUST be identical to the name of the <code>StateVariable</code> / <code>DerivedVariable</code> in the corresponding LEMS XML model file.</td>
</tr>
<tr>
<td>Stimulation time series</td>
<td><code>stimuli</code></td>
<td><code>txn</code> matrix of stimulation time series.</td>
</tr>
<tr>
<td>Noise time series</td>
<td><code>noise</code></td>
<td><code>txn</code> matrix of noise time series.</td>
</tr>
<tr>
<td>Spike timings</td>
<td><code>spikes</code></td>
<td><code>sparse</code> format for storing spikes. Variable number of columns in each row allowed.</td>
</tr>
<tr>
<td>Spike raster</td>
<td><code>raster</code></td>
<td><code>txn</code> spike raster.</td>
</tr>
<tr>
<td>Empirical timeseries</td>
<td><code>emp</code></td>
<td><code>txn</code> matrix of empirical time series.</td>
</tr>
<tr>
<td>Generic time series container</td>
<td><code>ts</code></td>
<td><code>txn</code> matrix of generic time series.</td>
</tr>
<tr>
<td>Events, labels, annotations</td>
<td><code>events</code></td>
<td><code>txn</code> matrix of strings to annotate time series.</td>
</tr>
</tbody>
</table></div></div>
<h3 id="ts-specific-metadata"><a class="toclink" href="http://127.0.0.1:8000/en/stable/04-modality-specific-files/10-computational-models.html#ts-specific-metadata"><code>"ts"</code>-specific metadata</a></h3>
<p>While it is possible to use <code>coords/*_times.tsv</code> files to specify the time points of a
time series, it is often more appenient to just specify the
<code>"SamplingPeriod"</code> or the <code>"SamplingFrequency"</code> (works only for equidistant sampling).</p>
<div class="md-typeset__scrollwrap"><div class="md-typeset__table"><table>
<thead>
<tr>
<th><strong>Key name</strong></th>
<th><strong>Requirement Level</strong></th>
<th><strong>Data type</strong></th>
<th><strong>Description</strong></th>
</tr>
</thead>
<tbody>
<tr>
<td>ModelEq</td>
<td>REQUIRED</td>
<td><a href="https://www.w3schools.com/js/js_json_arrays.asp">array</a> of <a href="https://www.w3schools.com/js/js_json_datatypes.asp">strings</a> or <a href="https://www.w3schools.com/js/js_json_datatypes.asp">string</a></td>
<td>Reference to one or more <code>eq/*_eq.xml</code> file(s) where the computational model is  specified in <a href="http://lems.github.io/LEMS">LEMS</a>.</td>
</tr>
<tr>
<td>ModelParam</td>
<td>REQUIRED</td>
<td><a href="https://www.w3schools.com/js/js_json_datatypes.asp">string</a></td>
<td>Reference to exactly one <code>param/*_param.xml</code> file where the computational model is  specified in <a href="http://lems.github.io/LEMS">LEMS</a>.</td>
</tr>
<tr>
<td>SourceCode</td>
<td>REQUIRED</td>
<td><a href="https://www.w3schools.com/js/js_json_arrays.asp">array</a> of <a href="https://www.w3schools.com/js/js_json_datatypes.asp">strings</a> or <a href="https://www.w3schools.com/js/js_json_datatypes.asp">string</a></td>
<td>Either <a href="http://127.0.0.1:8000/02-common-principles.html#uniform-resource-indicator">URI</a> to a publicly accessible repository or reference to files in <code>code/*_eq.xml</code> where the computational  code used to produce the simulation result is provided.</td>
</tr>
<tr>
<td>SourceCodeVersion</td>
<td>REQUIRED</td>
<td><a href="https://www.w3schools.com/js/js_json_datatypes.asp">string</a></td>
<td>Version of the <code>"SourceCode"</code>.</td>
</tr>
<tr>
<td>SoftwareVersion</td>
<td>REQUIRED</td>
<td><a href="https://www.w3schools.com/js/js_json_datatypes.asp">string</a></td>
<td>Version of the software that was used.</td>
</tr>
<tr>
<td>SoftwareName</td>
<td>REQUIRED</td>
<td><a href="https://www.w3schools.com/js/js_json_arrays.asp">array</a> of <a href="https://www.w3schools.com/js/js_json_datatypes.asp">strings</a> or <a href="https://www.w3schools.com/js/js_json_datatypes.asp">string</a></td>
<td>Name of the software that was used.</td>
</tr>
<tr>
<td>SoftwareRepository</td>
<td>REQUIRED</td>
<td><a href="https://www.w3schools.com/js/js_json_arrays.asp">array</a> of <a href="https://www.w3schools.com/js/js_json_datatypes.asp">strings</a> or <a href="https://www.w3schools.com/js/js_json_datatypes.asp">string</a></td>
<td>Repository where executable software is hosted (for example, Docker Hub).</td>
</tr>
<tr>
<td>Network</td>
<td>REQUIRED</td>
<td><a href="https://www.w3schools.com/js/js_json_arrays.asp">array</a> of <a href="https://www.w3schools.com/js/js_json_datatypes.asp">strings</a> or <a href="https://www.w3schools.com/js/js_json_datatypes.asp">string</a></td>
<td>Reference to the network graph file(s) in <code>net/</code> that were used to produce the  simulation result.</td>
</tr>
<tr>
<td>SamplingPeriod</td>
<td>RECOMMENDED</td>
<td><a href="https://www.w3schools.com/js/js_json_datatypes.asp">number</a></td>
<td>Sampling period (in s) of the time points of the corresponding time series.</td>
</tr>
<tr>
<td>SamplingFrequency</td>
<td>RECOMMENDED</td>
<td><a href="https://www.w3schools.com/js/js_json_datatypes.asp">number</a></td>
<td>Sampling frequency (in Hz) of all the data in the recording, regardless of their type (for example, <code>2400</code>).</td>
</tr>
</tbody>
</table></div></center></div>
<h2 id="spatial-data-spatial"><a class="toclink" href="http://127.0.0.1:8000/en/stable/04-modality-specific-files/10-computational-models.html#spatial-data-spatial">Spatial data (<code>spatial/</code>)</a></h2>
<p>The folder <code>spatial/</code> stores all kinds of spatial entities like</p>
<ul>
<li>functional connectivity matrices and more generic</li>
<li>maps of values projected onto surfaces or network graphs.</li>
</ul>
<p>The coordinates corresponding to rows and columns are defined in a <code>coord/</code> file,
linked in a sidecar JSON.
Every <code>spatial/*_desc-&lt;label&gt;*_&lt;suffix&gt;.tsv</code> data file MUST have an accompanying sidecar
JSON <code>spatial/*_desc-&lt;label&gt;*_&lt;suffix&gt;.json</code> that links to the LEMS XML files that
contain the underlying model equations (<code>eq/</code>) and parameters (<code>params/</code>) using the keys
<code>"ModelEq"</code> and <code>"ModelParam"</code>.</p>
<p>Both, <code>ts/</code> and <code>spatial/</code> files can be grouped into file bundles using the filename key
entity <code>series</code>. For example, a series of FC matrices can be used to store functional
connectivity dynamics matrices over time:
</p><div class="highlight"><pre id="__code_5"><span></span><pre><code>    spatial/desc_FCDtest1_series_00001_fc.tsv,
    spatial/desc_FCDtest1_series_00002_fc.tsv,
    spatial/desc_FCDtest1_series_00003_fc.tsv,
    ...
    spatial/desc_FCDtest1_series_00300_fc.tsv
</code></pre></div>
The coordinates of the series elements MUST be specified with the metadata key
<code>"CoordsSeries"</code>.<p></p>
<p>Template:
</p><div class="highlight"><pre id="__code_6"><span></span><pre><code>sub-&lt;label&gt;/
    [ses-&lt;label&gt;/]
        spatial/
            [sub-&lt;label&gt;][_space-&lt;label&gt;]_desc-&lt;label&gt;[_series-&lt;label&gt;]_fc.json
            [sub-&lt;label&gt;][_space-&lt;label&gt;]_desc-&lt;label&gt;[_series-&lt;label&gt;]_fc.tsv[.gz]
            [sub-&lt;label&gt;][_space-&lt;label&gt;]_desc-&lt;label&gt;[_series-&lt;label&gt;]_map.json
            [sub-&lt;label&gt;][_space-&lt;label&gt;]_desc-&lt;label&gt;[_series-&lt;label&gt;]_map.tsv[.gz]
</code></pre></div><p></p>
<p>Currently supported types of spatial objects:</p>
<center><div class="md-typeset__scrollwrap"><div class="md-typeset__table"><table>
<thead>
<tr>
<th><strong>Name</strong></th>
<th><code>suffix</code></th>
<th><strong>Description</strong></th>
</tr>
</thead>
<tbody>
<tr>
<td>Values projected onto surfaces, volumes or network graphs</td>
<td><code>map</code></td>
<td><code>nxm</code> matrix of values. Rows/cols correspond to spatial objects defined by <code>/coords</code></td>
</tr>
<tr>
<td>Functional connectivity matrix</td>
<td><code>fc</code></td>
<td><code>nxn</code> matrix</td>
</tr>
</tbody>
</table></div></div>
<h3 id="spatial-specific-metadata"><a class="toclink" href="http://127.0.0.1:8000/en/stable/04-modality-specific-files/10-computational-models.html#spatial-specific-metadata"><code>"spatial"</code>-specific metadata</a></h3>
<div class="md-typeset__scrollwrap"><div class="md-typeset__table"><table>
<thead>
<tr>
<th><strong>Key name</strong></th>
<th><strong>Requirement Level</strong></th>
<th><strong>Data type</strong></th>
<th><strong>Description</strong></th>
</tr>
</thead>
<tbody>
<tr>
<td>ModelEq</td>
<td>REQUIRED</td>
<td><a href="https://www.w3schools.com/js/js_json_arrays.asp">array</a> of <a href="https://www.w3schools.com/js/js_json_datatypes.asp">strings</a> or <a href="https://www.w3schools.com/js/js_json_datatypes.asp">string</a></td>
<td>Reference to one or more <code>eq/*_eq.xml</code> file(s) where the computational model is  specified in <a href="http://lems.github.io/LEMS">LEMS</a>.</td>
</tr>
<tr>
<td>ModelParam</td>
<td>REQUIRED</td>
<td><a href="https://www.w3schools.com/js/js_json_datatypes.asp">string</a></td>
<td>Reference to exactly one <code>param/*_param.xml</code> file where the computational model is  specified in <a href="http://lems.github.io/LEMS">LEMS</a>.</td>
</tr>
<tr>
<td>SourceCode</td>
<td>REQUIRED</td>
<td><a href="https://www.w3schools.com/js/js_json_arrays.asp">array</a> of <a href="https://www.w3schools.com/js/js_json_datatypes.asp">strings</a> or <a href="https://www.w3schools.com/js/js_json_datatypes.asp">string</a></td>
<td>Either <a href="http://127.0.0.1:8000/02-common-principles.html#uniform-resource-indicator">URI</a> to a publicly accessible repository or reference to files in <code>code/*_eq.xml</code> where the computational  code used to produce the simulation result is provided.</td>
</tr>
<tr>
<td>SourceCodeVersion</td>
<td>REQUIRED</td>
<td><a href="https://www.w3schools.com/js/js_json_datatypes.asp">string</a></td>
<td>Version of the <code>"SourceCode"</code>.</td>
</tr>
<tr>
<td>SoftwareVersion</td>
<td>REQUIRED</td>
<td><a href="https://www.w3schools.com/js/js_json_datatypes.asp">string</a></td>
<td>Version of the software that was used.</td>
</tr>
<tr>
<td>SoftwareName</td>
<td>REQUIRED</td>
<td><a href="https://www.w3schools.com/js/js_json_arrays.asp">array</a> of <a href="https://www.w3schools.com/js/js_json_datatypes.asp">strings</a> or <a href="https://www.w3schools.com/js/js_json_datatypes.asp">string</a></td>
<td>Name of the software that was used.</td>
</tr>
<tr>
<td>SoftwareRepository</td>
<td>REQUIRED</td>
<td><a href="https://www.w3schools.com/js/js_json_arrays.asp">array</a> of <a href="https://www.w3schools.com/js/js_json_datatypes.asp">strings</a> or <a href="https://www.w3schools.com/js/js_json_datatypes.asp">string</a></td>
<td>Repository where executable software is hosted (for example, Docker Hub).</td>
</tr>
<tr>
<td>Network</td>
<td>REQUIRED</td>
<td><a href="https://www.w3schools.com/js/js_json_arrays.asp">array</a> of <a href="https://www.w3schools.com/js/js_json_datatypes.asp">strings</a> or <a href="https://www.w3schools.com/js/js_json_datatypes.asp">string</a></td>
<td>Reference to the network graph file(s) in <code>net/</code> that were used to produce the  simulation result.</td>
</tr>
<tr>
<td>CoordsSeries</td>
<td>RECOMMENDED</td>
<td><a href="https://www.w3schools.com/js/js_json_arrays.asp">array</a> of <a href="https://www.w3schools.com/js/js_json_datatypes.asp">strings</a> or <a href="https://www.w3schools.com/js/js_json_datatypes.asp">string</a></td>
<td>Link to <code>coord/</code> file(s) where the coordinates of each series file are clarified. The  coordinates of each series file are defined in the row with the same index in the linked file(s). Consequently, the number of series files must be identical to the number of  rows in the linked file(s).</td>
</tr>
</tbody>
</table></div></center></div>
<h2 id="model-equations-eq"><a class="toclink" href="http://127.0.0.1:8000/en/stable/04-modality-specific-files/10-computational-models.html#model-equations-eq">Model equations (<code>eq/</code>)</a></h2>
<p>Equation and parameter files have a special role among the used file formats, because
they belong to the only file type that uses XML syntax and a format that is defined
outside of BIDS.
Model equations and parameterizations MUST be specified using the
<a href="http://lems.github.io/LEMS">LEMS</a> language.
LEMS provides a compact, minimally redundant, human-readable, human-writable, declarative
way of expressing models of physical systems.
<a href="https://github.com/LEMS/pylems">PyLEMS</a> is a Python implementation of the LEMS language
that can both parse and simulate existing LEMS models and provides an API in Python for
reading, modifying and writing LEMS files.
See the
<a href="https://pubmed.ncbi.nlm.nih.gov/25309419/">original publication introducing LEMS</a>,
and its <a href="http://lems.github.io/LEMS">repository</a> with examples for more information.</p>
<p>A basic principle of LEMS is to separate equations and parameters such that the equations
need only be stated once and can then be reused with different parameterizations.
Therefore, every <code>ts/</code> and <code>spatial/</code> object MUST reference the LEMS model XML(s) using
the keyword <code>"ModelEq"</code> and, furthermore, the LEMS XML that contains the parameters
that were used to produce the simulation result using the keyword <code>"ModelParam"</code>.</p>
<p>Template:
</p><div class="highlight"><pre id="__code_7"><span></span><pre><code>sub-&lt;label&gt;/
    [ses-&lt;label&gt;/]
        eq/
            desc-&lt;label&gt;_eq.json
            desc-&lt;label&gt;_eq.xml
</code></pre></div><p></p>
<h3 id="eq-specific-metadata"><a class="toclink" href="http://127.0.0.1:8000/en/stable/04-modality-specific-files/10-computational-models.html#eq-specific-metadata"><code>"eq"</code>-specific metadata</a></h3>
<div class="md-typeset__scrollwrap"><div class="md-typeset__table"><table>
<thead>
<tr>
<th><strong>Key name</strong></th>
<th><strong>Requirement Level</strong></th>
<th><strong>Data type</strong></th>
<th><strong>Description</strong></th>
</tr>
</thead>
<tbody>
<tr>
<td>SourceCode</td>
<td>RECOMMENDED</td>
<td><a href="https://www.w3schools.com/js/js_json_arrays.asp">array</a> of <a href="https://www.w3schools.com/js/js_json_datatypes.asp">strings</a> or <a href="https://www.w3schools.com/js/js_json_datatypes.asp">string</a></td>
<td>Either <a href="http://127.0.0.1:8000/02-common-principles.html#uniform-resource-indicator">URI</a> to a publicly accessible repository or reference to files in <code>code/*_eq.xml</code> where the computational  code used to produce the simulation result is provided.</td>
</tr>
<tr>
<td>SourceCodeVersion</td>
<td>RECOMMENDED</td>
<td><a href="https://www.w3schools.com/js/js_json_datatypes.asp">string</a></td>
<td>Version of the <code>"SourceCode"</code>.</td>
</tr>
<tr>
<td>SoftwareVersion</td>
<td>RECOMMENDED</td>
<td><a href="https://www.w3schools.com/js/js_json_datatypes.asp">string</a></td>
<td>Version of the software that was used.</td>
</tr>
<tr>
<td>SoftwareName</td>
<td>RECOMMENDED</td>
<td><a href="https://www.w3schools.com/js/js_json_arrays.asp">array</a> of <a href="https://www.w3schools.com/js/js_json_datatypes.asp">strings</a> or <a href="https://www.w3schools.com/js/js_json_datatypes.asp">string</a></td>
<td>Name of the software that was used.</td>
</tr>
<tr>
<td>SoftwareRepository</td>
<td>RECOMMENDED</td>
<td><a href="https://www.w3schools.com/js/js_json_arrays.asp">array</a> of <a href="https://www.w3schools.com/js/js_json_datatypes.asp">strings</a> or <a href="https://www.w3schools.com/js/js_json_datatypes.asp">string</a></td>
<td>Repository where executable software is hosted (for example, Docker Hub).</td>
</tr>
</tbody>
</table></div></div>
<h2 id="model-parameters-param"><a class="toclink" href="http://127.0.0.1:8000/en/stable/04-modality-specific-files/10-computational-models.html#model-parameters-param">Model parameters (<code>param/</code>)</a></h2>
<p>Every <code>ts/</code> and <code>spatial/</code> object MUST reference the LEMS model XML(s) using
the keyword <code>"ModelEq"</code> and, furthermore, the LEMS XML that contains the parameters
that were used to produce the simulation result using the keyword <code>"ModelParam"</code>.</p>
<p>Template:
</p><div class="highlight"><pre id="__code_8"><span></span><pre><code>sub-&lt;label&gt;/
    [ses-&lt;label&gt;/]
        param/
            desc-&lt;label&gt;_param.json
            desc-&lt;label&gt;_param.xml
</code></pre></div><p></p>
<h3 id="param-specific-metadata"><a class="toclink" href="http://127.0.0.1:8000/en/stable/04-modality-specific-files/10-computational-models.html#param-specific-metadata"><code>"param"</code>-specific metadata</a></h3>
<div class="md-typeset__scrollwrap"><div class="md-typeset__table"><table>
<thead>
<tr>
<th><strong>Key name</strong></th>
<th><strong>Requirement Level</strong></th>
<th><strong>Data type</strong></th>
<th><strong>Description</strong></th>
</tr>
</thead>
<tbody>
<tr>
<td>ModelEq</td>
<td>REQUIRED</td>
<td><a href="https://www.w3schools.com/js/js_json_arrays.asp">array</a> of <a href="https://www.w3schools.com/js/js_json_datatypes.asp">strings</a> or <a href="https://www.w3schools.com/js/js_json_datatypes.asp">string</a></td>
<td>Reference to one or more <code>eq/*_eq.xml</code> file(s) where the computational model is  specified in <a href="http://lems.github.io/LEMS">LEMS</a>.</td>
</tr>
<tr>
<td>SourceCode</td>
<td>RECOMMENDED</td>
<td><a href="https://www.w3schools.com/js/js_json_arrays.asp">array</a> of <a href="https://www.w3schools.com/js/js_json_datatypes.asp">strings</a> or <a href="https://www.w3schools.com/js/js_json_datatypes.asp">string</a></td>
<td>Either <a href="http://127.0.0.1:8000/02-common-principles.html#uniform-resource-indicator">URI</a> to a publicly accessible repository or reference to files in <code>code/*_eq.xml</code> where the computational  code used to produce the simulation result is provided.</td>
</tr>
<tr>
<td>SourceCodeVersion</td>
<td>RECOMMENDED</td>
<td><a href="https://www.w3schools.com/js/js_json_datatypes.asp">string</a></td>
<td>Version of the <code>"SourceCode"</code>.</td>
</tr>
<tr>
<td>SoftwareVersion</td>
<td>RECOMMENDED</td>
<td><a href="https://www.w3schools.com/js/js_json_datatypes.asp">string</a></td>
<td>Version of the software that was used.</td>
</tr>
<tr>
<td>SoftwareName</td>
<td>RECOMMENDED</td>
<td><a href="https://www.w3schools.com/js/js_json_arrays.asp">array</a> of <a href="https://www.w3schools.com/js/js_json_datatypes.asp">strings</a> or <a href="https://www.w3schools.com/js/js_json_datatypes.asp">string</a></td>
<td>Name of the software that was used.</td>
</tr>
<tr>
<td>SoftwareRepository</td>
<td>RECOMMENDED</td>
<td><a href="https://www.w3schools.com/js/js_json_arrays.asp">array</a> of <a href="https://www.w3schools.com/js/js_json_datatypes.asp">strings</a> or <a href="https://www.w3schools.com/js/js_json_datatypes.asp">string</a></td>
<td>Repository where executable software is hosted (for example, Docker Hub).</td>
</tr>
</tbody>
</table></div></div>
<h2 id="computer-code-code"><a class="toclink" href="http://127.0.0.1:8000/en/stable/04-modality-specific-files/10-computational-models.html#computer-code-code">Computer code (<code>code/</code>)</a></h2>
<p>Computer code involves "source code" (human-readable standard programming language) and
"machine code" (executable program).
Every BIDS dataset that contains simulation results <strong>MUST</strong> either directly store the
<strong>source code</strong> that was used to produce the result in this folder or link to a long-term
repository where it is stored using the field <code>"SourceCode"</code>.
Code can be in an arbitrary language, but MUST be versioned.
Furthermore, the
<strong>machine code</strong>, that is, the executable deployment of that source code used to produce
the result <strong>MUST</strong> be linked using the fields <code>"SoftwareName"</code>, <code>"SoftwareVersion"</code> and
<code>"SoftwareRepository"</code>.
Like in the case of source code, machine code can be either provided in this folder or in
a publicly-accessible repository.
It is preferred that deployments of the code exist in the form of
platform-independent self-contained container images (including the entire necessary
computational environment).</p>
<p>Template:
</p><div class="highlight"><pre id="__code_9"><span></span><pre><code>sub-&lt;label&gt;/
    [ses-&lt;label&gt;/]
        code/
            desc-&lt;label&gt;_code.&lt;extension&gt;
            desc-&lt;label&gt;_code.json
</code></pre></div><p></p>
<h3 id="code-specific-metadata"><a class="toclink" href="http://127.0.0.1:8000/en/stable/04-modality-specific-files/10-computational-models.html#code-specific-metadata"><code>"code"</code>-specific metadata</a></h3>
<div class="md-typeset__scrollwrap"><div class="md-typeset__table"><table>
<thead>
<tr>
<th><strong>Key name</strong></th>
<th><strong>Requirement Level</strong></th>
<th><strong>Data type</strong></th>
<th><strong>Description</strong></th>
</tr>
</thead>
<tbody>
<tr>
<td>SourceCode</td>
<td>RECOMMENDED</td>
<td><a href="https://www.w3schools.com/js/js_json_arrays.asp">array</a> of <a href="https://www.w3schools.com/js/js_json_datatypes.asp">strings</a> or <a href="https://www.w3schools.com/js/js_json_datatypes.asp">string</a></td>
<td>Either <a href="http://127.0.0.1:8000/02-common-principles.html#uniform-resource-indicator">URI</a> to a publicly accessible repository or reference to files in <code>code/*_eq.xml</code> where the computational  code used to produce the simulation result is provided.</td>
</tr>
<tr>
<td>SourceCodeVersion</td>
<td>RECOMMENDED</td>
<td><a href="https://www.w3schools.com/js/js_json_datatypes.asp">string</a></td>
<td>Version of the <code>"SourceCode"</code>.</td>
</tr>
<tr>
<td>SoftwareVersion</td>
<td>RECOMMENDED</td>
<td><a href="https://www.w3schools.com/js/js_json_datatypes.asp">string</a></td>
<td>Version of the software that was used.</td>
</tr>
<tr>
<td>SoftwareName</td>
<td>RECOMMENDED</td>
<td><a href="https://www.w3schools.com/js/js_json_arrays.asp">array</a> of <a href="https://www.w3schools.com/js/js_json_datatypes.asp">strings</a> or <a href="https://www.w3schools.com/js/js_json_datatypes.asp">string</a></td>
<td>Name of the software that was used.</td>
</tr>
<tr>
<td>SoftwareRepository</td>
<td>RECOMMENDED</td>
<td><a href="https://www.w3schools.com/js/js_json_arrays.asp">array</a> of <a href="https://www.w3schools.com/js/js_json_datatypes.asp">strings</a> or <a href="https://www.w3schools.com/js/js_json_datatypes.asp">string</a></td>
<td>Repository where executable software is hosted (for example, Docker Hub).</td>
</tr>
<tr>
<td>ModelEq</td>
<td>RECOMMENDED</td>
<td><a href="https://www.w3schools.com/js/js_json_arrays.asp">array</a> of <a href="https://www.w3schools.com/js/js_json_datatypes.asp">strings</a> or <a href="https://www.w3schools.com/js/js_json_datatypes.asp">string</a></td>
<td>Reference to one or more <code>eq/*_eq.xml</code> file(s) where the computational model is  specified in <a href="http://lems.github.io/LEMS">LEMS</a>.</td>
</tr>
</tbody>
</table></div></div>
"""
