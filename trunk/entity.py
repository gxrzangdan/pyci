# -*- coding: utf-8 -*-

# PyCi
#
# Copyright (c) 2009, The PyCi Project
# Authors: Wu Ke <ngu.kho@gmail.com>
#          Chen Xing <cxcxcxcx@gmail.com>
# URL: <http://code.google.com/p/pyci>
# For license information, see COPYING


"""Character entity
"""

# Prepare lists for character classification
num_list = set([i for i in u"0123456789����������������������һ�����������߰˾�ʮ��ǧ����Ҽ��������½��ƾ�ʰ���Ǫ.%��"])
date_list = set([i for i in u"��������ʱ����"])
letter_list = set([i for in u"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ������������������������������������£ãģţƣǣȣɣʣˣ̣ͣΣϣУѣңӣԣգ֣ףأ٣�"])
