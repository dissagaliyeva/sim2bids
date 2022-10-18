required = ['NumberOfRows', 'NumberOfColumns', 'CoordsRows', 'CoordsColumns', 'Description']

file_desc = {
    'weights': 'This is the SC representing the strength of connection between regions. Zeros represent unconnected '
               'areas (nxn matrix).',
    'distances': 'These are the length of myelinated fibre tracts between regions (nxn matrix).',
    'delays': 'This is the matrix of time delays between regions in physical units, calculated by the following '
              'formula: delays = distances / speed (nxn matrix).',
    'speeds': 'This is a single number or matrix of conduction speeds for the myelinated fibre tracts between regions '
              '(nxn matrix).',
    'times': 'These are the time steps of the simulated time series (nx1 vector).',
    'bold_times': 'These are the time steps of the simulated BOLD time series (nx1 vector).',
    'ts': 'This is the time series for subject {} (txn matrix).',
    'bold_ts': 'This is the time series for subject {} with BOLD monitor (txn matrix).',
    'emp_fc': 'This is the empirical FC matrix for subject {}.',
    'fc': 'This is the simulated FC matrix for subject {}.',
    'areas': 'This is the estimated vector each region’s area in mm^2 (nx1 vector).',
    'cortical': 'This is the vector that distinguishes cortical (1) from subcortical (0) regions (nx1 vector).',
    'normals': 'These are the average normal vectors of the dipoles (regions).',
    'faces': 'These are the faces of cortex surface triangulation.',
    'vertices': 'These are the vertices of cortex surface triangulation.',
    'hemisphere': 'The vector that distinguishes right (1) from left (0) hemisphere.',
    'map': 'This is the nxm matrix where the coordinates along rows are mapped to the coordinates along columns.',
    'hrf': 'These are hemodynamic response functions (HRF). The neural time series are multiplied with a HRF in order '
           'to predict fMRI time series.'
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
    'coord': {'required': ['Units'],
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
    dict1['NumberOfRows'] = shape[0]
    dict1['NumberOfColumns'] = shape[1]
    dict1['Description'] = desc

    if coords:
        dict1['CoordsRows'] = coords
        dict1['CoordsColumns'] = coords

    for k, v in kwargs.items():
        dict1[k] = v

    return dict1
