#!/usr/bin/python

from CTFLogic import syntax, semantics, deduction, validity

import os
import re

def make_tree_string(nested_tree):
    string = r"[.\(" + nested_tree[0] + r"\) "
    if len(nested_tree[1:]) > 0:
        for i in nested_tree[1:]:
            string += make_tree_string(i)
    string += " ]"
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
    a1 = syntax.Formula("(p->(q&r))")
    a2 = syntax.Formula("(~p->r)")
    c = syntax.Formula("r")
    tree = deduction.Tableau()
    tree.construct(validity.Inference([a1, a2], c))
    text = r"\Tree "
    text += latex_string_replace(
        make_tree_string(tree.get_tree_as_nested_list()))
    latex_preamble = (
        r"""\documentclass{article}
        \usepackage{qtree}
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
