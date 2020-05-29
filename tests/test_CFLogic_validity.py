import unittest
import csv
import os

from logic.CTFLogic import semantics, deduction, syntax


class ValidityTestCase(unittest.TestCase):
    def setUp(self):
        self.logical_truths = []
        self.valid_arguments = []
        my_dir = os.path.dirname(__file__)
        formula_file = os.path.join(my_dir, 'tautologies.csv')
        argument_file = os.path.join(my_dir, 'arguments.csv')
        with open(formula_file, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                self.logical_truths.append(row[0])
        with open(argument_file, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                self.valid_arguments.append(row)

    def test_semantic_logical_truths(self):
        for i in self.logical_truths:
            self.assertTrue(semantics.Formula(i).is_logical_truth())
            self.assertFalse(semantics.Formula("~"+i).is_logical_truth())

    def test_proof_logical_truths(self):
        for i in self.logical_truths:
            self.assertTrue(deduction.Formula(i).is_logical_truth())
            self.assertFalse(deduction.Formula("~"+i).is_logical_truth())

    def test_semantic_inference(self):
        for i in self.valid_arguments:
            premisses = [syntax.Formula(a) for a in i[:-1]]
            conclusion = syntax.Formula(i[-1])
            nonconclusion = syntax.Formula("~"+i[-1])
            self.assertTrue(
                semantics.Inference(premisses, conclusion).is_valid())
            self.assertFalse(
                semantics.Inference(premisses, nonconclusion).is_valid())

    def test_proof_inference(self):
        for i in self.valid_arguments:
            premisses = [syntax.Formula(a) for a in i[:-1]]
            conclusion = syntax.Formula(i[-1])
            nonconclusion = syntax.Formula("~"+i[-1])
            self.assertTrue(
                deduction.Inference(premisses, conclusion).is_valid())
            self.assertFalse(
                deduction.Inference(premisses, nonconclusion).is_valid())


if __name__ == '__main__':
    unittest.main()
