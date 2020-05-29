#!/usr/bin/python

from CTFLogic import syntax, semantics, deduction, validity

from pylatex import Document
import os

if __name__ == '__main__':
    a1 = syntax.Formula("((z&k)<->(y&m))")
    a2 = syntax.Formula("(d&(d->m))")
    c = syntax.Formula("(y->z)")
    tree = deduction.Tableau().construct(validity.Inference([a1,a2], c))
    text = "\\Tree["
    
    text += "]"
    doc = Document()
    doc.append(text)
    doc.generate_pdf(clean_tex=True)
