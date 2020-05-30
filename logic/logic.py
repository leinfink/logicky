#!/usr/bin/python

from CTFLogic import syntax, deduction
import latexrender


def render_CTF_Tableau_from_strings(prems, concl):
    premisses = []
    for p in prems:
        try:
            premisses.append(syntax.Formula(p))
        except syntax.NotWellFormedFormulaError:
            # shittiest code ever
            # basically try again with added outer parentheses
            premisses.append(syntax.Formula(f'({p})'))
    try:
        conclusion = syntax.Formula(concl)
    except syntax.NotWellFormedFormulaError:
        conclusion = syntax.Formula(f'({concl})')
    argument = deduction.Inference(premisses, conclusion)
    tree = deduction.Tableau()
    tree.construct(argument)
    valid = argument.is_valid()
    show_arrows = True if valid else False
    pdfoutputpath = latexrender.LatexRenderTableau(tree).render(show_arrows)
    return [pdfoutputpath, valid]


if __name__ == '__main__':
    print(render_CTF_Tableau_from_strings(["a->b", "~b"], "~a"))
