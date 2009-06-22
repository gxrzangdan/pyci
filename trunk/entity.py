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
num_list = set([i for i in u"0123456789０１２３４５６７８９零一二三四五六七八九十百千万亿壹贰叁肆伍陆柒捌玖拾○佰仟.%％"])
date_list = set([i for i in u"年月日周时分秒"])
letter_list = set([i for i in u"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ"])

C_NUM = 0
C_DATE = 1
C_LETTER = 2
C_OTHER = 3

def char_class(char):
    if char in num_list:
        return C_NUM
    elif char in date_list:
        return C_DATE
    elif char in letter_list:
        return C_LETTER
    else:
        return C_OTHER
