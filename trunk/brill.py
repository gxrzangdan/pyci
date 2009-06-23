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
    T_TAG = "TAG"
    T_CLASS = "CLASS"
    T_CHAR = "CHAR"

    def __init__(self, pred_offset, pred_type, pred_value, pred_not=False):
        """Construct an atomic predicate.

        @type pred_offset: integer
        @param pred_offset: the offset of the tuple to be tested

        @type pred_type: one of T_TAG, T_CLASS, T_CHAR
        @param pred_type: test type

          * T_TAG - tag;
          * T_CLASS - character;
          * T_CHAR - entity.

        @type pred_value: depends on pred_type
        @param pred_value: test value

        @type pred_not: bool
        @param pred_not: whether to inverse the result
        """
        assert pred_type in [self.T_TAG, self.T_CLASS, self.T_CHAR], \
               "Invalid pred_type"
        self._test = (pred_offset, pred_type, pred_value, pred_not)

    def offset(self):
        return self._test[0]

    def type_value(self):
        return (self._test[1], self._test[2])

    def inverse(self):
        return self._test[3]

    def __str__(self):
        return "AtomicPredicate: " + str(self._test)

    def __repr__(self):
        return "AtomicPredicate: " + repr(self._test)

    def __cmp__(self, other):
        return cmp(repr(self), repr(other))

    def test(self, context, idx):
        """Test the predicate under context.

        @type context: a list of (character, tag) tuples.
        @param context: the context

        @type idx: integer
        @param idx: the index to the context

        @return: the value of the predicate
        """
        o, t, v, n = self._test
        res = True
        if idx + o >= 0 and idx + o < len(context):
            char, tag = context[idx + o]
            if t == self.T_TAG:
                res = tag == v
            elif t == self.T_CHAR:
                res = char == v
            else:
                res = char_class(char) == v
        if n:
            res = not res
        return res


class BrillRule(object):
    """A rule for Brill tagger.

    It uses a combination of [[AtomicPredicate]] to test whether the
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

        @type test: an iterable of iterable of AtomicPredicates
        @param test: tests to trigger the rule, the predicates are
        tested in the following way:

          1. For each sublist i in test, i is true iff any of its
          elemental AtomicPredicate asserts true.

          2. For the whole list, it's true iff all the sublists are
          true.
        """
        self.from_tag = from_tag
        self.to_tag = to_tag
        self._test = sorted(test) # so that we can discover more
                                  # identical rules

    def applies(self, context, idx):
        """Check whether the rule applies to the context

        @type context: a list of (character, tag) tuples.
        @param context: the context.

        @type idx: integer.
        @param idx: the index to the context.
        """
        return all([any([ap.test(context, idx) for ap in clause])
                    for clause in self._test])

    def __str__(self):
        return "BrillRule: " + str([self.from_tag, self.to_tag, self._test])

    def __repr__(self):
        return "BrillRule: " + repr([self.from_tag, self.to_tag, self._test])

    def __cmp__(self, other):
        return cmp(repr(self), repr(other))

    def __hash__(self):
        return hash(repr(self))


class BrillRuleTemplate(object):
    """Template for generating Brill rules.

    With given from-tag and to-tag, the form_rule method will return a
    BrillRule with corresponding test.
    """

    def __init__(self, test):
        """Construct a template for generating Brill rules.

        @type test: a list of list of (offset, type)

        @param test: tests used to construct rules
        """
        # TODO: how do we support pred_not = False?
        self._test = test

    def __str__(self):
        return "BrillRuleTemplate: " + str(self._test)

    def __repr__(self):
        return "BrillRuleTemplate: " + repr(self._test)

    def form_rule(self, from_tag, to_tag, res, idx):
        """Form a BrillRule with given from-tag and to-tag which
        corrects the error in res[idx].

        @type from_tag: a tag from some tagset.
        @param from_tag: from-tag, must match the tag in res[idx].

        @type to_tag: a tag from some tagset.
        @param to_tag: to-tag, must be different from from_tag.

        @type res: a list of (character, tag) tuples.
        @param res: the currently tagged result(context).

        @type idx: integer.
        @param idx: the index to the res.
        """
        def value(context, idx, ptype):
            if ptype == AtomicPredicate.T_TAG:
                return context[idx][1]
            elif ptype == AtomicPredicate.T_CHAR:
                return context[idx][0]
            else:
                return char_class(context[idx][0])
        # first ensure the tag integrity
        assert from_tag != to_tag, "from_tag == to_tag"
        assert from_tag == res[idx][1], \
               "from_tag and the tag in context does not match"
        # then test we can reach all the offsets in self._test
        for clause in self._test:
            for offset, ptype in clause:
                if idx + offset < 0 or \
                   idx + offset >= len(res):
                    # the offset of ap cannot be reached, no rule will
                    # be formed.
                    return None
        test = []
        for clause in self._test:
            new_clause = []
            for offset, ptype in clause:
                new_clause.append(AtomicPredicate(offset, ptype,
                                                  value(res, idx + offset,
                                                        ptype)))
            test.append(new_clause)
        return BrillRule(from_tag, to_tag, test)


class UnigramBrillRuleTemplate(BrillRuleTemplate):
    def __init__(self, offset, ptype):
        BrillRuleTemplate.__init__(self, [[(offset, ptype)]])


class BigramBrillRuleTemplate(BrillRuleTemplate):
    def __init__(self, op1, op2):
        BrillRuleTemplate.__init__(self, [[op1], [op2]])


class TrigramBrillRuleTemplate(BrillRuleTemplate):
    def __init__(self, op1, op2, op3):
        BrillRuleTemplate.__init__(self, [[op1], [op2], [op3]])


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
            # change their tags to rule.to_tag
            for i in changes:
                res[i] = (res[i][0], rule.to_tag)
                tag_to_index[rule.from_tag].remove(i)
                tag_to_index[rule.to_tag].add(i)
            if self.trace:
                my_print("\tapply rule:", rule)
                my_print("\t\tchange:", changes)
                my_print("\t\t", res)
        # done
        if self.trace:
            my_print("\tfinal:", res)
        return res

    def train(self, train, rule_templates, max_rules, min_score, verbose=False):
        """Train with given rule templates

        @type train: list of words
        @param train: the training corpus

        @type rule_templates: a list of BrillRuleTemplate
        @param rule_templates: the rule templates to be used

        @type max_rules: integer
        @param max_rules: maximum number of rules to be used

        @type min_score: integer
        @param min_score: mininum improvement score a rule should get

        @type verbose: bool
        @param verbose: whether to give verbose output during training
        """
        # `declaration', these are to be used in helper functions
        trace = self.trace
        if trace:
            verbose = True
        res = []
        tag_to_index = defaultdict(set)
        error_idx = defaultdict(set)
        correct_idx = defaultdict(set)
        train = [i for i in self.tagset.tag(train)]
        rules_set = set()

        if verbose:
            print "Training corpus loaded, %d characters" % len(train)
            print "Using %d templates" % len(rule_templates)

        if trace:
            my_print("train:")

        # helper functions, classes
        class HelperRule(object):
            """A helper for rule. Saves information needed in
            find_possible_rules and find_best_rule.
            """

            def __init__(self, rule, trace=False):
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

        def generate_rules(idx, trace=False):
            if trace:
                my_print("generate_rules(%d)" % idx)
            from_tag = res[idx][1]
            to_tag = train[idx][1]
            ans = [i for i in
                   [i.form_rule(from_tag, to_tag, res, idx)
                    for i in rule_templates]
                   if i]
            if trace:
                my_print("generate_rules: %d rules" % len(ans))
                my_print("\t", ans)
            return ans

        def find_possible_rules():
            score_to_rules = defaultdict(set)
            rule_to_helper = {} # one rule <=> one helper
            max_score = 0
            for wrong_tag in error_idx:
                if verbose:
                    print "Tag:", wrong_tag,
                    count = 1
                for idx in error_idx[wrong_tag]:
                    if verbose:
                        print "\rTag:", wrong_tag, "%3.0f%%" % (count * 100.0 / len(error_idx[wrong_tag])),
                        count += 1
                    for rule in generate_rules(idx):
                        if rule in rule_to_helper or rule in rules_set:
                            # already have that rule, skipping
                            continue
                        helper = HelperRule(rule)
                        if helper.score >= min_score:
                            score_to_rules[helper.score].add(rule)
                            rule_to_helper[rule] = helper
                        if helper.score >= max_score:
                            max_score = helper.score
                if verbose:
                    print ""
            if trace:
                my_print("find_possible_rules:")
                my_print("\tmax_score:", max_score)
                my_print("\trules:", len(rule_to_helper))
                # my_print("\tscore_to_rules", dict(score_to_rules))
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
                if verbose:
                    print "\rCurrently best score:", max_score,
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
                                my_print("\tmade a mistake @", idx)
                            helper.changes.append(idx)
                            helper.score -= 1
                            score_to_rules[helper.score].add(rule)
                            break
                    except StopIteration:
                        if trace:
                            my_print("\n\trule:", rule, "score:", helper.score)
                        if verbose:
                            print ""
                        return rule, helper.score, helper
                # find the new max_score
                while len(score_to_rules[max_score]) == 0:
                    max_score -= 1
            if trace:
                my_print("\tI am sorry...")
            if verbose:
                print ""
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
        if verbose:
            print "After initial tagging, we have %d errors" % \
                  sum([len(error_idx[i]) for i in error_idx])
        if trace:
            my_print("train: ", [(res[i][0], train[i][1], res[i][1])
                              for i in range(len(res))])
            my_print("error:", dict(error_idx))
            my_print("correct:", dict(correct_idx))
        # new rule list
        rules = []
        while len(rules) <= max_rules:
            if verbose:
                print "Looking for possible rules"
            score_to_rules, rule_to_helper, max_score = find_possible_rules()
            if max_score >= min_score:
                if verbose:
                    print "Found %d possible rules" % len(rule_to_helper)
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
                    rules_set.add(rule)
                    if trace:
                        my_print("after commit train: ",
                                 [(res[i][0], train[i][1], res[i][1])
                                  for i in range(len(res))])
                        my_print("error:", dict(error_idx))
                        my_print("correct:", dict(correct_idx))
                    if verbose:
                        print rule, "added"
                        print "Now %d errors (%d corrections)" % \
                              (sum([len(error_idx[i]) for i in error_idx]),
                               score)

                else:
                    if verbose:
                        print "No rule has enough score"
                    break
            else:
                break
        # done
        if verbose:
            print "Training complete"
            print "New rule size: %d\n" % len(rules)
        self.rules = rules




def demo(test=False):
    from tagset.template import BESTagSet
    bes = BESTagSet()

    if test:
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

    if test:
        brill = BrillTagger(bes, stupid_tagger, trace=False)
        brill.train(train, templates, 20, 0)
        my_print(brill.rules)
        my_print(brill.tag("This is a test."))

        my_print("\nTest AtomicPredicate")

        ap0 = AtomicPredicate(0, AtomicPredicate.T_TAG, 'B')
        ap1 = AtomicPredicate(0, AtomicPredicate.T_TAG, 'B')
        ap2 = AtomicPredicate(1, AtomicPredicate.T_CHAR, '0', True)
        ap3 = AtomicPredicate(-1, AtomicPredicate.T_CLASS, C_NUM)

        assert ap1.test([('1', 'B')], 0) is True
        assert ap1.test([('1', 'C')], 0) is False

        assert ap2.test([('1', 'B'), ('2', 'C')], 0) is True
        assert ap2.test([('1', 'B')], 0) is False
        assert ap2.test([('1', 'B'), ('0', 'C')], 0) is False

        assert ap3.test([('1', 'B')], 1) is True
        assert ap3.test([('L', 'B')], 1) is False

        assert ap0 == ap1
        assert ap0 != ap2

        my_print("OK")

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

        my_print("\nTest BrillRuleTemplate")

        train = [('T', 'B'), ('h', 'E'), ('i', 'E'), ('s', 'E'), (' ', 'S'), ('i', 'B'), ('s', 'E'), (' ', 'S'), ('a', 'S'), (' ', 'S'), ('t', 'B'), ('e', 'E'), ('s', 'E'), ('t', 'E'), ('.', 'S')]

        back1tag = BrillRuleTemplate([[(-1, AtomicPredicate.T_TAG)]])
        ahead1tag = BrillRuleTemplate([[(1, AtomicPredicate.T_TAG)]])
        back1class_ahead1char = BrillRuleTemplate([[(-1, AtomicPredicate.T_CLASS)], [(1, AtomicPredicate.T_CHAR)]])

        for i, (char, tag) in enumerate(train):
            my_print(i, (char, tag))
            my_print(back1tag.form_rule(tag, 'X', train, i))
            my_print(ahead1tag.form_rule(tag, 'X', train, i))
            my_print(back1class_ahead1char.form_rule(tag, 'X', train, i))
            print ""

        my_print("\nTest Everything")

    train = ["This", " ", "is", " ", "a", "test", "."]
    test = "This is not a test."

    brill = BrillTagger(bes, stupid_tagger)
    brill.train(train, [
        # unigram
        UnigramBrillRuleTemplate(-1, AtomicPredicate.T_TAG),
        UnigramBrillRuleTemplate(1, AtomicPredicate.T_TAG),
        UnigramBrillRuleTemplate(-1, AtomicPredicate.T_CHAR),
        UnigramBrillRuleTemplate(1, AtomicPredicate.T_CHAR),
        # bigram
        BigramBrillRuleTemplate((-1, AtomicPredicate.T_TAG),
                                (1, AtomicPredicate.T_TAG)),
        BigramBrillRuleTemplate((-1, AtomicPredicate.T_CHAR),
                                (1, AtomicPredicate.T_CHAR))],
                20, 1, True)
    print "Our rules:"
    for rule in brill.rules:
        print rule
    print "Let's try"
    tagged_test = brill.tag(test)
    print [i for i in bes.untag(tagged_test)]



if __name__ == "__main__":
    demo()
