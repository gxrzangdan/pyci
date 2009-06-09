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
            self._trie[word] = word

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
            if idx is None:
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
        # just reverse everything
        train = [i[::-1] for i in train]
        FMMSeg.add_words(self, train)


    def seg(self, sent):
        """Segment a sentence.

        @type sent: unicode string
        @param sent: the sentence to be segmented

        @return: a list of segmented words
        """
        sent = sent[::-1]
        words = FMMSeg.seg(self, sent)
        words.reverse()
        return [i[::-1] for i in words]


def demo():
    """Demo for FMM and BMM segmentors
    """
    from pyci.corpus import rmrb

    words = [i for i in rmrb.words()]
    fseg = FMMSeg(train=words)
    bseg = BMMSeg(train=words)

    print "OOV"
    sent = u"马勒戈壁上的草泥马战胜了河蟹。"

    print "FMM",
    print "/".join(fseg.seg(sent))

    print "BMM",
    print "/".join(bseg.seg(sent))

    print "Let's add those words"
    new_words = [u"马勒戈壁", u"草泥马", u"河蟹"]
    fseg.add_words(new_words)
    bseg.add_words(new_words)

    print "FMM",
    print "/".join(fseg.seg(sent))

    print "BMM",
    print "/".join(bseg.seg(sent))

    print "\nAmbiguity"
    sent1 = u"结合成分子时"

    print "FMM",
    print "/".join(fseg.seg(sent1))

    print "BMM",
    print "/".join(bseg.seg(sent1))


if __name__ == "__main__":
    demo()
