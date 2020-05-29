#!/usr/bin/python

from . import validity
from . import syntax
from . import semantics
from .syntax import Form

from enum import Enum
import pdb


class ProofProcedure():
    pass


class TableauRules():
    class Rules(Enum):
        CONJ = 0
        DISJ = 1
        COND = 2
        BICOND = 3
        NEGNEG = 4
        NEGCONJ = 5
        NEGDISJ = 6
        NEGCOND = 7
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
        if r is None:
            return []
        if r == cls.Rules.NEGNEG:
            return [(formula.subformulas[0].subformulas[0], 0)]
        if r not in [cls.Rules.NEGCONJ, cls.Rules.NEGDISJ, cls.Rules.NEGBICOND,
                     cls.Rules.NEGCOND, cls.Rules.NEGNEG]:
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


class Tableau(ProofProcedure):
    class Node():
        def __init__(self, formula, parent_id, applicable_rule):
            self.formula: syntax.Formula = formula
            self.parent_id = parent_id
            self.applicable_rule = applicable_rule

    def __init__(self):
        # self.tree is a list containing nodes
        # [formula: Formula, parent_node: int, applicable_rule]
        # only formula and parent_node are technically part of the tree
        # applicable_rule is just to aid us
        self.tree = []

    def construct(self, inf: validity.Inference, full=True):
        # if full==True, continue a branch even after reaching contradictions

        # build initial list
        tree = self.initial_list(inf)

        used_nodes = []
        i = 0
        while (len(used_nodes) < len(tree)):
            if i not in used_nodes:
                new_nodes = TableauRules.get_new_nodes(tree[i].formula,
                                                       tree[i].applicable_rule)
                used_nodes.append(i)
                # if tree[i].applicable_rule == TableauRules.Rules.BICOND:
                # pdb.set_trace()
                branches = self.get_branches(tree, i)
                for b in branches:
                    start_parent_id = b[-1][1]
                    new_node_ids = []
                    for new in new_nodes:
                        if new[1] == 0:
                            parent_id = start_parent_id
                        else:
                            parent_id = new_node_ids[new[1]-1]
                        new_node_ids.append(len(tree))
                        new_node = self.Node(new[0],
                                             parent_id,
                                             TableauRules.get_rule(new[0]))
                        tree.append(new_node)
                if i < len(tree)-1:
                    i += 1
                else:
                    i = 0
        self.tree = tree

    def proof_valid(self):  # CAREFUL; return True or counterinterpretation
        branches = self.get_branches(self.tree)
        for b in branches:
            atomics = []
            branch_closed = False
            for node in b:
                if node[0].formula.form == Form.ATOMIC:
                    atomics.append(node[0].formula)
            for node in b:
                formula = node[0].formula
                if (formula.form == Form.NEGATION and
                        formula.subformulas[0].form == Form.ATOMIC):
                    if formula.subformulas[0] in atomics:
                        branch_closed = True
                        break
            if not branch_closed:
                return self.get_counterinterpretation(b)
        return True

    def get_counterinterpretation(self, branch) -> semantics.Interpretation:
        true_atomics = []
        false_atomics = []
        for node in branch:
            if node[0].formula.form == Form.ATOMIC:
                true_atomics.append(node[0].formula)
        for node in branch:
            formula = node[0].formula
            if (formula.form == Form.NEGATION and
                    formula.subformulas[0].form == Form.ATOMIC):
                false_atomics.append(formula.subformulas[0])
        assignments = {}
        for a in true_atomics:
            assignments[a.string] = 1
        for a in false_atomics:
            assignments[a.string] = 0
        return semantics.Interpretation(assignments)

    def initial_list(self, inf):
        tree = []
        i = -1  # root node has no parent
        # initial list
        for p in inf.premisses:
            tree.append(self.Node(p, i, TableauRules.get_rule(p)))
            i += 1
        neg_concl = inf.conclusion.negation()
        tree.append(self.Node(neg_concl, i, TableauRules.get_rule(neg_concl)))
        return tree

    def get_branches(self, tree, starting_id=0):
        tree = tree[starting_id:]

        def has_children(index):
            for n in tree[index:]:
                if n.parent_id == index + starting_id:
                    return True
            return False

        def get_parent(index):
            child_id = index
            for i, node in enumerate(tree[:child_id]):
                if i + starting_id == tree[child_id].parent_id:
                    return (node, i)
            return None

        branches = []
        for i, node in enumerate(tree):
            if not has_children(i):
                branch = [[node, i+starting_id]]  # [node, index in tree]
                j = i
                while a := get_parent(j):
                    # [node, index in tree]
                    branch.insert(0, [a[0], a[1]+starting_id])
                    j = a[1]
                if branch[0][0] == tree[0]:
                    branches.append(branch)
        return branches

    def get_tree_as_nested_list(self, tree=None, starting_id=0):
        if tree is None:
            tree = self.tree
        tree = tree[starting_id:]

        def get_children(index):
            subtree = [tree[index].formula.string]
            for i, n in enumerate(tree[index+1:]):
                if n.parent_id == index + starting_id:
                    subtree.append(get_children(i+index+1))
            return subtree

        return get_children(0)

    def print_branches(self, branches=None):
        if branches is None:
            branches = self.get_branches(self.tree)
        output = []
        for n in branches:
            output.append([i[0].formula.string for i in n])
        return output

    def print_tree(self, tree=None):
        if tree is None:
            tree = self.tree
        return ([(i.formula.string, i.parent_id) for i in tree])


class Formula(syntax.Formula):
    def is_logical_truth(self):
        tableau = Tableau()
        tableau.construct(validity.Inference([], self))
        return (tableau.proof_valid() is True)
    is_tautology = is_logical_truth


class Inference(validity.Inference):
    def is_valid(self):
        tableau = Tableau()
        tableau.construct(validity.Inference(self.premisses,
                                             self.conclusion))
        return (tableau.proof_valid() is True)


if __name__ == "__main__":
    pass
