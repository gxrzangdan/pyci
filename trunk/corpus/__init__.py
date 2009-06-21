# -*- coding: utf-8 -*-

# PyCi
#
# Copyright (c) 2009, The PyCi Project
# Authors: Wu Ke <ngu.kho@gmail.com>
#          Chen Xing <cxcxcxcx@gmail.com>
# URL: <http://code.google.com/p/pyci>
# For license information, see COPYING


"""Corpus package, features:

  - BaseCorpusReader, fundamental corpus reader for any tagged corpus

  - RMRBCorpusReader, corpus reader for PFR Renmin Ribao Tagged Corpus
    data file

  - DZWZCorpusReader, corpus reader for Duzhe Wenzhai Tagged Corpus
    data file

For copyright reasons, PyCi does not include any corpus data. You may
get part of the PFR Renmin Ribao Tagged Corpus data for free at
<http://icl.pku.edu.cn/icl_groups/corpus/dwldform1.asp>
"""

__all__ = ["BaseCorpusReader", "RMRBCorpusReader", "DZWZCorpusReader",
           "Bakeoff2005TrainReader", "Bakeoff2005TestReader"]

from api import BaseCorpusReader
from rmrb import RMRBCorpusReader
from dzwz import DZWZCorpusReader
from bakeoff2005 import Bakeoff2005TrainReader, Bakeoff2005TestReader

# Paths for corpus data
#_rmrb_path = "/home/chenxing/PD_1998_01_POS.txt"
#_dzwz_path = "/home/chenxing/Readers_Digest.txt"

#rmrb = RMRBCorpusReader(_rmrb_path)
#dzwz = DZWZCorpusReader(_dzwz_path)
