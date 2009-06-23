# -*- coding: utf-8 -*-

# PyCi
#
# Copyright (c) 2009, The PyCi Project
# Authors: Wu Ke <ngu.kho@gmail.com>
#          Chen Xing <cxcxcxcx@gmail.com>
# URL: <http://code.google.com/p/pyci>
# For license information, see COPYING


"""CRF segmentor using existing model
"""
__all__ = ["CRFTagger"]


import CRFPP
import tagset
from entity import *

class CRFTagger(object):
    """An unigram tagger
    """

    def __init__(self, tag_set):
        """Constructor
        """
        self.tag_set = tag_set
        self.seg_o = tagset.TagSeg(tag_set, self.tag) # 创建相应的切分器

        #self.prepareCharClassification()

    def use_model(self, model_path):
        """
        use a alread trained model.

        @type modelPath: string
        @param modelPath: the path of the model file
        """
        #self.model = modelPath
        self.tagger = CRFPP.Tagger("-m %s -v3" % model_path)

    def prepare_train_data(self, train_data, out_stream):
        """Prepare a txt file for CRF++ to train

        @type trainData: iterable of words
        @param trainData: training set
        @type outPath: string
        @param outPath: the path and name of the output file
        """
        for char, tag in self.tag_set.tag(train_data):
            out_stream.write(("%s\t%s\t%s\n" % (char, self.char_property(char), tag)).encode('utf8'))

    #def prepareCharClassification(self):
        #"""
        #"""
        #self.numList = u"0123456789０１２３４５６７８９"
        #self.dateList = u"年月日时分秒"
        #self.letterList = u"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ"

    def char_property(self, c):
        """Get the property of a character.
        @type c: a character
        @param c: a character to be analyzed
        """
        if c in num_list:
            return "NUM"
        elif c in date_list:
            return "DATE"
        elif c in letter_list:
            return "LETTER"
        else:
            return "NORMAL"

    def tag(self, sent):
        """Tag raw sent into (char, tag) tuple"""
        self.tagger.clear()

        # Add characters into tagger
        for i in sent:
            self.tagger.add(("%s\t%s" % (i, self.char_property(i))).encode('utf8'))

        self.tagger.parse()

        size = self.tagger.size()
        xsize = self.tagger.xsize()
        for i in range(0, (size)):
           yield (self.tagger.x(i, 0).decode('utf8'), self.tagger.y2(i))

    def seg(self, sent, verbose=False):
        """Segment a string and return a list of words
        """

        return self.seg_o.seg(sent,verbose=verbose)
