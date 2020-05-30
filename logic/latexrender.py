#!/usr/bin/python
import CTFLogic

import re
import os


class LatexRenderTableau():
    def __init__(self, tree: CTFLogic.deduction.Tableau):
        self.tree = tree
        self.branches = tree.get_branches(tree.tree)
        self.negatomics = {}
        self.node_count = 0
        self.show_arrows = True

    def render(self, show_arrows=True):
        self.negatomics = {}
        self.node_count = 0
        self.show_arrows = show_arrows
        text = r"\begin{forest}for tree={align=center, l sep=0, s sep+=4mm}"
        text += self.latex_string_replace(
            self.make_tree_string_forest(self.tree.get_tree_as_nested_list()))
        text += r"\end{forest}"
        f = open("latex/template.tex", "r")
        latex_preamble = f.read()
        latex_end = r"\end{document}"
        f = open("latex/logictex.tex", "w")
        f.write(latex_preamble+text+latex_end)
        f.close()
        os.system("pdflatex -output-directory=latex "
                  "-output-format=pdf latex/logictex.tex ")

    def make_tree_string_forest(self,
                                nested_tree,
                                branch=[]):
        string = r"[{$" + nested_tree[0] + r"$"
        print(nested_tree[0])
        abranch = branch + [CTFLogic.syntax.Formula(nested_tree[0])]
        if len(nested_tree[1:]) > 0:
            string += r"}"
            a = CTFLogic.syntax.Formula(nested_tree[0])
            if a.form == CTFLogic.syntax.Form.ATOMIC or (
                    a.form == CTFLogic.syntax.Form.NEGATION and
                    a.subformulas[0].form == CTFLogic.syntax.Form.ATOMIC):
                string += r", name=NODE"+str(self.node_count)
                negatomic = False
                if a.form == CTFLogic.syntax.Form.ATOMIC:
                    negatomic = True
                    key = a.negation().string
                elif a.form == CTFLogic.syntax.Form.NEGATION:
                    negatomic = True
                    key = a.string
                if negatomic:
                    current_branches = []
                    for i, b in enumerate(self.branches):
                        br = [node[0].formula for node in b]
                        if br[:len(abranch)] == abranch:
                            current_branches.append(i)
                    for i in current_branches:
                        self.negatomics[(key, i)] = self.node_count
                self.node_count += 1
            for i in nested_tree[1:]:
                if isinstance(i, list):
                    string += self.make_tree_string_forest(i, abranch)
            string += r"]"
        else:
            # string += r"}]"
            a = CTFLogic.syntax.Formula(nested_tree[0])
            if a.form == CTFLogic.syntax.Form.NEGATION:
                formula = a
            elif a.form == CTFLogic.syntax.Form.ATOMIC:
                formula = a.negation()
            else:
                # shouldn't happen for valid arguments
                string += "}]"
                return string
            current_branch_id = None
            for i, b in enumerate(self.branches):
                br = [node[0].formula for node in b]
                if br[:len(abranch)] == abranch:
                    current_branch_id = i
                    break
            # basically another version of the validity check here
            if (formula.string, current_branch_id) in self.negatomics:
                string += r"\\[-0.1em]$\times$"
                string += "}]"
                if self.show_arrows:
                    string += r"{\draw[->,dotted] () "
                    string += r"to[out=south west, in=west] ("
                    # get partner element
                    string += r"NODE" + str(
                        self.negatomics[(formula.string,
                                         current_branch_id)]) 
                    string += r");}"
            else:
                string += r"\\[-0.2em]\scriptsize open}]"
        return string

    def latex_string_replace(self, string):
        s = {
            "¬": r"\\lnot ",
            "∧": r"\\wedge ",
            "∨": r"\\lor ",
            "→": r"\\to ",
            "↔": r"\\leftrightarrow "
        }
        for key, value in s.items():
            string = re.sub(key, value, string)
        return string
