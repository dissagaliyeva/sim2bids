# usage: python test/test_convert/test_convert.py
# usage: python -m unittest test/test_convert/test_convert.py

import os
import unittest
from mock import patch
from incf.convert import convert


PATH1 = '../../data/timeseries_all.mat'
OUTPUT = '../../output'


class TestConvert(unittest.TestCase):

    def test_to_tsv(self):
        _ = convert.to_tsv(PATH1)

        # verify the folder gets created
        self.assertTrue(os.path.exists(OUTPUT))

        # verify the output folder is not empty
        self.assertTrue(os.listdir(OUTPUT) != 0)

        # verify timeseries_all.mat is converted to tsv
        self.assertTrue(os.path.exists(os.path.join(OUTPUT, 'timeseries_all_data.tsv')))


if __name__ == '__main__':
    unittest.main()
