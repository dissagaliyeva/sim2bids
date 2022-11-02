required = ['NumberOfRows', 'NumberOfColumns', 'Description']

file_desc = {
    # ====================================
    #             NETWORK FOLDER
    # ====================================

    'weights': 'This is the {}SC representing the strength of connection between regions. Zeros represent unconnected '
               'areas (nxn matrix).',
    'distances': 'These are the length of myelinated fibre tracts between regions (nxn matrix).',
    'delays': 'This is the matrix of time delays between regions in physical units, calculated by the following '
              'formula: delays = distances / speed (nxn matrix).',
    'speeds': 'This is a single number or matrix of conduction speeds for the myelinated fibre tracts between regions '
              '(nxn matrix).',

    # ====================================
    #             COORD FOLDER
    # ====================================
    # MORE COMMON
    'times': 'These are the time steps of the simulated time series (nx1 vector).',
    'bold_times': 'These are the time steps of the simulated BOLD time series (nx1 vector).',
    'areas': 'This is the estimated vector each region\'s area in mm^2 (nx1 vector).',
    'cortical': 'This is the vector that distinguishes cortical (1) from subcortical (0) regions (nx1 vector).',
    'normals': 'These are the average orientation of the region represented in the connectivity matrix (nx3 matrix).',
    'hemisphere': 'The vector that distinguishes right (1) from left (0) hemisphere (nx1 vector).',

    # LESS COMMON
    'faces': 'These are the faces of cortex surface triangulation.',
    'vertices': 'These are the vertices of cortex surface triangulation.',
    'coord_map': 'This is the nxm matrix where the coordinates along rows are mapped to the coordinates along columns.',
    'vnormals': 'These are the vertices pf cortex surface triangulation (nx3 matrix).',
    'fnormals': 'These are the indices of face vertices (nx3 matrix).',
    'sensors': 'These are the cartesian coordinates of the sensors (nx3 matrix).',
    'conv': 'This is a projection matrix that is like a map bt applied as a convolution matrix.',
    'volumes': 'These are the spaces enclosed by 3d objects in m^3 (nx1 vector).',
    'cartesian2d': 'These are the generic 2D Cartesian coordinates (nx2 matrix).',
    'cartesian3d': 'These are the generic 3D Cartesian coordinates (nx3 matrix).',
    'polar2d': 'These are the generic 2D Polar coordinates (nx2 matrix).',
    'polar3d': 'These are the generic 3D Polar coordinates (nx3 matrix).',

    # ====================================
    #             SPATIAL FOLDER
    # ====================================
    'emp_fc': 'This is the empirical FC matrix for subject {}.',
    'fc': 'This is the simulated FC matrix for subject {}.',
    'spatial_map': 'These are the values projected to onto the surface, volumes or network graphs (nxm matrix).',

    # ====================================
    #          TIME SERIES FOLDER
    # ====================================
    'ts': 'This is the time series for subject {} (txn matrix).',
    'bold_ts': 'This is the time series for subject {} with BOLD monitor (txn matrix).',
    'hrf': 'These are hemodynamic response functions (HRF). The neural time series are multiplied with a HRF in order '
           'to predict fMRI time series.',
    'vars': 'This is a (stable) variable time series (txn matrix).',
    'stimuli': 'This is a stimulation time series (txn matrix).',
    'noise': 'This is the noise time series (txn matrix).',
    'spikes': 'The is the sparse format for storing spikes (txn matrix).',
    'raster': 'This is the spike raster (txn matrix).',
    'emp': 'This is the time series of the empirical data (txn matrix).',
    'events': 'This is the matrix of strings to annotate time series (txn matrix).',

    # ====================================
    #           OTHER FOLDERS
    # ====================================
    'param': 'These are the {} parameters for the {} model.',
    'eq':  'These are the equations to simulate the time series with the {} model.',
    'code': 'The source code to reproduce results.'
}

centres = {'multi-unique': ['These are the region labels which are the same for all individuals',
                            'These are the 3d coordinate centres which are unique for each individual.'],
           'multi-same': ['These are the region labels which are the same for all individuals',
                          'These are the 3d coordinate centres which are the same for all individuals.'],
           'single': ['These are the region labels for a single subject.',
                      'These are the 3d coordinate centres for a single subject.']
           }

struct = {
    'net': {'required': required, 'recommend': []},
    'coord': {'required': required,
              'recommend': ['AnatomicalLandmarkCoordinates', 'AnatomicalLandmarkCoordinateSystem',
                            'AnatomicalLandmarkCoordinateUnits',
                            'AnatomicalLandmarkCoordinateSystemDescription']},
    'ts': {'required': ['ModelEq', 'ModelParam', 'SourceCode', 'SourceCodeVersion', 'SoftwareVersion',
                        'SoftwareName', 'SoftwareRepository', 'Network'],
           'recommend': ['SamplingPeriod', 'SamplingFrequency']},
    'spatial': {'required': ['ModelEq', 'ModelParam', 'SourceCode', 'SourceCodeVersion', 'SoftwareVersion',
                             'SoftwareName', 'SoftwareRepository', 'Network'], 'recommend': ['CoordSeries']},
    'eq': {'required': [], 'recommend': ['SourceCode', 'SourceCodeVersion', 'SoftwareVersion',
                                         'SoftwareName', 'SoftwareRepository']},
    'param': {'required': ['ModelEq'], 'recommend': ['SourceCode', 'SourceCodeVersion',
                                                     'SoftwareVersion', 'SoftwareName', 'SoftwareRepository']},
    'code': {'required': [], 'recommend': ['ModelEq', 'SourceCode', 'SourceCodeVersion',
                                           'SoftwareVersion', 'SoftwareName', 'SoftwareRepository']},
    'dataset_description': {'required': ['Name', 'BIDSVersion'], 'recommend':
        ['HEDVersion', 'DatasetType', 'License', 'Authors', 'Acknowledgements', 'HowToAcknowledge',
         'Funding', 'EthicsApprovals', 'ReferencesAndLinks', 'DatasetDOI', 'GeneratedBy', 'SourceDatasets']},
    'participants': {'required': ['participant_id'], 'recommend': ['species', 'age', 'sex', 'handedness', 'strain',
                                                                   'strain_rrid']}
}


def populate_dict(dict1, shape, desc, coords=None, **kwargs):
    if shape:
        dict1['NumberOfRows'] = shape[0]
        dict1['NumberOfColumns'] = shape[1]
    dict1['Description'] = desc

    if coords:
        dict1['CoordsRows'] = coords
        dict1['CoordsColumns'] = coords

    for k, v in kwargs.items():
        dict1[k] = v

    return dict1
