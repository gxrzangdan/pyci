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
import sys

class TagFeatureSet(object):
    """Tag set with feature information
    """

class CRFTagger(object):
    """An unigram tagger
    """

    def __init__(self):
        """Constructor
        """

        # Prepare lists for character classification
        self.prepareCharClassification()

    def useModel(self, modelPath):
        """
        use a alread trained model.

        @type modelPath: string
        @param modelPath: the path of the model file
        """
        #self.model = modelPath
        self.tagger = CRFPP.Tagger("-m %s -v3" % modelPath)

    def prepareTrainData(self, trainData, outPath):
        """Prepare a txt file for CRF++ to train

        @type trainData: iterable of words
        @param trainData: training set
        @type outPath: string
        @param outPath: the path and name of the output file
        """
        fp=open(outPath,"w")
        for char, tag in trainData:
            fp.write(("%s\t%s\t%s\n" % (char, self.charProperty(char), tag)).encode('utf8'))
        fp.close()

    def prepareCharClassification(self):
        """
        """
        self.numList = u"0123456789０１２３４５６７８９"
        self.dateList = u"年月日时分秒"
        self.letterList = u"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ"

    def charProperty(self, c):
        """Get the property of a character.
        @type c: a character
        @param c: a character to be analyzed
        """
        if c in self.numList:
            return "NUM"
        elif c in self.dateList:
            return "DATE"
        elif c in self.letterList:
            return "LETTER"
        else:
            return "NORMAL"

    def tag(self, sent):
        """Tag raw sent into (char, tag) tuple"""
        self.tagger.clear()

        #print sent
        # Add characters into tagger
        for i in sent:
            self.tagger.add(("%s\t%s" % (i, self.charProperty(i))).encode('utf8'))
#            print i

        self.tagger.parse()

        size = self.tagger.size()
        xsize = self.tagger.xsize()
        for i in range(0, (size)):
#           for j in range(0, (xsize)):
#              print tagger.x(i, j) , "\t",
#           print self.tagger.x(i, 0), self.tagger.y2(i)
           yield (self.tagger.x(i, 0).decode('utf8'), self.tagger.y2(i))
           #print "Details",
           #for j in range(0, (ysize-1)):
              #print "\t" , tagger.yname(j) , "/prob=" , tagger.prob(i,j),"/alpha=" , tagger.alpha(i, j),"/beta=" , tagger.beta(i, j),
#           print "\n",

#try:
    ## -v 3: access deep information like alpha,beta,prob
    ## -nN: enable nbest output. N should be >= 2
    ##tagger = CRFPP.Tagger("-m model -v 3 -n2")

    ## clear internal context
    #tagger.clear()

    ## add context
    #w=u"""记者20日从国家税务总局获悉，为了适当增加财政收入，完善烟产品消费税，我国近日对烟产品消费税政策作了重大调整，除烟产品生产环节的消费税政策有了较大改变，调整了计税价格，提高了消费税税率外，卷烟批发环节还加征了一道从价税，税率为5%。相关专家表示，我国大幅提高烟产品税负体现控烟与增收双重意图。

        #据介绍，政策调整后，甲类香烟的消费税从价税率由原来的45%调整至56%，乙类香烟由30%调整至36%，雪茄烟由25%调整至36%。与此同时，原来的甲乙类香烟划分标准也进行了调整，原来50元的分界线上浮至70元，即每标准条（200支）调拨价格在70元（不含增值税）以上（含70元）的卷烟为甲类卷烟，低于此价格的为乙类卷烟。  详细>>>

        #=== 提高烟产品消费税双重意图：控烟+增收 ===

            #“提高烟产品的税率，不但能增加政府收入，还能挽救上百万人的生命。”北京大学中国经济研究中心教授李玲在接受记者采访时表示。她说，在世界各国控烟的方式中，提高税率是最有效的方法之一。因为烟草价格是影响烟草产品短期消费的最主要因素，税率提高后烟价被抬高，年轻人、未成年人及低收入者戒烟或少吸烟的几率提高。

                #据介绍，目前，中国每年因吸烟致病造成的直接损失在1400亿元至1600亿元之间，间接损失达800亿元至1200亿元。为合理控制烟产品过度消费，世界上绝大多数国家均对其课以重税。2003年我国正式加入全球烟草控制框架公约，世界卫生组织不断督促我国加大利用税收手段控制吸烟的力度。“而我国卷烟税负水平与其他国家和地区相比明显偏低，有提升的空间。此次国家大幅度提高烟产品消费税税负，正当其时。”李玲说。  详细>>>"""
    #for i in w:
        #tagger.add(i.encode('utf8'))
    ##tagger.add("Confidence NN")
    ##tagger.add("in IN")
    ##tagger.add("the DT")
    ##tagger.add("pound NN")
    ##tagger.add("is VBZ")
    ##tagger.add("widely RB")
    ##tagger.add("expected VBN")
    ##tagger.add("to TO")
    ##tagger.add("take VB")
    ##tagger.add("another DT")
    ##tagger.add("sharp JJ")
    ##tagger.add("dive NN")
    ##tagger.add("if IN")
    ##tagger.add("trade NN")
    ##tagger.add("figures NNS")
    ##tagger.add("for IN")
    ##tagger.add("September NNP")

    #print "column size: " , tagger.xsize()
    #print "token size: " , tagger.size()
    #print "tag size: " , tagger.ysize()

    #print "tagset information:"
    #ysize = tagger.ysize()
    #for i in range(0, ysize):
        #print "tag " , i , " " , tagger.yname(i)

    ## parse and change internal stated as 'parsed'
    #tagger.parse()

    #print "conditional prob=" , tagger.prob(), " log(Z)=" , tagger.Z()

    #size = tagger.size()
    #xsize = tagger.xsize()
    #for i in range(0, (size )):
       #for j in range(0, (xsize)):
          #print tagger.x(i, j) , "\t",
       #print tagger.y2(i) , "\t",
       ##print "Details",
       ##for j in range(0, (ysize-1)):
          ##print "\t" , tagger.yname(j) , "/prob=" , tagger.prob(i,j),"/alpha=" , tagger.alpha(i, j),"/beta=" , tagger.beta(i, j),
       #print "\n",

    ##print "nbest outputs:"
    ##for n in range(0, 9):
        ##if (not tagger.next()):
            ##continue
        ##print "nbest n=" , n , "\tconditional prob=" , tagger.prob()
        ### you can access any information using tagger.y()...

    #print "Done"

#except RuntimeError, e:
    #print "RuntimeError: ", e,
