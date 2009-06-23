# -*- coding: utf-8 -*-

# PyCi
#
# Copyright (c) 2009, The PyCi Project
# Authors: Wu Ke <ngu.kho@gmail.com>
#          Chen Xing <cxcxcxcx@gmail.com>
# URL: <http://code.google.com/p/pyci>
# For license information, see COPYING


"""TagSet templates
"""
__all__ = ["BETagSet", "BESTagSet", "BMESTagSet", "B123MESTagSet"]

from api import *

class BETagSet(TagSet):
    """A tag set distinguishes only whether the character is the head of the word.
    """

    def __init__(self):
        def tagger(word):
            res = []
            if word:
                res.append((word[0], 'B'))
            for i in word[1:]:
                res.append((i, 'E'))
            return res

        TagSet.__init__(self, ['B'], ['E'], tagger)


class BESTagSet(TagSet):
    """A tag set distinguishes only whether the character is the head of the word, or itself alone is a word.
    """

    def __init__(self):
        def tagger(word):
            if len(word) == 1:
                return [(word, 'S')]
            elif len(word) > 1:
                return [(word[0], 'B')] + [(i, 'E') for i in word[1:]]
            else:
                return []

        TagSet.__init__(self, ['B', 'S'], ['E'], tagger)


class BMESTagSet(TagSet):
    """Begin Middle End Single
    """

    def __init__(self):
        def tagger(word):
            if len(word) == 1:
                return [(word, 'S')]
            elif len(word) > 1:
                return [(word[0], 'B')] + [(i, 'M') for i in word[1:-1]] + [(word[-1], 'E')]
            else:
                return []

        TagSet.__init__(self, ['B', 'S'], ['M','E'], tagger)

    def untag(self, tagged_sent, strict=True, verbose=False):
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
            if verbose:
                print char, tag
            if tag in self.itags:
                if word:
                    yield word
                word = char
            elif tag == 'E':
                word += char
                yield word
                word = ""
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


class B123MESTagSet(TagSet):
    """Begin{1,2,3} Middle End Single
    """

    def __init__(self):
        def tagger(word):
            if len(word) == 1:
                return [(word, 'S')]
            elif len(word) > 1:
                res = [(word[0], 'B')]
                if len(word) == 2:
                    res.append( (word[1], 'E') )
                elif len(word) == 3:
                    res.extend([ (word[1], 'B1'), (word[2], 'E') ])
                else:
                    res.extend([ (word[1], 'B1'), (word[2], 'B2')] + \
                            [(i, 'M') for i in word[3:-1]] + [ (word[-1], 'E') ])
                return res
            else:
                return []

        TagSet.__init__(self, ['B', 'S'], ['B1', 'B2', 'M','E'], tagger)


def demo():
    print ":::DEMO for tagset/template.py:::"

    head_tail = BETagSet()
    head_tail_single = BESTagSet()
    bmes = BMESTagSet()
    b123mes = B123MESTagSet()

    sent = ['ABC', 'BAC', 'A', 'B', 'IDFSDF','SDWEOURO','DD','WERQ']
    print sent

    ts = BETagSet()
    print [i for i in ts.tag(sent)]
    print [i for i in ts.untag(ts.tag(sent))]

    ts = BESTagSet()
    print [i for i in ts.tag(sent)]
    print [i for i in ts.untag(ts.tag(sent))]

    ts = BMESTagSet()
    print [i for i in ts.tag(sent)]
    print [i for i in ts.untag(ts.tag(sent))]

    ts = B123MESTagSet()
    print [i for i in ts.tag(sent)]
    print [i for i in ts.untag(ts.tag(sent))]

if __name__ == "__main__":
    demo()
