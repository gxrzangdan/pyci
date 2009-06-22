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

from collections import defaultdict
import entity

class BrillRuleTemplate(object):
    pass


class BrillRule(object):
    pass


class BrillTagger(object):
    """A brill tagger"""

    def __init__(self, tagset, initial_tagger, rules=[]):
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

    def tag(self, sent):
        """Tag a sentence

        @type sent: a unicode string
        @param sent: the sentence to be tagged
        @return: a list of (character, tag) tuple
        """
        # we need to ensure that res is a list
        res = [i for i in self.itag(sent)]
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
        # done
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
        res = []
        tag_to_index = defaultdict(set)
        error_idx = defaultdict(set)
        correct_idx = defaultdict(set)

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
            while True:
                # take a max_score rule
                rule = score_to_rules[max_score].pop()
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
                            helper.changes.append(idx)
                            helper.score -= 1
                            score_to_rules[helper.score].add(rule)
                    except StopIteration:
                        return rule, score, helper
                # find the new max_score
                while len(score_to_rules[max_score]) == 0:
                    max_score -= 1
            assert 0, "You shouldn't be here"

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
                        res[i] = (res[i][0], new_rule.to_tag)
                    rules.append(new_rule)
                else:
                    break
            else:
                break
        # done
        return rules




def demo():
    from tagset.template import BETagSet
    be = BETagSet()

    class FakeRule:
        def __init__(self, from_tag, to_tag):
            self.from_tag = from_tag
            self.to_tag = to_tag
            self.applies = lambda x, y: True

    b_to_e = FakeRule('B', 'E')
    e_to_b = FakeRule('E', 'B')

    btag = BrillTagger(be, be.tag, [b_to_e])
    print btag.tag(['this', 'is', 'a', 'test'])

    btag = BrillTagger(be, be.tag, [b_to_e, e_to_b])
    print btag.tag(['this', 'is', 'a', 'test'])


if __name__ == "__main__":
    demo()
