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

# packages
import corpus
import tagset


# modules
import mm
import trie
import unigram
import crf
import brill

if __name__ == "__main__":
    print "=" * 20 + "TRIE" + "=" * 20
    trie.demo()
    print "=" * 20 + "MM" + "=" * 20
    mm.demo()
    print "=" * 20 + "Unigram" + "=" * 20
    unigram.demo()
    print "=" * 20 + "Brill" + "=" * 20
    brill.demo()
