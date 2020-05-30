#!/usr/bin/python

from CTFLogic import syntax, semantics, deduction, validity

import os
import re

node_count = 0
negatomics = {}
branches = []

def make_tree_string_forest(nested_tree, branch=[]):
    global node_count
    string = r"[{$" + nested_tree[0] + r"$"
    print(nested_tree[0])
    abranch = branch + [syntax.Formula(nested_tree[0])]
    if len(nested_tree[1:]) > 0:
        string += r"}"
        a = syntax.Formula(nested_tree[0])
        if a.form == syntax.Form.ATOMIC or (
                a.form == syntax.Form.NEGATION and
                a.subformulas[0].form == syntax.Form.ATOMIC):
            string += r", name=NODE"+str(node_count)
            negatomic = False
            if a.form == syntax.Form.ATOMIC:
                negatomic = True
                key = a.negation().string
            elif a.form == syntax.Form.NEGATION:
                negatomic = True
                key = a.string
            if negatomic:
                current_branches = []
                for i, b in enumerate(branches):
                    br = [node[0].formula for node in b]
                    if br[:len(abranch)] == abranch:
                        current_branches.append(i)
                #cntstring = ", content="+str(node_count)+"br"
                for i in current_branches:
                    negatomics[(key, i)] = node_count
                    #cntstring += str(i)
                #string += cntstring
            node_count += 1
        for i in nested_tree[1:]:
            if isinstance(i, list):
                string += make_tree_string_forest(i, abranch)
        string += r"]"
    else:
        string += r"\\[-0.1em]$\times$"
        # string += r"}]"
        a = syntax.Formula(nested_tree[0])
        if a.form == syntax.Form.NEGATION:
            formula = a
        elif a.form == syntax.Form.ATOMIC:
            formula = a.negation()
        else:
            # shouldn't happen for valid arguments
            string += "}]"
            return string
        #string += r", content="
        string += "}]"
        string += r"{\draw[->,dotted] () "
        string += r"to[out=south west, in=west] ("
        current_branch_id = None
        for i, b in enumerate(branches):
            br = [node[0].formula for node in b]
            if br[:len(abranch)] == abranch:
                current_branch_id = i
                print("Equal:")
                print([i.string for i in br])
                print([i. string for i in abranch])
                break
            else:
                print("Nonequal:")
                print([i.string for i in br])
                print([i. string for i in abranch])
        #string += str(current_branch_id) + " to " + str(negatomics[(formula.string, current_branch_id)])
        string += r"NODE" + str(negatomics[(formula.string, current_branch_id)])  # get partner element
        string += r");}"
    return string


def latex_string_replace(string):
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


if __name__ == '__main__':
    a1 = syntax.Formula("(p&(~q->~p))")
    a2 = syntax.Formula("((q&p)v~p)")
    c = syntax.Formula("((n&m)v~m)")
    d = syntax.Formula("(((a->b)&(a->c))->(a->(b&c)))")
    argument = validity.Inference([], d)
    tree = deduction.Tableau()
    tree.construct(argument)
    branches = tree.get_branches(tree.tree)
    text = r"\begin{forest}for tree={align=center, l sep=0, s sep+=4mm}"
    text += latex_string_replace(
        make_tree_string_forest(tree.get_tree_as_nested_list()))
    text += r"\end{forest}"
    latex_preamble = (
        r"""\documentclass{article}
        \usepackage[]{forest}
        \usepackage[T1]{fontenc}
        \usepackage[utf8]{inputenc}
        \begin{document}
        """)
    latex_end = r"\end{document}"
    f = open("latex/logictex.tex", "w")
    f.write(latex_preamble+text+latex_end)
    f.close()
    os.system("pdflatex -output-directory=latex "
              "-output-format=pdf latex/logictex.tex ")
