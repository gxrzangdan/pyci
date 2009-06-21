# -*- coding: utf-8 -*-

# PyCi
#
# Copyright (c) 2009, The PyCi Project
# Authors: Wu Ke <ngu.kho@gmail.com>
#          Chen Xing <cxcxcxcx@gmail.com>
# URL: <http://code.google.com/p/pyci>
# For license information, see COPYING


"""PyCi -- a Chinese word segmentor library for Python
"""

__version__ = "0.0"

import corpus
import tagset


import mm
import trie
import unigram
import crf

if __name__ == "__main__":
    print "TRIE"
    trie.demo()
    print "MM"
    mm.demo()
    print "Unigram"
    unigram.demo()
