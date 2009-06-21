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

class HeadTailTagSet(TagSet):
    """A tag set distinguishes only whether the character is the head of the word.
    """

    def __init__(self):
        def head_tail_tagger(word):
            res = []
            if word:
                res.append((word[0], 'H'))
            for i in word[1:]:
                res.append((i, 'T'))
            return res

        TagSet.__init__(self, ['H'], ['T'], head_tail_tagger)


class HeadTailSingleTagSet(TagSet):
    """A tag set distinguishes only whether the character is the head of the word, or itself alone is a word.
    """

    def __init__(self):
        def head_tail_single_tagger(word):
            if len(word) == 1:
                return [(word, 'S')]
            elif len(word) > 1:
                return [(word[0], 'H')] + [(i, 'T') for i in word[1:]]
            else:
                return []

        TagSet.__init__(self, ['H', 'S'], ['T'], head_tail_single_tagger)

def demo():
    head_tail = HeadTailTagSet()
    head_tail_single = HeadTailSingleTagSet()
    sent = ['ABC', 'BAC', 'A', 'B']
    print sent
    print [i for i in head_tail.tag(sent)]
    print [i for i in head_tail.untag(head_tail.tag(sent))]
    print [i for i in head_tail_single.tag(sent)]
    print [i for i in head_tail_single.untag(head_tail_single.tag(sent))]

if __name__ == "__main__":
    demo()
