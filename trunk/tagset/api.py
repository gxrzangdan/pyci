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
        """
        res = []
        for word in sent:
            res.extend(self.tagger(word))
        return res

    def untag(self, tagged_sent):
        """Untag a sentence

        @type tagged_sent: a list of (character, tag) tuples
        """
        res = []
        word = ""
        for char, tag in tagged_sent:
            if tag in self.itags:
                if word:
                    res.append(word)
                word = char
            elif tag in self.otags:
                word += char
            else:
                raise TagError()
        return res


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
    print tagset.tag(sent)
    print tagset.untag(tagset.tag(sent))

    wrong = [('a', 'a'), ('b', 'b'), ('c', 'c')]
    try:
        print tagset.untag(wrong)
    except TagError:
        print "Catched"


if __name__ == "__main__":
    demo()
