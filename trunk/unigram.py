# -*- coding: utf-8 -*-

# PyCi
#
# Copyright (c) 2009, The PyCi Project
# Authors: Wu Ke <ngu.kho@gmail.com>
#          Chen Xing <cxcxcxcx@gmail.com>
# URL: <http://code.google.com/p/pyci>
# For license information, see COPYING


"""Unigram segmentor using tagging technique
"""
__all__ = ["UnigramTagger"]

from collections import defaultdict

from tagset import *

class UnigramTagger(object):
    """An unigram tagger
    """

    def __init__(self, tagset, train=None):
        """Construct an unigram segmentor

        @type tagset: TagSet
        @param tagset: the tag set to train
        @type train: iterable of words
        @param train: training set
        """
        self.tagset = tagset
        self.count = defaultdict(lambda : defaultdict(int))
        if train:
            self.add_words(train)

    def add_words(self, train):
        """Add words into the trie.

        @type train: iterable of words
        @param train: training set
        """
        for char, tag in self.tagset.tag(train):
            self.count[char][tag] += 1

    def tag(self, sent):
        """Tag raw sent into (char, tag) tuple"""
        for char in sent:
            if char in self.count:
                yield (char, max(self.count[char].keys(), key=lambda x:self.count[char][x]))
            else:
                yield (char, None)


def demo():
    words = ['ab', 'abb', 'ab', 'ba']

    def bintag(word):
        res = []
        if word:
            res.append((word[0], 'A'))
            for i in word[1:]:
                res.append((i, 'B'))
        return res

    tagset = TagSet(['A'], ['B'], bintag)
    tagger = UnigramTagger(tagset, words)
    segger = TagSeg(tagset, tagger)

    s = 'ababbabba'
    print [i for i in tagger.tag(s)]

    print segger.seg(s)


if __name__ == "__main__":
    demo()
