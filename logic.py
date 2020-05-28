#!/usr/bin/python

import logging
import re
# import shlex
# import sys
from enum import Enum


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
c_handler = logging.StreamHandler()
c_format = logging.Formatter('%(levelname)s: %(message)s')
c_handler.setFormatter(c_format)
logger.addHandler(c_handler)


class TFLogic():
    NOT = "¬"
    AND = "∧"
    OR = "∨"
    COND = "→"  # uses only 1 char
    BICOND = "↔"  # uses only 1 char
    SENLETTER = "[A-Z]"
    LPAREN = "[(]"
    RPAREN = "[)]"
    CONTRADICTION = "⊥"

    # additionally allowed (e.g. multi-char) variants
    ALLOWED_NOT = "~"
    ALLOWED_AND = "&"
    ALLOWED_OR = "v"
    ALLOWED_COND = "->"
    ALLOWED_BICOND = "<->"
    ALLOWED_CONTRADICTION = "#"

    class TruthMapping():
        @staticmethod
        def negation(a):
            s = {(1): 0,
                 (0): 1}
            return s.get((a))

        @staticmethod
        def conjunction(a, b):
            s = {(1, 1): 1,
                 (1, 0): 0,
                 (0, 1): 0,
                 (0, 0): 0}
            return s.get((a, b))

        @staticmethod
        def disjunction(a, b):
            s = {(1, 1): 1,
                 (1, 0): 1,
                 (0, 1): 1,
                 (0, 0): 0}
            return s.get((a, b))

        @staticmethod
        def conditional(a, b):
            s = {(1, 1): 1,
                 (1, 0): 0,
                 (0, 1): 1,
                 (0, 0): 1}
            return s.get((a, b))

        @staticmethod
        def biconditional(a, b):
            s = {(1, 1): 1,
                 (1, 0): 0,
                 (0, 1): 0,
                 (0, 0): 1}
            return s.get((a, b))

        # class Valuation():
        #     def __init__(self, values: dict):
        #         self.values = values

    @staticmethod
    def print_depth(depth):
        return "    "*depth

    @classmethod
    def prepare_string(cls, s):
        # replace multi-char variants with single characters
        # replace bicond first, since it contains cond
        s = re.sub(f'{cls.ALLOWED_BICOND}', cls.BICOND, s)
        s = re.sub(f'{cls.ALLOWED_COND}', cls.COND, s)
        # replace stuff with better-looking stuff
        s = re.sub(f'{cls.ALLOWED_NOT}', cls.NOT, s)
        s = re.sub(f'{cls.ALLOWED_AND}', cls.AND, s)
        s = re.sub(f'{cls.ALLOWED_OR}', cls.OR, s)
        s = re.sub(f'{cls.ALLOWED_CONTRADICTION}', cls.CONTRADICTION, s)
        return s

    @classmethod
    def is_sentence(cls, s, depth=0):
        logger.debug(f'{cls.print_depth(depth)}Asking if {s} is a sentence.')
        if cls.is_sentence_letter(s, depth):
            is_sentence = True
        elif cls.is_negation(s, depth):
            is_sentence = True
        elif cls.is_connective(s, depth):
            is_sentence = True
        else:
            is_sentence = False
        if is_sentence:
            if depth == 0:
                logger.info(f'{cls.print_depth(depth)} {s} '
                            'is a sentence.')
            else:
                logger.debug(f'{cls.print_depth(depth)}⇒ {s} '
                             'is a sentence.')
            return True
        else:
            if depth == 0:
                logger.info(f'{cls.print_depth(depth)} {s} '
                            'is NOT a sentence.')
            else:
                logger.debug(f'{cls.print_depth(depth)}⇒ {s} '
                             'is NOT a sentence.')
            return False

    @classmethod
    def is_sentence_letter(cls, s, depth=0):
        if re.match(f'^{cls.SENLETTER}$', s):
            logger.debug(f'{cls.print_depth(depth)}{s} '
                         'is a sentence letter.')
            return s
        else:
            logger.debug(f'{cls.print_depth(depth)}{s} '
                         'is NOT a sentence letter.')
            return False

    @classmethod
    def is_negation(cls, s, depth=0):
        if re.match(cls.NOT, s[0]):
            logger.debug(f'{cls.print_depth(depth)}{s} '
                         'starts with a negation sign.')
            if cls.is_sentence(s[1:], depth+1):
                logger.debug(f'{cls.print_depth(depth)}⇒ {s} '
                             'is a negation.')
                return s[1:]
            else:
                logger.info(f'{cls.print_depth(depth)}⇒ {s} '
                            'is NOT a negation.')
                return False
        else:
            # not starting with a negation sign
            # trivially not a negation
            logger.debug(f'{cls.print_depth(depth)}{s} '
                         'is NOT a negation.')
            return False

    @classmethod
    def is_connective(cls, s, depth=0):
        connected = cls.contains_central_connective(s)
        if connected:
            logger.debug(f'{cls.print_depth(depth)}{s} '
                         'is enclosed by parentheses and '
                         'contains a central connective.')
            left = connected[0]
            right = connected[1]
            connector = connected[2]
            logger.debug(f'{cls.print_depth(depth)}'
                         f'Asking first group [{left}]:')
            is_left = cls.is_sentence(left, depth+1)
            logger.debug(f'{cls.print_depth(depth)}'
                         f'Asking second group [{right}]:')
            is_right = cls.is_sentence(right, depth+1)
            if (is_left and is_right):
                logger.debug(f'{cls.print_depth(depth)}⇒ {s} '
                             'is a connective.')
                return [left, right, connector]
            else:
                logger.debug(f'{cls.print_depth(depth)}⇒ {s} '
                             'is NOT a connective.')
                return False
        else:
            # doesn't have a well-formed central connective
            # trivially not a connective
            logger.debug(f'{cls.print_depth(depth)}{s} '
                         'is not a connective.')
            return False

    @classmethod
    def contains_central_connective(cls, s, depth=0):
        paren_count, pos = 0, -1
        connective_pos = -1
        for c in s:
            pos += 1
            if re.match(f'^{cls.LPAREN}$', c):
                # add one depth (new parenthesis group)
                paren_count += 1
            elif re.match(f'^{cls.RPAREN}$', c):
                # close a parenthesis group
                paren_count -= 1
            if re.match(f'^({cls.AND}|{cls.OR}|{cls.COND}|{cls.BICOND})$', c):
                # we found a connective
                # now we check if it is in the outermost parenthesis group
                # that is, at depth 1
                logger.debug(f'Connective found at paren count {paren_count}')
                if paren_count == 1:
                    connective_pos = pos
                    break
        if connective_pos != -1:
            # found a central connective
            left = s[:connective_pos]
            right = s[connective_pos+1:]
            if (re.match(f'^{cls.LPAREN}$', left[0])
                    and re.match(f'^{cls.RPAREN}$', right[-1])):
                # also has appropriate enclosing parentheses
                # return the two connected subsentences
                left = left[1:]
                right = right[:-1]
                return [left, right, s[connective_pos]]
            else:
                # is not enclosed in parentheses
                logger.debug('Not enclosed in parentheses.')
                return False
        else:
            # does not contain a central connective
            logger.debug('No central connective found.')
            return False

    @classmethod
    def is_true(cls, sentence, valuation):
        s, v = sentence, valuation
        if not cls.is_sentence(s):
            logger.warning(f'{s} is not a sentence.')
            return False
        else:
            if res := cls.is_sentence_letter(s):
                # return the valuation of the sentence letter
                return v[res]
            elif res := cls.is_negation(s):
                # return the negation of the truth value of the subsentence
                val = cls.is_true(res, v)
                return cls.TruthMapping.negation(val)
            elif res := cls.is_connective(s):
                # return the corresponding connector-mapping of the subsentence
                vl = cls.is_true(res[0], v)  # left subsentence
                vr = cls.is_true(res[1], v)  # right subsentence
                connector = res[2]
                if connector == cls.AND:
                    # conjunction
                    return cls.TruthMapping.conjunction(vl, vr)
                elif connector == cls.OR:
                    # disjunction
                    return cls.TruthMapping.disjunction(vl, vr)
                elif connector == cls.COND:
                    # conditional
                    return cls.TruthMapping.conditional(vl, vr)
                elif connector == cls.BICOND:
                    # biconditional
                    return cls.TruthMapping.biconditional(vl, vr)

    @classmethod
    def is_tautology(cls, sentence):
        logger.info('Checking if the expression is a sentence...')
        if not cls.is_sentence(sentence):
            logger.warning(f'{sentence} is not a sentence.')
            return False
        logger.info('Checking if the sentence is a tautology...')

        # get all possible valuations
        val = cls.get_all_possible_valuations(sentence)

        # look through all valuations
        for v in val:
            if not cls.is_true(sentence, v):
                # found a valuation that is False
                logger.info(f'Valuation {v} turns sentence {sentence} false.')
                return False
        # all valuations returned True
        logger.info(f'Sentence {sentence} is true '
                    'under all possible valuations. TAUTOLOGY.')
        return True

    @classmethod
    def is_contradiction(cls, sentence):
        logger.info('Checking if the expression is a sentence...')
        if not cls.is_sentence(sentence):
            logger.warning(f'{sentence} is not a sentence.')
            return False
        logger.info('Checking if the sentence is a contradiction...')

        # get all possible valuations
        val = cls.get_all_possible_valuations(sentence)

        # look through all valuations
        for v in val:
            if cls.is_true(sentence, v):
                # found a valuation that is True
                logger.info(f'Valuation {v} turns sentence {sentence} true.')
                return False
        # all valuations returned True
        logger.info(f'There are no possible valuations under which '
                    f'sentence {sentence} is true. CONTRADICTION.')
        return True

    @classmethod
    def get_all_possible_valuations(cls, sentence):
        # get all sentence letters
        senlets = re.findall(cls.SENLETTER, sentence)
        senlets = set(senlets)  # make unique
        senlets = list(senlets)  # make ordered

        # get all possible valuations
        val = []
        dims = len(senlets)
        maxnum = (2 ** dims)
        logger.debug(f'maxnum = {maxnum}')
        logger.debug(f'dims = {dims}')
        for i in range(maxnum):
            val.append({})
        for i in range(1, dims+1):
            for j in range(1, maxnum+1):
                modulo = j % (2**i)
                if (modulo <= ((2**i)/2) and modulo != 0):
                    val[j-1][senlets[i-1]] = 1
                else:
                    val[j-1][senlets[i-1]] = 0

        return val

    @classmethod
    def is_equivalent(cls, s1, s2):
        logger.info('Checking if the expressions are sentences...')
        if not cls.is_sentence(s1):
            logger.warning(f'{s1} is not a sentence.')
            return False
        if not cls.is_sentence(s2):
            logger.warning(f'{s2} is not a sentence.')
            return False
        logger.info('Checking if the sentences are equivalent...')

        # get all possible valuations
        val = cls.get_all_possible_valuations(s1+s2)

        # look through all valuations
        for v in val:
            if cls.is_true(s1, v):
                if not cls.is_true(s2, v):
                    logger.info(f'Valuation {v} turns sentence {s1} true, '
                                f'but sentence {s2} false.')
                    return False
            if not cls.is_true(s1, v):
                if cls.is_true(s2, v):
                    logger.info(f'Valuation {v} turns sentence {s1} false, '
                                f'but sentence {s2} true.')
                    return False
        logger.info(f'There are no possible valuations under which '
                    f'sentence {s1} has the opposite truth value of '
                    f'sentence {s2}. EQUIVALENT.')
        return True

    @classmethod
    def is_jointly_satisfiable(cls, s1, s2):
        logger.info('Checking if the expressions are sentences...')
        if not cls.is_sentence(s1):
            logger.warning(f'{s1} is not a sentence.')
            return False
        if not cls.is_sentence(s2):
            logger.warning(f'{s2} is not a sentence.')
            return False
        logger.info('Checking if the sentences are jointly satisfiable...')

        # get all possible valuations
        val = cls.get_all_possible_valuations(s1+s2)

        # look through all valuations
        for v in val:
            if cls.is_true(s1, v):
                if cls.is_true(s2, v):
                    logger.info(f'Valuation {v} turns both sentence {s1} '
                                f'and sentence {s2} true. '
                                'JOINTLY SATISFIABLE.')
                    return True
        logger.info(f'There are no possible valuations under which '
                    f'sentence {s1} and sentence {s2} '
                    f'are both true. JOINTLY UNSATISFIABLE.')
        return False

    @classmethod
    def is_jointly_unsatisfiable(cls, s1, s2):
        return not cls.is_jointly_satisfiable(s1, s2)

    @classmethod
    def is_entailment(cls, conclusion, *args):
        all_sentences = ""
        logger.info('Checking if the expressions are sentences...')
        for s in args:
            if not cls.is_sentence(s):
                logger.warning(f'{s} is not a sentence.')
                return False
            else:
                all_sentences += s

        logger.info('Checking if the sentences entail the conclusion...')
        val = cls.get_all_possible_valuations(all_sentences)

        def all_premises_true(v):
            for s in args:
                if not cls.is_true(s, v):
                    return False
            return True

        # check all possible valuations
        for v in val:
            # a valuation can only disprove the entailment
            # if it is true on all premises
            if not all_premises_true(v):
                continue
            else:
                # an evaluation which is true on all premises
                # but false on the conclusion disproves the entailment
                if not cls.is_true(conclusion, v):
                    logger.info(f'Under the valuation {v}, '
                                f'all of {args} are true but '
                                f'{conclusion} is false. NO ENTAILMENT.')
                    return False

        # there was no counterexample, so it's true
        logger.info(f'There is no valuation in which '
                    f'all of {args} are true but '
                    f'{conclusion} is false. ENTAILMENT.')
        return True

    class Rule(Enum):
        REIT = 0
        CONJ_INT = 1
        CONJ_ELIM = 2
        COND_INT = 3
        COND_ELIM = 4
        NEG_INT = 5
        NEG_ELIM = 6
        INDPROOF = 7
        BICOND_INT = 8
        BICOND_ELIM = 9
        DIS_INT = 10
        DIS_ELIM = 11
        EXPLOSION = 12
        ASSUMPTION = 13

    class DeductionStep():
        def __init__(self, sentence, depth, rule, *ruleargs):
            self.sentence = sentence
            self.depth = depth
            self.rule = rule
            self.ruleargs = ruleargs

    @classmethod
    def is_applied_rule(cls, past_deduction_steps, new_deduction_step):
        rule = {
            cls.Rule.REIT: cls.is_reit,
            # cls.Rule.CONJ_INT: cls.is_conj_int,
            # cls.Rule.CONJ_ELIM: cls.is_conj_elim,
            # cls.Rule.COND_INT: cls.is_cond_int,
            # cls.Rule.COND_ELIM: cls.is_cond_elim,
            # cls.Rule.NEG_INT: cls.is_neg_int,
            # cls.Rule.NEG_ELIM: cls.is_neg_elim,
            # cls.Rule.INDPROOF: cls.is_indproof,
            # cls.Rule.BICOND_INT: cls.is_bicond_int,
            # cls.Rule.BICOND_ELIM: cls.is_bicond_elim,
            # cls.Rule.DIS_INT: cls.is_dis_int,
            # cls.Rule.DIS_ELIM: cls.is_dis_elim,
            cls.Rule.EXPLOSION: cls.is_explosion,
            # cls.Rule.ASSUMPTION: cls.is_assumption
            }
        return rule.get(new_deduction_step.rule)(past_deduction_steps,
                                                 new_deduction_step)

    def ensure_right_depth(func):
        def wrapper(cls, past_deduction_steps, new_deduction_step):
            d_old = past_deduction_steps[-1].depth
            d_new = new_deduction_step.depth
            if abs(d_new - d_old) > 1:
                logger.info('Can\'t jump more than 1 depth in any direction.')
                return False
            if d_new > d_old:
                if not new_deduction_step.rule == cls.Rule.ASSUMPTION:
                    logger.info('Only assumptions can open a subproof.')
                    return False
            # TODO Check that -1, so a step out of a subproof, is allowed
            #      for the current rule
            return func(cls, past_deduction_steps, new_deduction_step)
        return wrapper

    def ensure_no_closed_subproof(func):
        def wrapper(cls, past_deduction_steps, new_deduction_step):
            n = new_deduction_step
            cited_line = n.ruleargs[0]
            if cls.is_in_closed_subproof(
                    past_deduction_steps + [new_deduction_step],
                    cited_line,
                    len(past_deduction_steps)):
                logger.info(f'Line {cited_line} is in a closed subproof.')
                return False
            return func(cls, past_deduction_steps, new_deduction_step)
        return wrapper

    @classmethod
    def is_in_closed_subproof(cls, steps, cited_line, ref_line):
        if steps[cited_line].depth == 0:
            return False
        nsteps = steps[cited_line+1:ref_line+1]
        for s in nsteps:
            if s.depth < steps[cited_line].depth:
                return True
            elif (s.rule == cls.Rule.ASSUMPTION and
                  s.depth == steps[cited_line].depth):
                return True
        return False

    @classmethod
    @ensure_right_depth
    @ensure_no_closed_subproof
    def is_reit(cls, past_deduction_steps, new_deduction_step):
        cited_line = new_deduction_step.ruleargs[0]
        if (past_deduction_steps[cited_line].sentence
                == new_deduction_step.sentence):
            return True
        else:
            logger.info(f'The sentence at line {cited_line} '
                        f'[{past_deduction_steps[cited_line].sentence}] '
                        f'is not the same as the new sentence.')
            return False

    @classmethod
    @ensure_right_depth
    @ensure_no_closed_subproof
    def is_explosion(cls, past_deduction_steps, new_deduction_step):
        cited_line = new_deduction_step.ruleargs[0]
        if re.match(f'^{cls.CONTRADICTION}$',
                    past_deduction_steps[cited_line].sentence):
            return True
        else:
            logger.info(f'The sentence at line {cited_line} '
                        f'[{past_deduction_steps[cited_line].sentence}] '
                        f'is not {cls.CONTRADICTION}.')
            return False

    def is_theorem():
        pass

    def is_provably_equivalent():
        pass

    def is_provably_consistent():
        pass

    def is_provably_inconsistent():
        pass

    @classmethod
    def is_valid(cls, conclusion, *args):
        result = cls.is_entailment(conclusion, *args)
        if result:
            logger.info(f'The argument consisting of the premises {args} '
                        f'and the conclusion {conclusion} is valid.')


class FOLogic(TFLogic):
    pass


def is_sentence(s):
    if TFLogic.is_sentence(TFLogic.prepare_string(s)):
        print(f'{s} is a sentence.')
    else:
        print(f'{s} is not a sentence.')


def is_true(s):
    valuation = {'R': 0,
                 'B': 0}
    print(f'{valuation}')
    result = TFLogic.is_true(TFLogic.prepare_string(s))
    print(f'{result}')


# if executed as a script
if __name__ == "__main__":
    # args = shlex.split(sys.argv[1])
    # s = TFLogic.prepare_string(args[0])
    # s2 = TFLogic.prepare_string(args[1])
    # print(f'{s}, {s2}')
    t = TFLogic
    p = []
    p.append(t.DeductionStep("AvB", 0, t.Rule.ASSUMPTION))  # 0
    p.append(t.DeductionStep("~B", 0, t.Rule.ASSUMPTION))  # 1
    p.append(t.DeductionStep("A", 1, t.Rule.ASSUMPTION))  # 2
    p.append(t.DeductionStep("A", 1, t.Rule.REIT, 2))  # 3
    p.append(t.DeductionStep("B", 1, t.Rule.ASSUMPTION))  # 4
    p.append(t.DeductionStep(t.prepare_string("#"), 1, t.Rule.NEG_ELIM, 1, 4))  # 5
    p.append(t.DeductionStep("B", 2, t.Rule.ASSUMPTION))  # 6
    # p.append(t.DeductionStep("A", 0, t.Rule.EXPLOSION, 5)) # 7

    # new = t.DeductionStep("B", 2, t.Rule.REIT, 4)
    new = t.DeductionStep("C", 2, t.Rule.EXPLOSION, 5)
    print(t.is_applied_rule(p, new))
