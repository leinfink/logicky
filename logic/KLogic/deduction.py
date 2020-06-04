#!/usr/bin/python

from enum import Enum

from . import syntax
from . import semantics

# import superclasses from CTFLogic
from logic.CTFLogic import deduction, validity

import pdb

class KTableauRules(deduction.TableauRules):
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
        NEGNEC = 9
        NEGPOSS = 10
        NEC = 11
        POSS = 12

    @classmethod
    def get_rule(cls, formula):
        f1 = formula.form
        if f1 == syntax.KForm.NEGATION:
            subformula = formula.subformulas[0]
            f2 = subformula.form
            if f2 == syntax.KForm.NECESSARY:
                return cls.Rules.NEGNEC
            elif f2 == syntax.KForm.POSSIBLE:
                return cls.Rules.NEGPOSS
            s = {
                syntax.KForm.NEGATION: cls.Rules.NEGNEG,
                syntax.KForm.CONJUNCTION: cls.Rules.NEGCONJ,
                syntax.KForm.DISJUNCTION: cls.Rules.NEGDISJ,
                syntax.KForm.CONDITIONAL: cls.Rules.NEGCOND,
                syntax.KForm.BICONDITIONAL: cls.Rules.NEGBICOND
            }
            return s.get(f2)
        elif f1 == syntax.KForm.NECESSARY:
            return cls.Rules.NEC
        elif f1 == syntax.KForm.POSSIBLE:
            return cls.Rules.POSS
        s = {
            syntax.KForm.CONJUNCTION: cls.Rules.CONJ,
            syntax.KForm.DISJUNCTION: cls.Rules.DISJ,
            syntax.KForm.CONDITIONAL: cls.Rules.COND,
            syntax.KForm.BICONDITIONAL: cls.Rules.BICOND
        }
        return s.get(f1)


class KTableau(deduction.Tableau):
    class KNode():
        def __init__(self, formula, parent_id, applicable_rule, worldnr=0):
            self.formula: syntax.KFormula = formula
            self.parent_id = parent_id
            self.applicable_rule = applicable_rule
            self.worldnr = worldnr
            self.string = self.formula.string

    class KWorldRelationNode(KNode):
        def __init__(self, w1, w2, parent_id=None):
            self.w1 = w1
            self.w2 = w2
            self.parent_id = parent_id
            self.applicable_rule = None
            self.set_string()
            self.worldnr = None

        def set_string(self):
            self.string = str(self.w1) + "r" + str(self.w2)

    def initial_list(self, inf):
        tree = []
        i = -1  # root node has no parent
        # initial list
        for p in inf.premisses:
            tree.append(self.KNode(p, i, KTableauRules.get_rule(p), 0))
            i += 1
        neg_concl = inf.conclusion.negation()
        tree.append(self.KNode(neg_concl, i,
                               KTableauRules.get_rule(neg_concl), 0))
        return tree

    def construct(self, inf: validity.Inference):
        # if full==True, continue a branch even after reaching contradictions

        # build initial list
        self.tree = self.initial_list(inf)

        used_nodes = []
        self.used_wr_nodes_for_node = {}
        pdbed = False
        i = 0
        while (len(used_nodes) < len(self.tree)):
            #if pdbed:
             #   pdb.set_trace()
            if i not in used_nodes:
                new_nodes = self.get_new_nodes(self.tree[i], i)
                if self.tree[i].applicable_rule == KTableauRules.Rules.NEC:
                    if new_nodes == []:
                        used_nodes.append(i)
                else:
                    used_nodes.append(i)
                is_poss = False
                is_nec = False
                if self.tree[i].applicable_rule == KTableauRules.Rules.POSS:
                    is_poss = True
                if self.tree[i].applicable_rule == KTableauRules.Rules.NEC:
                    is_nec = True
                branches = self.get_branches(self.tree, i)
                for b in branches:
                    start_parent_id = b[-1][1]
                    new_node_ids = []
                    add_one_for_reasons = False
                    if is_poss:
                        new_world_id = self.tree[i].worldnr
                    for new in new_nodes:
                        if new[1] == 0:
                            parent_id = start_parent_id
                            if add_one_for_reasons:
                                parent_id = new_node_ids[0]
                            print(f'start id: {start_parent_id}')
                        else:
                            try:
                                parent_id = new_node_ids[new[1]-1]
                            except:
                                print("huh")
                                pdb.set_trace()
                        new_node_ids.append(len(self.tree))
                        #print(new_node_ids)
                        if type(new[0]) == self.KWorldRelationNode:
                            new_node = new[0]
                            new_node.parent_id = parent_id
                            #print(new_node.parent_id)
                            if is_poss:
                                used_worlds = []
                                new_world = new_node.w1 + 1
                                for index2, node2 in enumerate(self.tree):
                                    if type(node2) == self.KWorldRelationNode:
                                        if index2 in self.get_parents_until(
                                                new_node.parent_id, index2):
                                            if node2.w1 not in used_worlds:
                                                used_worlds.append(node2.w1)
                                            if node2.w2 not in used_worlds:
                                                used_worlds.append(node2.w2)
                                while new_world in used_worlds:
                                    new_world = new_world + 1
                                new_world_id = new_world
                                new_node.w2 = new_world_id
                                # IMPORTANT, set string again!
                                # should actually put this in a .w2 accesssor!
                                # TODO
                                new_node.set_string()
                                #print(new_node.string)
                            for i, v in enumerate(self.tree):
                                if (v.applicable_rule ==
                                    KTableauRules.Rules.NEC):
                                    if i in used_nodes:
                                        used_nodes.remove(i)
                                        pdbed = True
                        else:
                            if is_nec:
                                print("alles weird")
                                print(new[3])
                                print("und")
                                print(parent_id)
                                print(len(self.tree))
                                if new[3] in self.get_parents_until(parent_id, new[3]):
                                    # new[3] is the used worldrelation node
                                    new_node = self.KNode(new[0],
                                                          parent_id,
                                                          KTableauRules.get_rule(
                                                              new[0]), new[2])
                                    add_one_for_reasons = True
                                else:
                                    continue
                            else:
                                new_node = self.KNode(new[0],
                                                      parent_id,
                                                      KTableauRules.get_rule(
                                                          new[0]), new[2])
                            if is_poss:
                                new_node.worldnr = new_world_id
                        #print(new_node.parent_id)
                        if type(new_node) == self.KWorldRelationNode:
                            self.tree.append(self.KWorldRelationNode(new_node.w1, new_node.w2, new_node.parent_id))
                            self.tree[-1].worldnr = new_node.worldnr
                        else:
                            self.tree.append(self.Node(new_node.formula, new_node.parent_id, new_node.applicable_rule))
                            self.tree[-1].worldnr = new_node.worldnr
                        #if (new_node.parent_id in [4,6]):
                            #print([f'{a.string} p:{a.parent_id} {i}' for i,a in enumerate(self.tree)])
                #print("hi")
            if i < len(self.tree)-1:
                i += 1
            else:
                i = 0

    def get_parents_until(self, child_id, lowest_index):
        def get_parent(index):
            child = index
            for i, node in enumerate(self.tree[:child]):
                if i == self.tree[child].parent_id:
                    return i
            return None
        i = child_id
        parents = []
        while i > lowest_index:
            #pdb.set_trace()
            last_parent = get_parent(i)
            i = last_parent
            if i is None:
                break
            else:
                parents.append(last_parent)
        return parents

    def get_new_nodes(self, node, index=None):
        r = node.applicable_rule
        if r is None:
            return []
        if r == KTableauRules.Rules.NEGNEG:
            return [(node.formula.subformulas[0].subformulas[0], 0, node.worldnr)]
        if r == KTableauRules.Rules.NEGNEC:
            return [(node.formula.turn_neg_modality(), 0, node.worldnr)]
        if r == KTableauRules.Rules.NEGPOSS:
            return [(node.formula.turn_neg_modality(), 0, node.worldnr)]
        if r == KTableauRules.Rules.NEC:
            new_nodes = []
            i = 0
            if node not in self.used_wr_nodes_for_node:
                self.used_wr_nodes_for_node[node] = []
            for index2, node2 in enumerate(self.tree):
                if type(node2) == self.KWorldRelationNode:
                    if (node2.w1 == node.worldnr and node2 not in self.
                            used_wr_nodes_for_node[node]):
                        #pdb.set_trace()
                        if (index in self.get_parents_until(index2, index) or index2 in self.get_parents_until(index, index2)):
                            new_nodes.append((node.formula.subformulas[0],
                                              i, node2.w2, index2)) #index2 for the node of the world relation we used
                            self.used_wr_nodes_for_node[node].append(node2)
                            #i += 1
            return new_nodes
        if r == KTableauRules.Rules.POSS:
            #new_world = node.worldnr + 1
            #used_worlds = []
            # this should work as long as POSS is the only rule adding new
            # world relations
            # if not, we would need to check the tree until the end of each
            # respective subbranch of the POSS, not only until the POSS-node
            # nevermind, there can be other POSS nodes, fuck.
            #for i, node in enumerate(self.tree):
            #   if type(node) == self.KWorldRelationNode:
            #        if node.w1 not in used_worlds:
            #           used_worlds.append(node.w1)
            #        if node.w2 not in used_worlds:
            #            used_worlds.append(node.w2)
            #while new_world in used_worlds:
            #    new_world = new_world + 1
            return [(self.KWorldRelationNode(node.worldnr, None), 0),
                    (node.formula.subformulas[0], 1, None)]
        if r not in [KTableauRules.Rules.NEGCONJ, KTableauRules.Rules.NEGDISJ,
                     KTableauRules.Rules.NEGBICOND,
                     KTableauRules.Rules.NEGCOND, KTableauRules.Rules.NEGNEG,
                     KTableauRules.Rules.NEGPOSS, KTableauRules.Rules.NEGNEC]:
            left = node.formula.subformulas[0]
            right = node.formula.subformulas[1]
        if r == KTableauRules.Rules.CONJ:
            a = (left, 0, node.worldnr)
            b = (right, 1, node.worldnr)
            return [a, b]
        elif r == KTableauRules.Rules.DISJ:
            a = (left, 0, node.worldnr)
            b = (right, 0, node.worldnr)
            return [a, b]
        elif r == KTableauRules.Rules.COND:
            a = (left.negation(), 0, node.worldnr)
            b = (right, 0, node.worldnr)
            return [a, b]
        elif r == KTableauRules.Rules.BICOND:
            a = (left, 0, node.worldnr)
            b = (left.negation(), 0, node.worldnr)
            c = (right, 1, node.worldnr)
            d = (right.negation(), 2, node.worldnr)
            return [a, b, c, d]
        left = node.formula.subformulas[0].subformulas[0]
        right = node.formula.subformulas[0].subformulas[1]
        if r == KTableauRules.Rules.NEGCONJ:
            a = (left.negation(), 0, node.worldnr)
            b = (right.negation(), 0, node.worldnr)
            return [a, b]
        elif r == KTableauRules.Rules.NEGDISJ:
            a = (left.negation(), 0, node.worldnr)
            b = (right.negation(), 1, node.worldnr)
            return [a, b]
        elif r == KTableauRules.Rules.NEGCOND:
            a = (left, 0, node.worldnr)
            b = (right.negation(), 1, node.worldnr)
            return [a, b]
        elif r == KTableauRules.Rules.NEGBICOND:
            a = (left, 0, node.worldnr)
            b = (left.negation(), 0, node.worldnr)
            c = (right.negation(), 1, node.worldnr)
            d = (right, 2, node.worldnr)
            return [a, b, c, d]

    def branch_closed(self, branch):
        # CARE: -> True or counterinterpretation
        b = branch
        atomics = []
        branch_closed = False
        for node in b:
            if not type(node[0]) == self.KWorldRelationNode:
                if node[0].formula.form == syntax.KForm.ATOMIC:
                    atomics.append(node[0].formula.string+str(node[0].worldnr))
        for node in b:
            if not type(node[0]) == self.KWorldRelationNode:
                formula = node[0].formula
                if (formula.form == syntax.KForm.NEGATION and
                        formula.subformulas[0].form == syntax.KForm.ATOMIC):
                    if (formula.subformulas[0].string+str(node[0].worldnr)) in atomics:
                        branch_closed = True
                        break
        if not branch_closed:
            return self.get_counterinterpretation(b)
        else:
            return True

    def get_counterinterpretation(self, branch) -> semantics.KInterpretation:
        true_atomics = []
        false_atomics = []
        world_relations = []
        worlds = []
        for node in branch:
            if not type(node[0]) == self.KWorldRelationNode:
                if node[0].formula.form == syntax.KForm.ATOMIC:
                    true_atomics.append((node[0].formula, node[0].worldnr))
            else:
                if not node[0].w1 in worlds:
                    worlds.append(node[0].w1)
                if not node[0].w2 in worlds:
                    worlds.append(node[0].w2)
        for w in worlds:
            world_relations.append([])
        for node in branch:
            if not type(node[0]) == self.KWorldRelationNode:
                formula = node[0].formula
                if (formula.form == syntax.KForm.NEGATION and
                        formula.subformulas[0].form == syntax.KForm.ATOMIC):
                    false_atomics.append((formula.subformulas[0], node[0].worldnr))
            else:
                if not node[0].w2 in world_relations[node[0].w1]:
                    world_relations[node[0].w1].append(node[0].w2)
        assignments = {}
        for a in true_atomics:
            assignments[(a[1], a[0].string)] = 1
        for a in false_atomics:
            assignments[(a[1], a[0].string)] = 0
        return semantics.KInterpretation(worlds, world_relations, assignments)

    def get_tree_as_nested_list(self, tree=None, simplify=True, starting_id=0):
        if tree is None:
            tree = self.tree
        tree = tree[starting_id:]
        #print([f'{n.string},{n.worldnr},{n.parent_id}[{i}]' for i,n in enumerate(tree)])

        if simplify:
            branches = self.get_branches(tree)
            for b in branches:
                atomics = []
                conatomics = []
                stop_branch = False
                for node in b:
                    if type(node[0]) == self.KWorldRelationNode:
                        continue
                    if node[0].formula.form == syntax.KForm.ATOMIC:
                        if node[0].formula.string+str(node[0].worldnr) in conatomics:
                            stop_branch = node[1]
                            break
                        atomics.append(node[0].formula.string+str(node[0].worldnr))
                    formula = node[0].formula
                    if (formula.form == syntax.KForm.NEGATION and
                            formula.subformulas[0].form == syntax.KForm.ATOMIC):
                        if formula.subformulas[0].string+str(node[0].worldnr) in atomics:
                            stop_branch = node[1]
                            break
                        conatomics.append(formula.subformulas[0].string+str(node[0].worldnr))
                if stop_branch:
                    for i, n in enumerate(tree[stop_branch:]):
                        if n == []:
                            continue
                        if n.parent_id == stop_branch:
                            tree[i+stop_branch] = []

        def get_children(index):
            if type(tree[index]) == self.KWorldRelationNode:
                subtree = [(f'{tree[index].w1}r{tree[index].w2}', None)]
                #subtree = [(f'{tree[index].w1}r{tree[index].w2}', tree[index].worldnr)]
            else:
                subtree = [(tree[index].formula.string, tree[index].worldnr)]
            for i, n in enumerate(tree[index+1:]):
                if n == []:
                    continue
                if n.parent_id == index + starting_id:
                    subtree.append(get_children(i+index+1))
            return subtree

        return get_children(0)


class KInference(validity.Inference):
    def is_valid(self):
        tableau = KTableau()
        tableau.construct(validity.Inference(self.premisses,
                                             self.conclusion))
        return (tableau.proof_valid() is True)


if __name__ == "__main__":
    a = syntax.KFormula("(avb)")
    #b = syntax.KFormula("~(~b->◇◇c)")
    #a = syntax.KFormula("~a")
    b = syntax.KFormula("<>x")
    d = syntax.KFormula("<>b")
    c = syntax.KFormula("<>d")
    inf = KInference([a,b,d], c)
    print(inf.is_valid())
