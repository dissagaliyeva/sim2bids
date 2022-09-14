required = ['NumberOfRows', 'NumberOfColumns', 'CoordsRows', 'CoordsColumns', 'Description']

file_desc = {
    'weights': 'The Structural Connectivity (SC) that contains the connectome.',
    'distances': 'The distances between areas.',
    'times': 'Time series of the simulated time series.',
    'ts': 'Time series of the simulated time series.',
    'bold': 'This is the time series for subject {} with BOLD monitor.',
    'spatial': 'This is the time series.',
    'bold_times': 'This is the time series for subject {} with BOLD monitor.'
}

centres = {'multi-unique': ['These are the region labels which are unique for each individual.',
                            'These are the 3d coordinate centres which are unique for each individual.'],
           'multi-same': ['These are the region labels which are the same for all individuals.',
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
