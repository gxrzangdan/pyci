# -*- coding: utf-8 -*-

# PyCi
#
# Copyright (c) 2009, The PyCi Project
# Authors: Wu Ke <ngu.kho@gmail.com>
#          Chen Xing <cxcxcxcx@gmail.com>
# URL: <http://code.google.com/p/pyci>
# For license information, see COPYING


"""Corpus reader for Bakeoff 2005 training and testing corpus.

For more information and corpus data of the Second International
Chinese Word Segmentation Bakeoff, please visit
http://www.sighan.org/bakeoff2005/
"""
__all__ = ["Bakeoff2005TrainReader", "Bakeoff2005TestReader"]

from api import BaseCorpusReader

class Bakeoff2005TrainReader(BaseCorpusReader):
    """Corpus reader for Bakeoff 2005 training corpus.

    The Bakeoff 2005 training data is formatted as below:
      1. There will be one sentence per line.
      2. Words and punctuation symbols will be separated by
      spaces.
      3. There will be no further annotations, such as part-of-speech
      tags: if the original corpus includes those, those will be
      removed.
    """

    def __init__(self, path, coding="utf-8"):
        """Constructor for a Bakeoff 2005 training corpus reader.

        @type path: string
        @param path: the path for the corpus file
        @type coding: string
        @param coding: encoding for the corpus file
        """
        self._coding = coding
        self._path = path

    def raw_para(self):
        """Read a paragraph and decode into Unicode.

        @return: a generator iterates over all paragraphs in
        appearances order
        """
        corpus_file = file(self._path, "rU")
        for para in corpus_file.readlines():
            # strip off white spaces
            para = para.strip()
            if para:
                # decode into Unicode
                para = para.decode(self._coding)
                yield para
        corpus_file.close()

    def seg_sents(cls, para):
        """Segment a raw paragraph into a list of sentences.

        Bakeoff corpus has no paragraph information so one paragraph
        is actually one sentence.

        @return: a list of segmented sentences
        """
        return [para]

    def seg_words(cls, sent):
        """Segment a raw sentence into a list of tuples of words and
        None.

        @return: a list of tuples of words and None(as POS tags)
        """
        res = []
        for word in sent.split():
            res.append((word, None))
        return res

    def __repr__(self):
        return "<Bakeoff2005TrainReader: %s>" % self._path


class Bakeoff2005TestReader(BaseCorpusReader):
    """Corpus reader for Bakeoff 2005 test corpus.

    The Bakeoff 2005 test data is formatted as below:
      1. There will be one sentence per line.
    """

    def __init__(self, path, coding="utf-8"):
        """Constructor for a Bakeoff 2005 test corpus reader.

        @type path: string
        @param path: the path for the corpus file
        @type coding: string
        @param coding: encoding for the corpus file
        """
        self._coding = coding
        self._path = path

    def raw_para(self):
        """Read a paragraph and decode into Unicode.

        @return: a generator iterates over all paragraphs in
        appearances order
        """
        corpus_file = file(self._path, "rU")
        for para in corpus_file.readlines():
            # strip off white spaces
            para = para.strip()
            if para:
                # decode into Unicode
                para = para.decode(self._coding)
                yield para
        corpus_file.close()

    def seg_sents(cls, para):
        """Segment a raw paragraph into a list of sentences.

        Bakeoff corpus has no paragraph information so one paragraph
        is actually one sentence.

        @return: a list of segmented sentences
        """
        return [para]

    def seg_words(cls, sent):
        """You're not going to use that, right?

        Segment a raw sentence into a list of tuples of words and
        None.

        @return: a list of tuples of words and None(as POS tags)
        """
        return [(sent, None)]

    def __repr__(self):
        return "<Bakeoff2005TestReader: %s>" % self._path


def demo_train():
    """Demo for Bakeoff2005TrainReader"""
    path = raw_input("TRAIN PATH: ")
    d = Bakeoff2005TrainReader(path)
    count = 0
    for sent in d.sents():
        print count,
        print ' '.join(sent)
        count += 1
        if count == 10:
            break


def demo_test():
    """Demo for Bakeoff2005TrainReader"""
    path = raw_input("TEST PATH: ")
    d = Bakeoff2005TestReader(path)
    count = 0
    for sent in d.sents():
        print count,
        print ' '.join(sent)
        count += 1
        if count == 10:
            break

if __name__ == "__main__":
    # demo and test
    demo_train()
    demo_test()
