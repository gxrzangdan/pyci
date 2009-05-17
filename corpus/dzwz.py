# -*- coding: utf-8 -*-

# PyCi
#
# Copyright (c) 2009, The PyCi Project
# Authors: Wu Ke <ngu.kho@gmail.com>
#          Chen Xing <cxcxcxcx@gmail.com>
# URL: <http://code.google.com/p/pyci>
# For license information, see COPYING


"""Corpus reader for Duzhe Wenzhai Tagged Corpus
"""
__all__ = ["DZWZCorpusReader"]

from api import BaseCorpusReader

class DZWZCorpusReader(BaseCorpusReader):
    """Corpus reader for Duzhe Wenzhai Tagged Corpus
    """

    def __init__(self, path, coding="gb18030"):
        """Constructor for a Duzhe Wenzhai Tagged Corpus reader.

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

    def seg_sents(cls, para):
        """Segment a raw paragraph into a list of sentences.

        Temporarily treat whole paragraph as a sentence.

        @return: a list of segmented sentences
        """
        # TODO: make a real sentence segmentor.
        return [para]

    def seg_words(cls, sent):
        """Segment a raw sentence into a list of tuples of words and
        corresponding POS tags.

        @return: a list of tuples of words and POS tags
        """
        res = []
        for word in sent.split():
            res.append(tuple(word.split("/")))
        return res

    def __repr__(self):
        return "<DZWZCorpusReader: %s>" % self._path


if __name__ == "__main__":
    # demo and test
    d = DZWZCorpusReader("/var/Readers_Digest.txt")
    for word in d.tagged_words():
        print word[0], word[1]
