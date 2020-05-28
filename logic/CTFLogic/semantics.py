#!/usr/bin/python

import syntax
import validity

import re


class TruthExtensionMapping():
    negation = {(1,): 0,
                (0,): 1}

    conjunction = {(1, 1): 1,
                   (1, 0): 0,
                   (0, 1): 0,
                   (0, 0): 0}

    disjunction = {(1, 1): 1,
                   (1, 0): 1,
                   (0, 1): 1,
                   (0, 0): 0}

    conditional = {(1, 1): 1,
                   (1, 0): 0,
                   (0, 1): 1,
                   (0, 0): 1}

    biconditional = {(1, 1): 1,
                     (1, 0): 0,
                     (0, 1): 0,
                     (0, 0): 1}

    @classmethod
    def get_truth(cls, form: syntax.Form, subtruths):
        s = {
            syntax.Form.NEGATION: cls.negation,
            syntax.Form.CONJUNCTION: cls.conjunction,
            syntax.Form.DISJUNCTION: cls.disjunction,
            syntax.Form.CONDITIONAL: cls.conditional,
            syntax.Form.BICONDITIONAL: cls.biconditional
        }
        return s.get(form).get(tuple(subtruths))


class Interpretation():
    def __init__(self, assignments):
        self.assignments = assignments

    def get_truth(self, f: syntax.Formula):
        if f.form == syntax.Form.ATOMIC:
            return self.assignments[f.string]
        else:
            subtruths = []
            for i in f.subformulas:
                subtruths.append(self.get_truth(i))
            return TruthExtensionMapping.get_truth(f.form, subtruths)


class Inference(validity.Inference):
    def __init__(self, premisses, conclusion):
        self.premisses = premisses
        self.conclusion = conclusion
        self.interpretations = self.get_all_interpretations()

    def is_valid(self):
        # inner loop to check all premisses are true
        def makes_all_premisses_true(interpretation):
            for premiss in self.premisses:
                if interpretation.get_truth(premiss) == 0:
                    return False
            return True
        # check all interpretations
        for i in self.interpretations:
            if not makes_all_premisses_true(i):
                continue
            else:
                # if an interpretation makes all premisses true
                # but the conclusion false, the inference is invalid
                if i.get_truth(self.conclusion) == 0:
                    return False
        return True

    def get_all_interpretations(self):
        # get all sentence letters
        sentence_strings = ""
        for s in self.premisses:
            sentence_strings += s.string
        sentence_strings += self.conclusion.string
        pattern = syntax.re_pattern(syntax.ATOMICS, anywhere=True)
        senlets = re.findall(pattern, sentence_strings)
        senlets = set(senlets)  # make unique
        senlets = list(senlets)  # make ordered

        # get all possible interpretation
        interpretations = []
        dims = len(senlets)  # count of parameters/sentence letters
        maxnum = (2 ** dims)  # count of possible interpretations
        for i in range(maxnum):
            interpretations.append(Interpretation({}))
        for parameter in range(1, dims+1):
            for valuation in range(1, maxnum+1):
                # for every parameter, increase the "step" before value switch
                # (e.g. 101010 vs 11001100 vs 11110000 etc.)
                # via modulo operation
                modulo = valuation % (2**parameter)
                if (modulo <= ((2**parameter)/2) and modulo != 0):
                    interpretations[
                        valuation-1].assignments[senlets[parameter-1]] = 1
                else:
                    interpretations[
                        valuation-1].assignments[senlets[parameter-1]] = 0
        return interpretations


class Formula(syntax.Formula):
    def is_logical_truth(self):
        return Inference([], self).is_valid()
    is_tautology = is_logical_truth
