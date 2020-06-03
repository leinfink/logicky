#!/usr/bin/python

import os

import logic.CTFLogic.deduction as CTFdeduction
import logic.CTFLogic.syntax as CTFsyntax
import logic.KLogic.deduction as Kdeduction
import logic.KLogic.syntax as Ksyntax
from . import latexrender


def render_CTF_Tableau_from_strings(prems, concl, path):
    premisses = []
    for p in prems:
        try:
            premisses.append(CTFsyntax.Formula(p))
        except CTFsyntax.NotWellFormedFormulaError:
            # shittiest code ever
            # basically try again with added outer parentheses
            premisses.append(CTFsyntax.Formula(f'({p})'))
    try:
        conclusion = CTFsyntax.Formula(concl)
    except CTFsyntax.NotWellFormedFormulaError:
        conclusion = CTFsyntax.Formula(f'({concl})')
    argument = CTFdeduction.Inference(premisses, conclusion)
    tree = CTFdeduction.Tableau()
    tree.construct(argument)
    valid = argument.is_valid()
    show_arrows = True if valid else False
    pdfoutputpath = latexrender.LatexRenderTableau(tree).render(path, 'ctflogic', show_arrows)
    return [pdfoutputpath, argument, tree]


def render_K_Tableau_from_strings(prems, concl, path):
    premisses = []
    for p in prems:
        try:
            premisses.append(Ksyntax.KFormula(p))
        except CTFsyntax.NotWellFormedFormulaError:
            # shittiest code ever
            # basically try again with added outer parentheses
            premisses.append(Ksyntax.KFormula(f'({p})'))
    try:
        conclusion = Ksyntax.KFormula(concl)
    except CTFsyntax.NotWellFormedFormulaError:
        conclusion = Ksyntax.KFormula(f'({concl})')
    argument = Kdeduction.KInference(premisses, conclusion)
    tree = Kdeduction.KTableau()
    tree.construct(argument)
    #print([(node[0].string, node[0].worldnr) for node in tree.get_branches(tree.tree)[0]])
    valid = argument.is_valid()
    print(valid)
    show_arrows = True if valid else False
    pdfoutputpath = latexrender.LatexRenderTableau(tree).render(path, 'klogic', show_arrows)
    return [pdfoutputpath, argument, tree]



if __name__ == '__main__':
    #print(render_CTF_Tableau_from_strings(["((A->B)&(B->C))"], "(A->C)", os.getcwd()+"/logic/latex/"))
    #print(render_K_Tableau_from_strings(["(◻(A->B)&◻(B->C))"], "◻(A->C)", os.getcwd()+"/logic/latex/"))
    #print(render_K_Tableau_from_strings([], "(◇(A&B)->(◇A&◇B))", os.getcwd()+"/logic/latex/"))
    #print(render_K_Tableau_from_strings([], "((◇p&◇~q)->◇◻◇p)", os.getcwd()+"/logic/latex/"))
    #print(render_K_Tableau_from_strings([], "(◻a<->◻(~a->a))", os.getcwd()+"/logic/latex/"))
   # print(render_K_Tableau_from_strings([], "(~◇B->◻(B->A))", os.getcwd()+"/logic/latex/"))
    print(render_K_Tableau_from_strings(['(avb)','<>x','<>b'], "<>d", os.getcwd()+"/logic/latex/"))
#✸ (A ∧ B) ⊃ ( ✸ A ∧ ✸ B)
# A ≡  (¬A ⊃ A)
# ¬ ✸ B ⊃  (B ⊃ A)
#  A, ✸ B✸ (A ∧ B)
