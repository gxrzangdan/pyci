# -*- coding: utf-8 -*-

# PyCi
#
# Copyright (c) 2009, The PyCi Project
# Authors: Wu Ke <ngu.kho@gmail.com>
#          Chen Xing <cxcxcxcx@gmail.com>
# URL: <http://code.google.com/p/pyci>
# For license information, see COPYING


"""TagSet interface
"""
__all__ = ["TagError", "TagSet"]

class TagError(Exception):
    pass

class TagSet(object):
    """Basic tagset
    """

    def __init__(self, initial_tags, other_tags, tagger):
        """Construct a tag set.

        @type initial_tags: iterable
        @param initial_tags: tags which stands for a starting of a word
        @type other_tags: iterable
        @param other_tags: other tags
        @type tagger: function returning a list of tuples
        @param tagger: function to put tags onto a word, returns a
        list of (character, tag) tuples
        """
        self.itags = set([i for i in initial_tags])
        self.otags = set([i for i in other_tags])
        self.tagger = tagger

    def tag(self, sent):
        """Tag a sentence.

        @type sent: a list of words
        @param sent: the sentence to be tagged by tagger
        @return : generator
        """
        for word in sent:
            for chartuple in self.tagger(word):
                yield chartuple

    def untag(self, tagged_sent, strict=True):
        """Untag a sentence into a list of words.

        @type tagged_sent: a list of (character, tag) tuples
        @param tagged_sent: the sentence to be untagged
        @type strict: bool
        @param strict: whether untagging is strict, if True, a
        TagError will be raise if the tag is in neither self.itags nor
        self.otags, otherwise, the character will be treated as if
        it's a single character word
        @return: generator
        """
        word = ""
        for char, tag in tagged_sent:
            if tag in self.itags:
                if word:
                    yield word
                word = char
            elif tag in self.otags:
                word += char
            else:
                if strict:
                    raise TagError()
                if word:
                    yield word
                word = ""
                yield char
        if word:
            yield word


def demo():
    def tagger(word):
        res = []
        for char in word:
            if char == 'a':
                res.append((char, 'a'))
            else:
                res.append((char, 'b'))
        return res

    itags = ['a']
    otags = ['b']

    tagset = TagSet(itags, otags, tagger)

    sent = ['a', 'asdf', 'asjlks', 'ajb', 'asdlk']
    print sent
    print [i for i in tagset.tag(sent)]
    print [i for i in tagset.untag(tagset.tag(sent))]

    wrong = [('a', 'a'), ('b', 'b'), ('c', 'c'), ('d', 'a'), ('e', 'a'), ('f', 'b'), ('g', 'b')]
    try:
        print [i for i in tagset.untag(wrong)]
    except TagError:
        print "Catched"

    try:
        print [i for i in tagset.untag(wrong, False)]
    except:
        print "No"


if __name__ == "__main__":
    demo()
