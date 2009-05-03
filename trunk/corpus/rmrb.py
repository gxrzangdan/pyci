# -*- coding: utf-8 -*-

# PyCi
#
# Copyright (c) 2009, The PyCi Project
# Authors: Wu Ke <ngu.kho@gmail.com>
#          Chen Xing <cxcxcxcx@gmail.com>
# URL: <http://code.google.com/p/pyci>
# For license information, see COPYING


"""
Corpus Reader for PFR Renmin Ribao Tagged Corpus

For copyright reasons, PyCi does not include any corpus data. You may
get part of the PFR Renmin Ribao Tagged Corpus data for free at
<http://icl.pku.edu.cn/icl_groups/corpus/dwldform1.asp>
"""
__all__ = ["RMRBCorpusReader"]

from api import BaseCorpusReader


class RMRBCorpusReader(BaseCorpusReader):
    """Corpus Reader for PFR Renmin Ribao Tagged Corpus
    """

    def __init__(self, path, coding="gb18030"):
        """Constructor for a PFR Renmin Ribao Tagged Corpus reader.

        @type path: string
        @param path: the path for the corpus file
        @type coding: string
        @param coding: encoding for the corpus file
        """
        self._coding = coding
        self._path = path

    def raw_para(self):
        """Read a paragraph and decode into Unicode.

        Starting number for each paragraph will be stripped off.

        @return: a generator iterates over all paragraphs in
        appearances order
        """
        corpus_file = file(self._path, "rU")
        for para in corpus_file.readlines():
            # strip off white spaces
            para = para.strip()
            if para:
                # strip off the starting numbering
                para = para[len("19980101-01-001-001/m"):]
                # decode into Unicode
                para = para.decode(self._coding)
                yield para

    def seg_sents(cls, para):
        """Segment a raw paragraph into a list of sentences.

        Temporarily treat whole paragraph as a sentence.

        @return: a list of segmented sentences
        """
        # TODO: make a real sentence segmentor.
        yield para

    def seg_words(cls, sent):
        """Segment a raw sentence into a list of tuples of words and
        corresponding POS tags.

        @return: a list of tuples of words and POS tags
        """
        for word in sent.split():
            yield tuple(word.split("/"))

    def __repr__(self):
        return "<RMRBCorpusReader: %s>" % self._path


if __name__ == "__main__":
    # demo and test
    r = RMRBCorpusReader("/var/PD_1998_01_POS.txt")
    for word in r.tagged_words():
        print word[0], word[1]
