#!/usr/bin/python

from logic.CTFLogic import semantics
from logic.CTFLogic import syntax

from . import syntax

class KTruthExtensionMapping(semantics.TruthExtensionMapping):
    @classmethod
    def get_truth(cls, form: syntax.KForm, subtruths):
        s = {
            syntax.KForm.NEGATION: cls.negation,
            syntax.KForm.CONJUNCTION: cls.conjunction,
            syntax.KForm.DISJUNCTION: cls.disjunction,
            syntax.KForm.CONDITIONAL: cls.conditional,
            syntax.KForm.BICONDITIONAL: cls.biconditional
        }
        return s.get(form).get(tuple(subtruths))

class KInterpretation(semantics.Interpretation):
    def __init__(self, worlds, worldrelations, assignments):
        self.worlds = worlds
        self.worldrelations = worldrelations
        self.assignments = assignments

    def get_atomic_truth(self, world, parameter):
        tup = [world, parameter]
        return self.assignments.get(tuple(tup))

    def get_truth(self, world, f: syntax.KFormula):
        if f.form == syntax.KForm.ATOMIC:
            return self.get_atomic_truth(world, f.string)
        elif f.form == syntax.KForm.NECESSARY:
            return self.get_necessary(world, f)
        elif f.form == syntax.KForm.POSSIBLE:
            return self.get_possible(world, f)
        else:
            subtruths = []
            for i in f.subformulas:
                subtruths.append(self.get_truth(world, i))
            return KTruthExtensionMapping.get_truth(
                f.form, subtruths)

    def get_necessary(self, world, f):
        for w in self.worlds:
            if w in self.worldrelations[world]:
                if self.get_truth(w, f.subformulas[0]) == 0:
                    return 0
        return 1

    def get_possible(self, world, f):
        for w in self.worlds:
            if w in self.worldrelations[world]:
                if self.get_truth(w, f.subformulas[0]) == 1:
                    return 1
        return 0

if __name__ == "__main__":
    a = syntax.KFormula("◇~a")
    b = syntax.KFormula("~◻a")
    ass = {(0,'a'):1, (1,'a'):1, (2,'a'):0}
    worlds = [0,1,2]
    worldrelations = [[1,2],[2],[0]]
    inter = KInterpretation(worlds,worldrelations,ass)
    print(inter.get_truth(0,a))
    print(inter.get_truth(1,a))
    print(inter.get_truth(2,a))
    print(inter.get_truth(0,b))
    print(inter.get_truth(1,b))
    print(inter.get_truth(2,b))
