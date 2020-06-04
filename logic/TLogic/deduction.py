#!/usr/bin/python

# import superclasses from KLogic
from logic.KLogic import deduction, syntax
from logic.KLogic.deduction import KTableauRules

from logic.CTFLogic import validity

import pdb

class TTableau(deduction.KTableau):

    def construct(self, inf: validity.Inference):
        # if full==True, continue a branch even after reaching contradictions

        # build initial list
        self.tree = self.initial_list(inf)

        used_nodes = []
        self.used_wr_nodes_for_node = {}
        pdbed = False
        i = 0
        while (len(used_nodes) < len(self.tree)):
            #print([f'{a.string} p:{a.parent_id} {i}' for i,a in enumerate(self.tree)])
            #if pdbed:
             #   pdb.set_trace()
            #print(f'current i: {self.tree[i].string}')
            #if self.tree[i].string == "◇¬(B→A)":
             #   pdb.set_trace()
            if i not in used_nodes:
                new_nodes = self.get_new_nodes(self.tree[i], i)
                if self.tree[i].applicable_rule == KTableauRules.Rules.NEC:
                    #print([a[0].string for a in new_nodes])
                    #print([a.string for a in self.tree])
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
                            #print(new[0].string)
                            parent_id = start_parent_id
                            #print(parent_id)
                            if add_one_for_reasons:
                                #print("oho")
                                parent_id = new_node_ids[0]
                            #print(f'start id: {start_parent_id}')
                        else:
                            try:
                                parent_id = new_node_ids[new[1]-1]
                            except:
                                print("huh")
                                #pdb.set_trace()
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
                            #for i, v in enumerate(self.tree):
                            #    if (v.applicable_rule ==
                            #        KTableauRules.Rules.NEC):
                            #        if i in used_nodes:
                             #           used_nodes.remove(i)
                             #           pdbed = True
                        else:
                            if is_nec:
                                #print("alles weird")
                                #print(new[3])
                                #print("und")
                                #print(parent_id)
                                #print(len(self.tree))
                                #print(f'id{parent_id}')
                                #print(self.get_parents_until(parent_id, new[3]))
                                if new[3] in self.get_parents_until(parent_id, new[3]) or new[3] == parent_id:
                                    #print("jawoll")
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
                            # reflexive condition of Logic T
                            self.tree.append(self.KWorldRelationNode(new_node.w2, new_node.w2, len(self.tree)-1))
                            self.tree[-1].worldnr = new_node.worldnr
                            new_node_ids[-1] = len(self.tree)-1
                            for c, v in enumerate(self.tree):
                                if (v.applicable_rule ==
                                    KTableauRules.Rules.NEC):
                                    if c in used_nodes:
                                        used_nodes.remove(c)
                                        pdbed = True
                            #print(self.tree[-1].string)
                            #print([f'{a.string} p:{a.parent_id} {i}' for i,a in enumerate(self.tree)])
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
        #print([f'{a.string} p:{a.parent_id} {i}' for i,a in enumerate(self.tree)])

    def initial_list(self, inf):
        a = super().initial_list(inf)
        b = a + [self.KWorldRelationNode(0, 0, len(a)-1)]
        b[-1].worldnr = None
        return b


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
                    #print(b[-1].string)
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
            #if len(tree[index+1:]) == 0:
                #print("hohoho")
                #print(tree[index:][0].parent_id)
            #print(f'subtree:{subtree}, but last tree item: {self.tree[-1].string}, {self.tree[-1].worldnr}')
            return subtree

        #print(f'last tree item: {self.tree[-1].string}, {self.tree[-1].worldnr}')
        return get_children(0)


class TInference(validity.Inference):
    def is_valid(self):
        tableau = TTableau()
        tableau.construct(validity.Inference(self.premisses,
                                             self.conclusion))
        return (tableau.proof_valid() is True)
