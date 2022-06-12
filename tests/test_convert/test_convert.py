# usage: python test/test_convert/test_convert.py
# usage: python -m unittest test/test_convert/test_convert.py

import os
import unittest
from mock import patch
from incf.convert import convert
from incf.util import rm_tree


PATHS = ['../../data/timeseries_all.mat',
         '../../data/ses-preop/FC.mat']

OUTPUT = '../../output'

OUTPUT_FILE = ['../../output/timeseries_all_data.tsv',
               '../../output/FC_CON01T1_ROIts.tsv',
               '../../output/FC_CON01T1_ROIts_DK68.tsv',
               '../../output/FC_FC_cc_DK68.tsv',
               '../../output/FC_FC_cc.tsv',
               '../../output/FC_ROI_ID_table.tsv'
               ]


class TestConvert(unittest.TestCase):

    def test_to_tsv(self):
        _ = convert.to_tsv(PATHS[0])

        # verify the folder gets created
        self.assertTrue(os.path.exists(OUTPUT))

        # verify the output folder is not empty
        self.assertTrue(os.listdir(OUTPUT) != 0)

        # verify timeseries_all.mat is converted to tsv
        self.assertTrue(os.path.exists(OUTPUT_FILE[0]))

        # verify multi-file conversion
        _ = convert.to_tsv(PATHS)

        # verify timeseries_all.mat is converted to tsv
        for path in OUTPUT_FILE:
            self.assertTrue(os.path.exists(path))

        # verify files deletion
        rm_tree(OUTPUT)
        self.assertFalse(os.path.exists(OUTPUT))

    def test_to_(self):
        pass


if __name__ == '__main__':
    unittest.main()
