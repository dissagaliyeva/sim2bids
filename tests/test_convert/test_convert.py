# usage: python test/test_appert/test_appert.py
# usage: python -m unittest test/test_appert/test_appert.py

import os
import unittest
from src.sim2bids import appert
from src.sim2bids import rm_tree


PATHS = ['../../data/timeseries_all.mat',
         '../../data/ses-preop/FC.mat']

FAIL1 = ['../../data/ses-preop/HRF.mat']

OUTPUT = '../../output'

OUTPUT_FILE = ['../../output/timeseries_all_data.tsv',
               '../../output/FC_CON01T1_ROIts.tsv',
               '../../output/FC_CON01T1_ROIts_DK68.tsv',
               '../../output/FC_FC_cc_DK68.tsv',
               '../../output/FC_FC_cc.tsv',
               '../../output/FC_ROI_ID_table.tsv'
               ]


class Testappert(unittest.TestCase):

    def test_to_tsv(self):
        _ = appert.to_tsv(PATHS[0])

        # verify the folder gets created
        self.assertTrue(os.path.exists(OUTPUT))

        # verify the output folder is not empty
        self.assertTrue(os.listdir(OUTPUT) != 0)

        # verify timeseries_all.mat is apperted to tsv
        self.assertTrue(os.path.exists(OUTPUT_FILE[0]))

        # verify multi-file appersion
        _ = appert.to_tsv(PATHS)

        # verify timeseries_all.mat is apperted to tsv
        for path in OUTPUT_FILE:
            self.assertTrue(os.path.exists(path))

        # remove all files
        rm_tree(OUTPUT)

        # verify empty files don't get processed
        _ = appert.to_tsv(FAIL1)
        self.assertFalse(len(os.listdir(OUTPUT)) > 0)

        # remove all files
        rm_tree(OUTPUT)
        self.assertFalse(os.path.exists(OUTPUT))

    def test_check_filetype(self):

        # check .mat file
        p1 = appert.check_filetype(PATHS[0])
        self.assertTrue(p1, '.mat')

        # check multiple .mat files
        p2 = appert.check_filetype(PATHS)
        self.assertTrue(p2, '.mat')

        # verify .csv file
        p3 = appert.check_filetype('../../data/ses-preop/HRF.csv')
        self.assertTrue(p3, '.csv')

        # verify .dcm file
        p4 = appert.check_filetype('../../data/dcm/image-000350.dcm')
        self.assertTrue(p4, '.dcm')

        # verify exception
        self.assertRaises(TypeError, appert.check_filetype,
                          [PATHS[0], '../../data/ses-preop/HRF.csv'])


if __name__ == '__main__':
    unittest.main()

