#!/usr/bin/python

import re
from enum import Enum

# sentence letters / propositional variables
SENLETTER = "[a-uw-zA-Z]"  # not v, we will use it as or sign
ATOMICS = [SENLETTER]
# parentheses
LPAREN = "[(]"
RPAREN = "[)]"
# unary Connectives
NOT = "¬"
UNARY_CONNECTIVES = [NOT]
# binary Connectives
AND = "∧"
OR = "∨"
COND = "→"
BICOND = "↔"
BINARY_CONNECTIVES = [AND, OR, COND, BICOND]

# distinction used for proof systems
PRIMITIVE_CONNECTIVES = [NOT, AND]
DEFINED_CONNECTIVES = [OR, COND, BICOND]

# alternative symbols
variants = {
    NOT: "~",
    AND: "&",
    OR: "v",
    BICOND: "(<->)|(≡)|(⇿)",  # put before COND
    COND: "(->)|(⊃)|(⇾)"
}


class Form(Enum):
    ATOMIC = 0
    NEGATION = NOT
    CONJUNCTION = AND
    DISJUNCTION = OR
    CONDITIONAL = COND
    BICONDITIONAL = BICOND


def re_pattern(lookup, anywhere=False):
    con_pattern = "^(" if not anywhere else "("
    for c in lookup[:-1]:
        con_pattern += f'{c}|'
    con_pattern += f'{lookup[-1]}'
    con_pattern += ")$" if not anywhere else ")"
    return con_pattern


def prepare_string(s):
    for key, value in variants.items():
        s = re.sub(value, key, s)
    return s


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class NotWellFormedFormulaError(Error):
    """Is not a well formed formula."""
    pass


class Formula():
    def __init__(self, s: str, form=None, subformulas=None):
        if form and subformulas:
            self.string = prepare_string(s)
            self.form = form
            self.subformulas = subformulas
        else:
            wff = self.wellformed(s, True)
            self.string = wff[0]
            self.form = wff[1]
            self.subformulas = wff[2]

    def get_form(self, s):
        for i in Form:
            if i._value_ == s:
                form = i
                break
        return form

    def __eq__(self, other):
        return self.string == other.string

    def wellformed(self, s, prepare=False):
        if prepare:
            s = prepare_string(s)
        if s == "":
            raise NotWellFormedFormulaError()
        r = (self.get_atomic(s) or
             self.get_unary_connective(s) or
             self.get_binary_connective(s))
        if r:
            res = r
        else:
            # is neither a well-formed atomic, nor unary, not binary
            # (considering also all subformulas)
            raise NotWellFormedFormulaError()
        return res

    def get_atomic(self, s):
        if re.match(re_pattern(ATOMICS), s):
            return (s, Form.ATOMIC, None)
        else:
            return False

    def get_unary_connective(self, s):
        if re.match(re_pattern(UNARY_CONNECTIVES), s[0]):
            form = self.get_form(s[0])
            return (s, form, [Formula(s[1:])])
        else:
            return False

    def get_binary_connective(self, s):
        connected = self.find_binary_connector(s)
        if connected:
            left = Formula(connected[0])
            right = Formula(connected[1])
            connector = connected[2]
            return (s, self.get_form(connector), [left, right])
        else:
            return False

    def find_binary_connector(self, s):
        paren_count, pos = 0, -1
        connective_pos = -1
        for c in s:
            pos += 1
            if re.match(f'^{LPAREN}$', c):
                # add one depth (new parenthesis group)
                paren_count += 1
            elif re.match(f'^{RPAREN}$', c):
                # close a parenthesis group
                paren_count -= 1
            if re.match(re_pattern(BINARY_CONNECTIVES), c):
                # we found a connective
                # now we check if it is in the outermost parenthesis group
                # that is, at depth 1
                if paren_count == 1:
                    connective_pos = pos
                    break
        if connective_pos != -1:
            # found a central connective
            left = s[:connective_pos]
            right = s[connective_pos+1:]
            if (re.match(f'^{LPAREN}$', left[0])
                    and re.match(f'^{RPAREN}$', right[-1])):
                # also has appropriate enclosing parentheses
                # return the two connected subsentences
                left = left[1:]
                right = right[:-1]
                return [left, right, s[connective_pos]]
            else:
                # is not enclosed in parentheses
                return False
        else:
            # does not contain a central connective
            return False

    def negation(self):
        string = NOT + self.string
        form = Form.NEGATION
        subformulas = [self]
        return Formula(string, form, subformulas)
