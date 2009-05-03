# -*- coding: utf-8 -*-

# PyCi
#
# Copyright (c) 2009, The PyCi Project
# Authors: Wu Ke <ngu.kho@gmail.com>
#          Chen Xing <cxcxcxcx@gmail.com>
# URL: <http://code.google.com/p/pyci>
# For license information, see COPYING


"""Gneral interface for a corpus reader
"""
__all__ = ["BaseCorpusReader"]

class BaseCorpusReader(object):
    """Basic corpus interface
    """
    _loaded_paras = []
    _all_para_loaded = False

    def raw_para(self):
        """Read a paragraph -- you need to implement this for your
        corpus reader.

        You have to decode these bytes into Unicode.

        @return: a generator iterates over all paragraphs in
        appearances order
        """
        raise NotImplementedError

    def seg_sents(cls, para):
        """Segment a raw paragraph into a list of sentences -- you
        need to implement this.

        @return: a list of segmented sentences
        """
        raise NotImplementedError

    def seg_words(cls, sent):
        """Segment a raw sentence into a list of tuples of words and
        corresponding POS tags -- you need to implement this.

        @return: a list of tuples of words and POS tags
        """
        raise NotImplementedError

    def words(self):
        """Get untagged words from the corpus. This is done with the
        help of read_a_para(), seg_sents(), and seg_words() you
        provide.

        @return: a generator which iterates over all the words in
        appearances order
        """
        for word in self.tagged_words():
            yield word[0]

    def sents(self):
        """Get untagged sentences from the corpus. Sentences are
        organized as lists of words. This is done with the help of
        read_a_para(), seg_sents(), and seg_words() you provide.

        @return: a generator which iterates over all the sentences in
        appearances order
        """
        for sent in self.tagged_sents():
            yield [word[0] for word in sent]

    def paras(self):
        """Get untagged paragraphs from the corpus. Paragraphs are
        organized as lists of sentences, and sentences are in the same
        form as you get from sents(). This is done with the help of
        read_a_para(), seg_words(), and seg_words() you provide.

        @return: a generator which iterates over all the paragraphs in
        appearances order
        """
        for para in self.tagged_paras():
            yield [[word[0] for word in sent] for sent in para]

    def tagged_words(self):
        """Get tagged words from the corpus. Words are organized as
        tuples of (word, postag). This is done with the help of
        read_a_para(), seg_sents(), and seg_words() you provide.

        @return: a generator which iterates over all the words in
        appearances order
        """
        for sent in self.tagged_sents():
            for word in sent:
                yield word

    def tagged_sents(self):
        """Get tagged sentences from the corpus. Sentences are
        organized as lists of tuples of words and POS tags. This is
        done with the help of read_a_para(), seg_sents(), and
        seg_words() you provide.

        @return: a generator which iterates over all the sentences in
        appearances order
        """
        for para in self.tagged_paras():
            for sent in para:
                yield sent

    def tagged_paras(self):
        """Get tagged paragraphs from the corpus. Paragraphs are
        organized as lists of sentences, and sentences are in the same
        form as you get from tagged_sents(). This is done with the
        help of read_a_para(), seg_words(), and seg_words() you
        provide.

        @return: a generator which iterates over all the paragraphs in
        appearances order
        """
        if self._all_para_loaded:
            for para in self._loaded_paras:
                yield para
        else:
            for para in self.raw_para():
                self._loaded_paras.append(
                    [self.seg_words(sent)
                     for sent in self.seg_sents(para)])
                yield self._loaded_paras[-1]
            self._all_para_loaded = True

class DummyCorpusReader(BaseCorpusReader):
    """Dummy corpus reader for testing purpose.
    """

    def __init__(self):
        pass

    def raw_para(self):
        for i in ['This is paragraph one .\nHello Everyone !', 'This is paragraph two .']:
            yield i

    def seg_sents(cls, para):
        return para.split('\n')

    def seg_words(cls, sent):
        return zip(sent.split(), range(100))

if __name__ == "__main__":
    d = DummyCorpusReader()
    print "-" * 20, "Words", "-" * 20
    for i in d.words():
        print i
    print "-" * 20, "Sentences", "-" * 20
    for i in d.sents():
        print repr(i)
    print "-" * 20, "Paragraphs", "-" * 20
    for i in d.paras():
        print repr(i)
    print "-" * 20, "Tagged words", "-" * 20
    for i in d.tagged_words():
        print i
    print "-" * 20, "Tagged sentences", "-" * 20
    for i in d.tagged_sents():
        print repr(i)
    print "-" * 20, "Tagged paragraphs", "-" * 20
    for i in d.tagged_paras():
        print repr(i)
    print "-" * 20, "Tagged paragraphs again", "-" * 20
    for i in d.tagged_paras():
        print repr(i)
