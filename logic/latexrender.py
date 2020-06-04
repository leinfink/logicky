#!/usr/bin/python
import logic.CTFLogic as CTFLogic
import logic.KLogic as KLogic

import re
import os
from datetime import datetime
import pdb

class LatexRenderTableau():
    def __init__(self, tree):
        self.tree = tree
        self.branches = tree.get_branches(tree.tree)
        self.negatomics = {}
        self.node_count = 0
        self.show_arrows = True

    def render(self, path, logiccls, show_arrows=True):
        self.negatomics = {}
        self.atomics = {}
        self.node_count = 0
        self.show_arrows = show_arrows
        text = r"\begin{forest}for tree={align=center, l sep=0, s sep+=4mm}"
        text += self.latex_string_replace(
            self.make_tree_string_forest(self.tree.get_tree_as_nested_list(), logiccls=logiccls))
        text += r"\end{forest}"
        f = open(path+"template.tex", "r")
        latex_preamble = f.read()
        latex_end = r"\end{document}"
        now = datetime.now()
        timestamp = str(datetime.timestamp(now))
        path = path + timestamp
        f = open(path+"output.tex", "w")
        f.write(latex_preamble+text+latex_end)
        f.close()
        return timestamp+"output"

    def make_tree_string_forest(self,
                                nested_tree,
                                branch=[],
                                logiccls='ctflogic'):
        if logiccls == 'ctflogic':
            formulacls = CTFLogic.syntax.Formula
            formcls = CTFLogic.syntax.Form
            #if not isinstance(nested_tree[0], tuple):
             #   nested_tree2 = []
              #  for i, v in enumerate(nested_tree):
               #     print(v)
                #    nested_tree2.append((v, None))
                #nested_tree = nested_tree2
        elif logiccls == 'klogic':
            formulacls = KLogic.syntax.KFormula
            formcls = KLogic.syntax.KForm
        elif logiccls == 'tlogic':
            formulacls = KLogic.syntax.KFormula
            formcls = KLogic.syntax.KForm
        if logiccls == 'ctflogic':
            if not isinstance(nested_tree[0], tuple):
                nested_tree[0] = (nested_tree[0], None)
        if nested_tree[0][1] is not None:
            string = r"[{$" + nested_tree[0][0] + ", " + str(nested_tree[0][1]) + r"$"
        else:
            string = r"[{$" + nested_tree[0][0] + r"$"
        # abranch = branch + [formulacls(nested_tree[0])]
        abranch = branch + [nested_tree[0]]
        if len(nested_tree[1:]) > 0:
            string += r"}"
            try:
                a = formulacls(nested_tree[0][0])
            except CTFLogic.syntax.NotWellFormedFormulaError:
                pass
            else:
                if a.form == formcls.ATOMIC or (
                       a.form == formcls.NEGATION and
                        a.subformulas[0].form == formcls.ATOMIC):
                    string += r", name=NODE"+str(self.node_count)
                    atomic_or_neg = False
                    if a.form == formcls.ATOMIC:
                        atomic_or_neg = True
                    elif a.form == formcls.NEGATION:
                        atomic_or_neg = True
                    if atomic_or_neg:
                        current_branches = []
                        for i, b in enumerate(self.branches):
                            if logiccls == 'klogic' or logiccls == 'tlogic':
                                br = [(node[0].string, node[0].worldnr) for node in b]
                            elif logiccls == 'ctflogic':
                                br = [(node[0].string, None) for node in b]
                            #print(f'{abranch} XXXXXXXXXX {br}')
                            if br[:len(abranch)] == abranch:
                                current_branches.append(i)
                        for i in current_branches:
                            #print(f'added (neg)atomic {a.string}')
                            if a.form == formcls.ATOMIC:
                                self.atomics[(a.string, i, nested_tree[0][1])] = self.node_count
                            elif a.form == formcls.NEGATION:
                                self.negatomics[(a.string, i, nested_tree[0][1])] = self.node_count
                    self.node_count += 1
            for i in nested_tree[1:]:
                #pdb.set_trace()
                if isinstance(i, list):
                    string += self.make_tree_string_forest(i, abranch, logiccls)
            string += r"]"
        else:
            # string += r"}]"
            #this try clause catches ending worldrelation nodes
            # I added it for TLogic
            # if it breaks something in KLogic, revert it!
            try:
                a = formulacls(nested_tree[0][0])
            except CTFLogic.syntax.NotWellFormedFormulaError:
                string += r"\\[-0.2em]\scriptsize open}]"
            else:
                if a.form == formcls.NEGATION:
                    formula = a.subformulas[0]
                    othercheck = self.atomics
                elif a.form == formcls.ATOMIC:
                    formula = a.negation()
                    othercheck = self.negatomics
                else:
                    # shouldn't happen for valid arguments
                    string += "}]"
                    return string
                current_branch_id = None
                for i, b in enumerate(self.branches):
                    #print(b)
                    if logiccls == 'klogic' or logiccls == 'tlogic':
                        br = [(node[0].string, node[0].worldnr) for node in b]
                    elif logiccls == 'ctflogic':
                        br = [(node[0].string, None) for node in b]
                    print(br[:len(abranch)])
                    print(abranch)
                    if br[:len(abranch)] == abranch:
                        current_branch_id = i
                        break
                # basically another version of the validity check here
                if (formula.string, current_branch_id, nested_tree[0][1]) in othercheck:
                    string += r"\\[-0.1em]$\times$"
                    string += "}]"
                    if self.show_arrows:
                        string += r"{\draw[->,dotted] () "
                        string += r"to[out=west, in=west] ("
                        # get partner element
                        string += r"NODE" + str(
                            othercheck[(formula.string,
                                        current_branch_id, nested_tree[0][1])])
                        string += r");}"
                else:
                    #print((formula.string, current_branch_id, nested_tree[0][1]))
                    #print(othercheck)
                    string += r"\\[-0.2em]\scriptsize open}]"
        return string

    def latex_string_replace(self, string):
        s = {
            "¬": r"\\lnot ",
            "∧": r"\\wedge ",
            "∨": r"\\lor ",
            "→": r"\\to ",
            "↔": r"\\leftrightarrow ",
            "◻": r"\\Box ",
            "◇": r"\\Diamond "
        }
        for key, value in s.items():
            string = re.sub(key, value, string)
        return string
