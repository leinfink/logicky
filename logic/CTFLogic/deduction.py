#!/usr/bin/python

import validity
from syntax import Form

from enum import Enum
import IPython


class ProofProcedure():
    pass


class TableauRules():
    class Rules(Enum):
        CONJ = 0,
        DISJ = 1,
        COND = 2,
        BICOND = 3,
        NEGNEG = 4,
        NEGCONJ = 5,
        NEGDISJ = 6,
        NEGCOND = 7,
        NEGBICOND = 8

    SPLITRULES = [Rules.COND, Rules.DISJ, Rules.NEGCONJ,
                  Rules.BICOND, Rules.NEGBICOND]

    NONSPLITRULES = [Rules.CONJ, Rules.NEGNEG, Rules.NEGDISJ,
                     Rules.NEGCOND]

    @classmethod
    def get_rule(cls, formula):
        f1 = formula.form
        if f1 == Form.ATOMIC:
            return None
        elif f1 == Form.NEGATION:
            subformula = formula.subformulas[0]
            f2 = subformula.form
            s = {
                Form.NEGATION: cls.Rules.NEGNEG,
                Form.CONJUNCTION: cls.Rules.NEGCONJ,
                Form.DISJUNCTION: cls.Rules.NEGDISJ,
                Form.CONDITIONAL: cls.Rules.NEGCOND,
                Form.BICONDITIONAL: cls.Rules.NEGBICOND
            }
            return s.get(f2)
        else:
            s = {
                Form.CONJUNCTION: cls.Rules.CONJ,
                Form.DISJUNCTION: cls.Rules.DISJ,
                Form.CONDITIONAL: cls.Rules.COND,
                Form.BICONDITIONAL: cls.Rules.BICOND
                }
            return s.get(f1)

    @classmethod
    def get_new_nodes(cls, formula, rule):
        r = rule
        if r == cls.Rules.NEGNEG:
            return [(formula.subformulas[0].subformulas[0], 0)]
        left = formula.subformulas[0]
        right = formula.subformulas[1]
        if r == cls.Rules.CONJ:
            a = (left, 0)
            b = (right, 1)
            return [a, b]
        elif r == cls.Rules.DISJ:
            a = (left, 0)
            b = (right, 0)
            return [a, b]
        elif r == cls.Rules.COND:
            a = (left.negation(), 0)
            b = (right, 0)
            return [a, b]
        elif r == cls.Rules.BICOND:
            a = (left, 0)
            b = (left.negation(), 0)
            c = (right, 1)
            d = (right.negation(), 2)
            return [a, b, c, d]
        left = formula.subformulas[0].subformulas[0]
        right = formula.subformulas[0].subformulas[1]
        if r == cls.Rules.NEGCONJ:
            a = (left.negation(), 0)
            b = (right.negation(), 0)
            return [a, b]
        elif r == cls.Rules.NEGDISJ:
            a = (left.negation(), 0)
            b = (right.negation(), 1)
            return [a, b]
        elif r == cls.Rules.NEGCOND:
            a = (left, 0)
            b = (right.negation(), 1)
            return [a, b]
        elif r == cls.Rules.NEGBICOND:
            a = (left, 0)
            b = (left.negation(), 0)
            c = (right.negation(), 1)
            d = (right, 2)
            return [a, b, c, d]


class TableauTree(list):
    def add_node(self, formula, parent_id):
        self.append((formula,
                     parent_id,
                     TableauRules.get_rule(formula)))


class Tableau(ProofProcedure):
    def __init__(self):
        # tree is a list containing tuples
        # (formula: Formula, parent_node: int, applicable_rule)
        # only formula and parent_node are technically part of the tree
        # applicable_rule is just to aid us
        self.tree = TableauTree()

    def construct(self, inf: validity.Inference):
        used_nodes = []
        # build initial list
        tree = self.initial_list(inf)

        i = 0
        nonsplit_checked = []
        while (len(used_nodes) < len(tree)):
            if i not in used_nodes:
                if len(nonsplit_checked) < (len(tree) - len(used_nodes)):
                    if tree[i][3] in TableauRules.NONSPLITRULES:
                        new_nodes = TableauRules.get_new_nodes(
                            tree[i][0], tree[i][3])
                        tree = self.add_new_nodes(tree, new_nodes, i)
            i += 1
            continue
        self.tree = tree

    def initial_list(self, inf):
        tree = TableauTree()
        i = -1  # root node has no parent
        # initial list
        for p in inf.premisses:
            tree.add_node(p, i)
            i += 1
        tree.add_node(inf.conclusion.negation(), i)
        return tree

    def add_new_nodes(self, tree, new_nodes, parent_node: int):
        pass

    def get_end_notes(self, tree, node_id: int) -> int:
        subtree = tree[node_id:]
        children = self.find_children(subtree, node_id)
        if len(children) == 0:
            return node_id
        for c in children:
            start = c[2] - node_id
            self.find_children(subtree[start:], c[2])
            # TODO


    # def find_end(self, subtree, node_id: int):

    def find_children(self, subtree, node_id: int):
        children = []
        for i in subtree:
            if i[2] != node_id:
                continue
            else:
                children.append(i)
        return children


IPython.embed()
