# -*- coding: utf-8 -*-

# PyCi
#
# Copyright (c) 2009, The PyCi Project
# Authors: Wu Ke <ngu.kho@gmail.com>
#          Chen Xing <cxcxcxcx@gmail.com>
# URL: <http://code.google.com/p/pyci>
# For license information, see COPYING


"""Trie data structure for fast dictionary look-up
"""

class Trie(object):
    """Trie is a data structure ideal for fast dictionary look-up.
    For details, see http://en.wikipedia.org/wiki/Trie
    """

    def __init__(self, keys, value=lambda x:0):
        """Construct a trie from keys.

        @type keys: random accessible object with hashable elements
        @param keys: keys from which the trie is constructed
        @type value: callable
        @param value: method to get values from keys, default sets
        everything to 0
        """
        self._trie_root = TrieNode(None)
        for i in keys:
            self._trie_root.insert(i, value(i))

    def __getitem__(self, key):
        return self._trie_root.lookup(key)

    def __setitem__(self, key, value):
        return self._trie_root.insert(key, value)

    def longest_prefix(self, seq):
        """Find the longest prefix of seq that is in the trie.

        @type seq: random accessible object with hashable elements
        @param seq: from where the longest prefix will be extracted
        """
        return self._trie_root.longest_prefix(seq)


class TrieNode(object):
    """A node for a trie -- you should use class Trie to access data
    stored here.
    """

    # FIXME: first, rest in insert, longest_prefix, lookup is SLOW

    def __init__(self, label):
        """Construct a trie node with label.

        @type label: hashable
        @param label: the label for this trie node
        """
        self._label = label
        self._child = {}
        self._value = None

    def insert(self, key, value):
        """Insert a node with key, if the node already exists, update
        its value.

        @type key: random accessible object of hashable elements
        @param key: the key for updating
        @type value: anything you like
        @param value: the value for the key
        """
        if not key:
            self._value = value
        else:
            first = key[0]
            rest = key[1:]
            if first not in self._child:
                self._child[first] = TrieNode(first)
            self._child[first].insert(rest, value)

    def lookup(self, key):
        """Lookup a node with key.

        @type key: random accessible object of hashable elements
        @param key: the key for updating
        @return: the value
        """
        if not key:
            return self._value
        else:
            first = key[0]
            rest = key[1:]
            if first not in self._child:
                raise KeyError
            return self._child[first].lookup(rest)

    def longest_prefix(self, seq):
        """Find the longest prefix of seq starting at this node.

        @seq: random accessible object with hashable elements
        @param seq: from where the longest prefix will be extracted
        """
        if not seq:
            return self._label
        else:
            first = seq[0]
            rest = seq[1:]
            if first not in self._child:
                return self._label
            elif self._label:
                return self._label + self._child[first].longest_prefix(rest)
            else:
                return self._child[first].longest_prefix(rest)


if __name__ == "__main__":
    # demo
    from corpus import rmrb
    words = [i for i in rmrb.words()]
    trie = Trie(words)
    sent = raw_input("Give me a sentence: ").decode("utf8")
    pref = trie.longest_prefix(sent)
    print pref
    print trie[pref]
    trie[pref] = 1234
    print trie[pref]
