# -*- coding: utf-8 -*-

# PyCi
#
# Copyright (c) 2009, The PyCi Project
# Authors: Wu Ke <ngu.kho@gmail.com>
#          Chen Xing <cxcxcxcx@gmail.com>
# URL: <http://code.google.com/p/pyci>
# For license information, see COPYING


"""
Brill tagger
"""
__all__ = ["BrillRuleTemplate", "BrillRule", "BrillTagger", "AtomicPredicate"]

from collections import defaultdict
from pprint import pprint

from entity import char_class, C_NUM, C_DATE, C_LETTER, C_OTHER

def my_print(*args):
    for n, i in enumerate(args):
        if len(str(i)) < 50:
            if n != len(args) - 1:
                print i,
            else:
                print i
        else:
            pprint(i)


class AtomicPredicate(object):
    """An atomic predicate is a predicate tests
    whether:

      * given offset has given tag or not
      * given offset is given character or not
      * given offset is in given character class or not

      An AtomicPredicate is comparable -- it's equal to any object
      having the identical repr().
    """

    def __init__(self, pred_offset, pred_type, pred_value, pred_not=False):
        """Construct an atomic predicate.

        @type pred_offset: integer
        @param pred_offset: the offset of the tuple to be tested

        @type pred_type: one of 'T', 'C', 'E'
        @param pred_type: test type, 'T' - tag; 'C' - character; 'E' -
        entity

        @type pred_value: depends on pred_type
        @param pred_value: test value

        @type pred_not: bool
        @param pred_not: whether to inverse the result
        """
        assert pred_type in ['T', 'C', 'E'], "Invalid pred_type"
        self.test_slot = (pred_offset, pred_type, pred_value, pred_not)

    def __str__(self):
        return "AtomicPredicate: " + str(self.test_slot)

    def __repr__(self):
        return "AtomicPredicate: " + repr(self.test_slot)

    def __cmp__(self, other):
        return cmp(repr(self), repr(other))

    def test(self, context, idx):
        o, t, v, n = self.test_slot
        res = True
        if idx + o >= 0 and idx + o < len(context):
            char, tag = context[idx + o]
            if t == "T":
                res = tag == v
            elif t == "C":
                res = char == v
            else:
                res = char_class(char) == v
        if n:
            res = not res
        return res


class BrillRule(object):
    """A rule for Brill tagger.

    It uses a combination of [[AtomicPrediate]] to test whether the
    rule is applicable.

    A BrillRule is hashable and comparable. It's equal to any object
    having the identical repr().
    """

    def __init__(self, from_tag, to_tag, test):
        """Construct a brill rule.

        @type from_tag: a tag from some tagset
        @param from_tag: from-tag of the rule

        @type to_tag: a tag from some tagset
        @param to_tag: to-tag of the rule

        @type test: a list of list of AtomicPredicates
        @param test: tests to trigger the rule, the predicates are
        tested in the following way:

          1. For each sublist i in test, it's true iff any of its
          element AtomicPredicate asserts true.

          2. For the whole list, it's true iff all the sublists are
          true.
        """
        self.from_tag = from_tag
        self.to_tag = to_tag
        self.test = test

    def applies(self, context, idx):
        return all([any([ap.test(context, idx) for ap in clause])
                    for clause in self.test])

    def __str__(self):
        return "BrillRule: " + str([self.from_tag, self.to_tag, self.test])

    def __repr__(self):
        return "BrillRule: " + repr([self.from_tag, self.to_tag, self.test])

    def __cmp__(self, other):
        return cmp(repr(self), repr(other))

    def __hash__(self):
        return hash(repr(self))


class BrillRuleTemplate(object):
    # TODO
    pass


class BrillTagger(object):
    """A brill tagger"""

    def __init__(self, tagset, initial_tagger, rules=[], trace=0):
        """Construct a brill tagger

        @type tagset: a TagSet instance
        @param tagset: the tag set we are using

        @type initial_tagger: a function which takes a unicode string
        and returns tuples of (character, tag)
        @param initial_tagger: the tagger that produces the coarse
        tagging, it should match the tagset given

        @type rules: orderd list of BrillRules
        @param rules: rules to apply after tagging with initial_tagger
        """
        self.tagset = tagset
        self.itag = initial_tagger
        self.rules = rules
        self.trace = trace
        if trace:
            my_print("__init__:")
            my_print("\ttagset:", tagset)
            my_print("\titag:", initial_tagger)
            my_print("\trules:", rules)

    def tag(self, sent):
        """Tag a sentence

        @type sent: a unicode string
        @param sent: the sentence to be tagged
        @return: a list of (character, tag) tuple
        """
        # we need to ensure that res is a list
        res = [i for i in self.itag(sent)]
        if self.trace:
            my_print("tag:")
            my_print("\tinit:", res)
        # construct the tag-to-index mapping for res
        tag_to_index = defaultdict(set)
        for idx, (character, tag) in enumerate(res):
            tag_to_index[tag].add(idx)
        # apply rules on res
        for rule in self.rules:
            # find out all changes
            changes = [i for i in tag_to_index[rule.from_tag]
                       if rule.applies(res, i)]
            if self.trace:
                my_print("\tapply rule:", rule)
                my_print("\t\tchange:", changes)
            # change their tags to rule.to_tag
            for i in changes:
                res[i] = (res[i][0], rule.to_tag)
                tag_to_index[rule.from_tag].remove(i)
                tag_to_index[rule.to_tag].add(i)
        # done
        if self.trace:
            my_print("\tfinal:", res)
        return res

    def train(self, train, rule_templates, max_rules, min_score):
        """Train with given rule templates

        @type train: a list of (character, tag) tuples
        @param train: the training corpus

        @type rule_templates: a list of BrillRuleTemplate
        @param rule_templates: the rule templates to be used

        @type max_rules: integer
        @param max_rules: maximum number of rules to be used

        @type min_score: integer
        @param min_score: mininum improvement score a rule should get
        """
        # `declaration', these are to be used in helper functions
        trace = self.trace
        res = []
        tag_to_index = defaultdict(set)
        error_idx = defaultdict(set)
        correct_idx = defaultdict(set)

        if trace:
            my_print("train:")

        # helper functions, classes
        class HelperRule(object):
            """A helper for rule. Saves information needed in
            find_possible_rules and find_best_rule.
            """

            def __init__(self, rule):
                self.rule = rule
                self.correct_iter = iter(correct_idx[rule.from_tag])
                self.score = 0
                # find changes for error_idx[rule.from_tag]
                self.changes = [i for i in error_idx[rule.from_tag]
                                if rule.applies(res, i)]
                # calculate our score for fixing those errors
                for i in self.changes:
                    if train[i][1] == rule.to_tag:
                        # we are right
                        self.score += 1
                    else:
                        # we are wrong but it does not hurt. at least
                        # we are not bringing new errors.
                        pass
                if trace:
                    my_print("HelperRule@0x%08x" % id(self))
                    my_print("\trule:", self.rule)
                    my_print("\tscore:", self.score)
                    my_print("\tchanges:", self.changes)

        def generate_rules(idx):
            if trace:
                my_print("generate_rules(%d)" % idx)
            from_tag = res[idx][1]
            to_tag = train[idx][1]
            ans = [i.form_rule(from_tag, to_tag, res, idx)
                   for i in rule_templates]
            if trace:
                my_print("generate_rules:")
                my_print("\t", ans)
            return ans

        def find_possible_rules():
            score_to_rules = defaultdict(set)
            rule_to_helper = {} # one rule <=> one helper
            max_score = 0
            for wrong_tag in error_idx:
                for idx in error_idx[wrong_tag]:
                    for rule in generate_rules(idx):
                        if rule in rule_to_helper:
                            # already have that rule, skipping
                            continue
                        helper = HelperRule(rule)
                        if helper.score >= min_score:
                            score_to_rules[helper.score].add(rule)
                            rule_to_helper[rule] = helper
                        if helper.score >= max_score:
                            max_score = helper.score
            if trace:
                my_print("find_possible_rules:")
                my_print("\tmax_score:", max_score)
                my_print("\trules:", len(rule_to_helper))
                my_print("\tscore_to_rules", dict(score_to_rules))
            return score_to_rules, rule_to_helper, max_score

        def find_best_rule(score_to_rules, rule_to_helper, max_score):
            # we find the best rule in the following way:
            #
            # 1. for each rule helper, we store the rule's changes and
            # its score.
            #
            # 2. treat score_to_rules like below,
            #
            # scores      rules
            #   x    -->  [...]
            #  x-1   -->  [...]
            #  x-2   -->  [...]
            #  ...   -->   ...
            #  min   -->  [...]
            #
            # 3. since we have `made' all changes to errors in
            # find_possible_rules, all the changes we are going to
            # make are on the correctly tagged characters -- that is
            # to say, we are not going to improve any score, only
            # lowering them.
            #
            # 4. so the algorithm goes like this:
            #
            # a. find a rule with currently maximum score, apply it to
            # any appliable correct indices.
            #
            # b. if the rule does not make any more changes to the
            # correct tags, it's the best rule, return it.
            #
            # c. otherwise, keep making mistakes and decreasing its
            # score till it no more has the highest score.
            #
            # d. repeat, someday we will reach stage b.
            if trace:
                my_print("find_best_rule:")
            while max_score >= min_score:
                # take a max_score rule
                rule = score_to_rules[max_score].pop()
                if trace:
                    my_print("\trule:", rule)
                    my_print("\tmax_score:", max_score)
                # and its helper
                helper = rule_to_helper[rule]
                # just in case
                assert rule == helper.rule, \
                       "rule and the rule in its helper do not match"
                assert helper.score == max_score, \
                       "helper's score in wrong"
                # till it's no more the best
                while True:
                    # make the miserable mistake
                    try:
                        idx = helper.correct_iter.next()
                        if rule.applies(res, idx):
                            if trace:
                                my_print("\t", rule, "made a mistake @", idx)
                            helper.changes.append(idx)
                            helper.score -= 1
                            score_to_rules[helper.score].add(rule)
                            break
                    except StopIteration:
                        if trace:
                            my_print("\trule:", rule, "score:", helper.score)
                        return rule, helper.score, helper
                # find the new max_score
                while len(score_to_rules[max_score]) == 0:
                    max_score -= 1
            if trace:
                my_print("\tI am sorry...")
            return None, max_score, None

        # tag raw sentence with our initial tagger, make sure res is a
        # list
        res = [i for i in self.itag(''.join([i[0] for i in train]))]
        # # construct the tag-to-index mapping for res
        # for idx, (character, tag) in enumerate(res):
        #     tag_to_index[tag].add(idx)
        # find out all error and correct indices
        for idx, (character, tag) in enumerate(res):
            if tag == train[idx][1]:
                correct_idx[tag].add(idx)
            else:
                error_idx[tag].add(idx)
        if trace:
            my_print("train: ", [(res[i][0], train[i][1], res[i][1])
                              for i in range(len(res))])
            my_print("error:", dict(error_idx))
            my_print("correct:", dict(correct_idx))
        # new rule list
        rules = []
        while len(rules) <= max_rules:
            score_to_rules, rule_to_helper, max_score = find_possible_rules()
            if max_score >= min_score:
                rule, score, helper = find_best_rule(score_to_rules,
                                                     rule_to_helper,
                                                     max_score)
                if score >= min_score:
                    # commit changes
                    for i in helper.changes:
                        # update error_idx, correct_idx
                        if rule.from_tag != train[i][1]:
                            # we used to get it wrong, it might be
                            # still wrong. or when we're lucky, it's
                            # correct.
                            error_idx[res[i][1]].remove(i)
                            if rule.to_tag == train[i][1]:
                                # we got it correct!
                                correct_idx[rule.to_tag].add(i)
                            else:
                                # we got it wrong...
                                error_idx[rule.to_tag].add(i)
                        else:
                            # it was correct, now it's surely wrong
                            correct_idx[rule.from_tag].remove(i)
                            error_idx[rule.to_tag].add(i)
                        # finally, change the tag in res
                        res[i] = (res[i][0], rule.to_tag)
                    # add it to rules
                    rules.append(rule)
                    if trace:
                        my_print("train: ", [(res[i][0], train[i][1], res[i][1])
                                          for i in range(len(res))])
                        my_print("error:", dict(error_idx))
                        my_print("correct:", dict(correct_idx))
                else:
                    break
            else:
                break
        # done
        self.rules = rules




def demo():
    from tagset.template import BESTagSet
    bes = BESTagSet()

    class DummyRule:
        def __init__(self, from_tag, to_tag, test):
            self.from_tag = from_tag
            self.to_tag = to_tag
            self.test = test
        def __str__(self):
            return str([self.from_tag, self.to_tag, self.test])
        def __repr__(self):
            return repr([self.from_tag, self.to_tag, self.test])
        def __hash__(self):
            return hash(str(self))
        def __cmp__(self, other):
            if type(self) is type(other):
                return cmp(str(self), str(other))
            else:
                return 1
        def applies(self, res, idx):
            if res[idx][1] != self.from_tag:
                return False
            for pos, tag in self.test:
                if idx + pos >= 0 and idx + pos < len(res):
                    if res[idx + pos][1] != tag:
                        return False
            return True

    my_print("Test DummyRule")
    bb_to_sb = DummyRule('B', 'S', [(1, 'B')])
    se_to_sb = DummyRule('E', 'B', [(-1, 'S')])

    test = [('0', 'S'), ('1', 'E'), ('2', 'B'), ('3', 'B')]
    ans1 = [False, False, True, True]
    ans2 = [False, True, False, False]

    my_print(test)
    for i, (c, t) in enumerate(test):
        my_print(i, (c, t))

        assert bb_to_sb.applies(test,i ) == ans1[i]
        my_print("\tbb_to_sb:")
        if bb_to_sb.applies(test, i):
            my_print("yes")
        else:
            my_print("no")

        assert se_to_sb.applies(test, i) == ans2[i]
        my_print("\tse_to_sb:",)
        if se_to_sb.applies(test, i):
            my_print("yes")
        else:
            my_print("no")

    class DummyTemplate:
        def __init__(self, test_pos):
            self.test_pos = test_pos
        def form_rule(self, from_tag, to_tag, res, idx):
            assert res[idx][1] == from_tag
            test = []
            for i in self.test_pos:
                if idx + i >= 0 and idx + i < len(res):
                    test.append((i, res[idx + i][1]))
            return DummyRule(from_tag, to_tag, test)

    my_print("\nTest DummyTemplate")

    t1 = DummyTemplate([-1])
    t2 = DummyTemplate([1])

    r11 = t1.form_rule('S', 'B', test, 0)
    assert r11.test == []
    my_print(r11)

    r12 = t1.form_rule('E', 'B', test, 1)
    assert r12.test == [(-1, 'S')]
    my_print(r12)

    r21 = t2.form_rule('B', 'S', test, 2)
    assert r21.test == [(1, 'B')]
    my_print(r21)

    r22 = t2.form_rule('B', 'E', test, 3)
    assert r22.test == []
    my_print(r22)

    my_print("\nTest Brill trainer")

    templates = [t1, t2]
    train = [i for i in bes.tag(["This", "is", "a", "test", "."])]
    def stupid_tagger(sent):
        return [(i, "S") for i in sent]

    brill = BrillTagger(bes, stupid_tagger, trace=False)
    brill.train(train, templates, 20, 0)
    my_print(brill.rules)
    my_print(brill.tag("This is a test."))

    my_print("\nTest AtomicPredicate")

    ap0 = AtomicPredicate(0, 'T', 'B')
    ap1 = AtomicPredicate(0, 'T', 'B')
    ap2 = AtomicPredicate(1, 'C', '0', True)
    ap3 = AtomicPredicate(-1, 'E', C_NUM)

    assert ap1.test([('1', 'B')], 0) is True
    assert ap1.test([('1', 'C')], 0) is False

    assert ap2.test([('1', 'B'), ('2', 'C')], 0) is True
    assert ap2.test([('1', 'B')], 0) is False
    assert ap2.test([('1', 'B'), ('0', 'C')], 0) is False

    assert ap3.test([('1', 'B')], 1) is True
    assert ap3.test([('L', 'B')], 1) is False

    assert ap0 == ap1
    assert ap0 != ap2

    my_print("pass")

    my_print("\nTest BrillRule")

    test = [("T", "S"), ("1", "E"), ("0", "B")]

    r0 = BrillRule(None, None, [[ap1], [ap2], [ap3]])
    r1 = BrillRule(None, None, [[ap1, ap2], [ap3]])
    r2 = BrillRule(None, None, [[ap1], [ap2, ap3]])
    r3 = BrillRule(None, None, [[ap1, ap2], [ap3]])

    assert r1 == r3
    assert r1 != r2

    d = {r0: 0, r1: 1, r2:2}
    assert d[r3] == d[r1]
    s = set([r0, r1, r2, r3])
    assert len(s) == 3

    print test
    for i in range(len(test)):
        print test[i]
        print ap1.test(test, i), ap2.test(test, i), ap3.test(test, i)
        print r0.applies(test, i)
        print r1.applies(test, i)
        print r2.applies(test, i)


if __name__ == "__main__":
    demo()
