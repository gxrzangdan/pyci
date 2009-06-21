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
__all__ = ['head_tail_tagger', 'head_tail', 'head_tail_single_tagger', 'head_tail_single']

from api import *

class BETagSet(TagSet):
    """A tag set distinguishes only whether the character is the head of the word.
    """

    def __init__(self):
        def tagger(word):
            res = []
            if word:
                res.append((word[0], 'H'))
            for i in word[1:]:
                res.append((i, 'T'))
            return res

        TagSet.__init__(self, ['H'], ['T'], tagger)


class BESTagSet(TagSet):
    """A tag set distinguishes only whether the character is the head of the word, or itself alone is a word.
    """

    def __init__(self):
        def tagger(word):
            if len(word) == 1:
                return [(word, 'S')]
            elif len(word) > 1:
                return [(word[0], 'H')] + [(i, 'T') for i in word[1:]]
            else:
                return []

        TagSet.__init__(self, ['H', 'S'], ['T'], tagger)


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
