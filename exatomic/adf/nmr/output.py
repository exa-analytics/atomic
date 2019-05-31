# -*- coding: utf-8 -*-
# Copyright (c) 2015-2018, Exa Analytics Development Team
# Distributed under the terms of the Apache License 2.0
"""
ADF NMR Output Editor
#############################
Editor class for parsing the NMR data from an ADF calculation
"""
from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from collections import defaultdict
import re
import six
import numpy as np
import pandas as pd
from io import StringIO
from exa.util.units import Length
from exa import TypedMeta
from exatomic.base import sym2z
#from exatomic.algorithms.basis import lmap, enum_cartesian
#from exatomic.algorithms.numerical import dfac21
from exatomic.core.atom import Atom
from exatomic.core.tensor import NMRShielding, JCoupling
#from exatomic.core.basis import BasisSet, BasisSetOrder
#from ..core.orbital import Orbital, Excitation, MOMatrix
from exatomic.adf.editor import Editor

class OutMeta(TypedMeta):
    atom = Atom
    nmr_shielding = NMRShielding
    j_coupling = JCoupling

class Output(six.with_metaclass(OutMeta, Editor)):
    """ADF NMR parser"""
    def parse_atom(self):
        # use the regex instead of find because we have a similar search string in an nmr and
        # cpl calculation for the nuclear coordinates
        _reatom = "(?i)NUCLEAR COORDINATES"
        found = self.regex(_reatom, keys_only=True)
        #if len(found) > 1:
        #    raise NotImplementedError("We can only parse outputs from a single NMR calculation")
        atom = []
        for idx, val in enumerate(found):
            start = val + 3
            stop = start
            while self[stop].strip(): stop += 1
            # a bit of a hack to make sure that there is no formatting change depending on the
            # number of atoms in the molecule as the index is right justified so if there are
            # more than 100 atoms it will fill the alloted space for the atom index and change the
            # delimitter and therefore the number of columns
            self[start:stop] = map(lambda x: x.replace('(', ''), self[start:stop])
            df = self.pandas_dataframe(start, stop, ncol=5)
            df.columns = ['symbol', 'set', 'x', 'y', 'z']
            for c in ['x', 'y', 'z']: df[c] *= Length['Angstrom', 'au']
            df['Z'] = df['symbol'].map(sym2z)
            df['frame'] = idx
            # remove the trailing chracters from the index
            df['set'] = list(map(lambda x: x.replace('):', ''), df['set']))
            df['set'] = df['set'].astype(int) - 1
            atom.append(df)
        self.atom = pd.concat(atom, ignore_index=True)

    def parse_nmr_shielding(self):
        _reatom = "N U C L E U S :"
        _reshield = "==== total shielding tensor"
        _renatom = "NUCLEAR COORDINATES (ANGSTROMS)"
        found = self.find(_reatom, keys_only=True)
        if not found:
            #raise NotImplementedError("Could not find {} in output".format(_reatom))
            return
        ncalc = self.find(_renatom, keys_only=True)
        ncalc.append(len(self))
        ndx = 0
        dfs = []
        for start in found:
            try:
                ndx = ndx if start > ncalc[ndx] and start < ncalc[ndx+1] else ndx+1
            except IndexError:
                raise IndexError("It seems that there was an issue with determining which NMR calculation we are in")
            start_shield = self.find(_reshield, keys_only=True, start=start)[0] + start + 2
            end_shield = start_shield + 3
            symbol, index = self[start].split()[-1].split('(')
            index = int(index.replace(')', ''))
            isotropic = float(self[start_shield+4].split()[-1])
            df = self.pandas_dataframe(start_shield, end_shield, ncol=3)
            cols = ['xx', 'xy', 'xz', 'yx', 'yy', 'yz', 'zx', 'zy', 'zz']
            df = pd.DataFrame(df.unstack().values.reshape(1,9), columns=cols)
            df['isotropic'] = isotropic
            df['atom'] = index - 1
            df['symbol'] = symbol
            df['label'] = 'nmr shielding'
            df['frame'] = ndx
            dfs.append(df)
        shielding = pd.concat(dfs, ignore_index=True)
        self.nmr_shielding = shielding

