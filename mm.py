# -*- coding: utf-8 -*-

# PyCi
#
# Copyright (c) 2009, The PyCi Project
# Authors: Wu Ke <ngu.kho@gmail.com>
#          Chen Xing <cxcxcxcx@gmail.com>
# URL: <http://code.google.com/p/pyci>
# For license information, see COPYING


"""Forward and Backward Maximum Matching word segmentor. Mainly used
as a baseline segmentor.
"""

from copy import deepcopy

from pyci.trie import Trie

class FMMSeg(object):
    """A forward maximum matching Chinese word segmentor.
    """

    def __init__(self, wordtrie=None, train=None):
        """Construct a FMM Chinese word segmentor.

        @type train: an iterable of words
        @param train: training set
        @type wordtrie: a trie of words
        @param wordtrie: previously trained trie

        If wordtrie is provided, it's deepcopied as the initial trie,
        otherwise a new blank trie will be constructed.

        If train is provided, it's appended into the trie above.
        """
        if wordtrie:
            self._trie = deepcopy(wordtrie)
        else:
            self._trie = Trie()
        if train:
            self.add_words(train)

    def add_words(self, train):
        """Add train words into the trie.

        @type train: an iterable of words
        @param train: (possibly) new words
        """
        for word in train:
            self._trie[word] = None

    def seg(self, sent):
        """Segment a sentence.

        @type sent: unicode string
        @param sent: the sentence to be segmented

        @return: a list of segmented words
        """
        words = []
        offset = 0
        idx = self._trie.longest_prefix(sent, offset)
        while offset < len(sent):
            if idx == offset:
                # the first character is not found in our trie, so
                # treat it as a whole word
                idx = offset + 1
            words.append(sent[offset:idx])
            offset = idx
            idx = self._trie.longest_prefix(sent, offset)
        return words


class BMMSeg(FMMSeg):
    """A backward maximum matching Chinese word segmentor.
    """

    def add_words(self, train):
        """Add train words into the trie.

        @type train: an iterable of words
        @param train: (possibly) new words
        """
        for word in train:
            self._trie[word[::-1]] = None


    def seg(self, sent):
        """Segment a sentence.

        @type sent: unicode string
        @param sent: the sentence to be segmented

        @return: a list of segmented words
        """
        sent = sent[::-1]
        words = []
        offset = 0
        idx = self._trie.longest_prefix(sent, offset)
        while offset < len(sent):
            if idx == offset:
                # the first character is not found in our trie, so
                # treat it as a whole word
                idx = offset + 1
            words.append(sent[offset:idx])
            offset = idx
            idx = self._trie.longest_prefix(sent, offset)
        words.reverse()
        return [i[::-1] for i in words]


def demo_fmm():
    """Demo for FMM segmentor
    """
    from pyci.corpus import rmrb
    words = [i for i in rmrb.words()]
    seg = FMMSeg(train=words)
    sent = u"马勒戈壁上的草泥马战胜了河蟹。"
    print "/".join(seg.seg(sent))
    seg.add_words([u"草泥马", u"马勒戈壁", u"河蟹"])
    print "/".join(seg.seg(sent))


def demo_bmm():
    """Demo for BMM segmentor
    """
    from pyci.corpus import rmrb
    words = [i for i in rmrb.words()]
    seg = BMMSeg(train=words)
    sent = u"马勒戈壁上的草泥马战胜了河蟹。"
    print "/".join(seg.seg(sent))
    seg.add_words([u"草泥马", u"马勒戈壁", u"河蟹"])
    print "/".join(seg.seg(sent))

if __name__ == "__main__":
    print "FMM"
    demo_fmm()
    print "BMM"
    demo_bmm()
