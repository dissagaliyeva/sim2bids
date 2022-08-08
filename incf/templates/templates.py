from collections import OrderedDict

struct = {'coord': {'required': ['Units'],
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
          'code': {'required': [], 'recommend': ['ModelEq', 'ModelParam', 'SourceCode', 'SourceCodeVersion',
                                                 'SoftwareVersion', 'SoftwareName', 'SoftwareRepository']}, }

required = ['NumberOfRows', 'NumberOfColumns', 'CoordsRows', 'CoordsColumns', 'Description']


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

#
# JSON_template = OrderedDict({
#     "NumberOfRows": 0,
#     "NumberOfColumns": 0,
#     "CoordsRows": [],
#     "CoordsColumns": [],
#     "Description": ""
# })
#
# JSON_simulations = OrderedDict({
#         "ModelEq": "",
#         "ModelParam": "",
#         "SourceCode": "",
#         "SourceCodeVersion": "",
#         "SoftwareVersion": "",
#         "SoftwareName": "",
#         "SoftwareRepository": "",
#         "Network": [],
# })
#
# JSON_centers = {
#     "Units": "",
#     "AnatomicalLandmarkCoordinates": "",
#     "AnatomicalLandmarkCoordinateSystem": "",
#     "AnatomicalLandmarkCoordinateUnits": "",
#     "AnatomicalLandmarkCoordinateSystemDescription": "",
# }
#
# #     "": "",
# JSON_TS = {
#     "ModelEq": "",
#     "ModelParam": "",
#     "SourceCode": "",
#     "SourceCodeVersion": "",
#     "SoftwareVersion": "",
#     "SoftwareName": "",
#     "SoftwareRepository": "",
#     "Network": "",
#     "SamplingPeriod": "",
#     "SamplingFrequency": ""
# }
#
# JSON_SPATIAL = {
#     "ModelEq": "",
#     "ModelParam": "",
#     "SourceCode": "",
#     "SourceCodeVersion": "",
#     "": "",
#     "": "",
#     "": "",
#     "": "",
#     "": "",
#     "": "",
# }
#
#
#
# def merge_dicts(dict1, dict2):
#     return {**dict1, **dict2}
#
#
