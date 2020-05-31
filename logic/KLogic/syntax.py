#!/usr/bin/python

from ..CTFLogic import syntax

import re
from enum import Enum

# monadic operators
NEC = "◻"
POSS = "◇"
UNARY_CONNECTIVES = syntax.UNARY_CONNECTIVES + [NEC, POSS]


class KForm(Enum):
    ATOMIC = 0
    NEGATION = syntax.NOT
    CONJUNCTION = syntax.AND
    DISJUNCTION = syntax.OR
    CONDITIONAL = syntax.COND
    BICONDITIONAL = syntax.BICOND
    NECESSARY = NEC
    POSSIBLE = POSS


def get_form(s):
    for i in KForm:
        if i._value_ == s:
            form = i
            break
    return form


class KFormula(syntax.Formula):
    def get_atomic(self, s):
        if re.match(syntax.re_pattern(syntax.ATOMICS), s):
            return (s, KForm.ATOMIC, None)
        else:
            return False

    def get_unary_connective(self, s):
        if re.match(syntax.re_pattern(UNARY_CONNECTIVES), s[0]):
            form = get_form(s[0])
            return (s, form, [KFormula(s[1:])])
        else:
            return False

    def get_binary_connective(self, s):
        connected = self.find_binary_connector(s)
        if connected:
            left = KFormula(connected[0])
            right = KFormula(connected[1])
            connector = connected[2]
            return (s, self.get_form(connector), [left, right])
        else:
            return False

    def get_form(self, s):
        for i in KForm:
            if i._value_ == s:
                form = i
                break
        return form
