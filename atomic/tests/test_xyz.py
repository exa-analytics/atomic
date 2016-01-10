# -*- coding: utf-8 -*-

# Hacky import
import sys
sys.path.insert(0, '/home/tjd/Programs/analytics-exa/atomic')
sys.path.insert(0, '/home/tjd/Programs/analytics-exa/exa')

from exa.testers import UnitTester
from atomic import xyz
from atomic import _np as np
from io import StringIO

xyzfl = '''3
1 comment
H 0.0  0.0 0.0
H 0.0  0.7 0.0
H 0.0 -0.7 0.0
2
comments 2
H 0.0  0.0 0.0
H 0.0 -0.7 0.0
'''

# Only partial testing of read_xyz
# Not sure how to implement testing linecache
# funtionality with a StringIO approach

class TestReadXYZ(UnitTester):
    def setUp(self):
        self.raw = xyz._rawdf(StringIO(xyzfl))
        self.idx = xyz._index(self.raw)

    def test__rawdf(self):
        self.assertEqual(self.raw.shape, (9, 4))

    def test__index(self):
        self.assertTrue(np.all(np.array(self.idx) == np.array([0, 5])))

    def test__parse_xyz(self):
        to = xyz._parse_xyz(self.raw, 'A', self.idx)
        self.assertTrue(np.all(np.array(to.index.levels[0]) == np.array([0, 1])))
        self.assertTrue(np.all(np.array(to.index.levels[1]) == np.array([0, 1, 2])))
