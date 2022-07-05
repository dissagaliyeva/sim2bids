from collections import OrderedDict

JSON_template = OrderedDict({
    "NumberOfRows": 0,
    "NumberOfColumns": 0,
    "CoordsRows": [],
    "CoordsColumns": [],
})

JSON_simulations = OrderedDict({
        "ModelEq": "",
        "ModelParam": "",
        "SourceCode": "",
        "SourceCodeVersion": "",
        "SoftwareVersion": "",
        "SoftwareName": "",
        "SoftwareRepository": "",
        "Network": [],
        "Description": ""
})

JSON_centers = {
    "NumberOfRows": 0,
    "NumberOfColumns": 0,
    "Units": "",
    "Description": ""
}


def merge_dicts(dict1, dict2):
    return {**dict1, **dict2}


def populate_dict(dict1, shape, desc, coords=None):
    dict1['NumberOfRows'] = shape[0]
    dict1['NumberOfColumns'] = shape[1]
    dict1['Description'] = desc

    if coords:
        dict1['CoordsRows'] = coords
        dict1['CoordsColumns'] = coords

    return dict1
