# -*- coding: utf-8 -*-

# PyCi
#
# Copyright (c) 2009, The PyCi Project
# Authors: Wu Ke <ngu.kho@gmail.com>
#          Chen Xing <cxcxcxcx@gmail.com>
# URL: <http://code.google.com/p/pyci>
# For license information, see COPYING


"""TagSet package.

Contains several tag set used for tagging segmentation like CRF.
"""

from api import TagError, TagSet, TagSeg
from template import *


def demo():
    print ":::DEMO for tagset package:::"
    import api
    import template
    api.demo()
    template.demo()


if __name__ == "__main__":
    demo()
