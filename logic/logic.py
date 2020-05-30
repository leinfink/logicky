#!/usr/bin/python

from CTFLogic import syntax, deduction, validity
import latexrender

if __name__ == '__main__':
    a1 = syntax.Formula("(p&(~q->~p))")
    a2 = syntax.Formula("((q&p)v~p)")
    c = syntax.Formula("((n&m)v~m)")
    d = syntax.Formula("(((a->b)&(a->c))->(a->(b&c)))")
    argument = deduction.Inference([], d)
    tree = deduction.Tableau()
    tree.construct(argument)
    show_arrows = True if argument.is_valid() else False
    latexrender.LatexRenderTableau(tree).render(show_arrows)
