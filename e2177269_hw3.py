class Term:
    """
    A class used to represent predicates, functions, variables or constants

    Attributes
    ----------
    name : str
        symbol of the term
    arguments : list
        a list containing the subterms of the term

    for p(x,f(y,A)):
        name : 'p'
        arguments : [t1, t2]
    t1:
        name : 'x'
        arguments : []
    t2:
        name : 'f'
        arguments : [t21, t22]
    t21:
        name : 'y'
        arguments : []
    t22:
        name : 'A'
        arguments : []
    """
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

    def __eq__(self, t2):
        """
        returns True if all symbols in the term are the same with those in t2
        (and the string representations of the two terms the same)
        """
        if not isinstance(t2, Term):
            return NotImplemented

        if self.name != t2.name:
            return False

        arg_len = len(self.arguments)
        if arg_len != len(t2.arguments):
            return False

        res = True
        for i in range(arg_len):
            res = res and self.arguments[i] == t2.arguments[i]

        return res

    def __ne__(self, t2):
        return not self == t2

    def __invert__(self):
        """
        returns a term which is the negation of this term(literal)
        """
        if self.name[0] == '~':
            return Term(self.name[1:], self.arguments)
        return Term('~' + self.name, self.arguments)

    def __str__(self):
        if self.arguments == []:
            return self.name

        argument_list = []
        for arg in self.arguments:
            argument_list.append(str(arg))

        literal_str = self.name + '(' + ','.join(argument_list) + ')'
        return literal_str

    @classmethod
    def from_string(cls, literal_str):
        """
        dissects the given input string and construct subterms recursively
        returns the root Term instance
        """
        if literal_str.find('(') == -1:
            name = literal_str
            arguments = []
            return cls(name, arguments)

        name = literal_str[:literal_str.find('(')]
        arguments_str = literal_str[literal_str.find('(') + 1:-1]
        argument_list = split(arguments_str)

        arguments = []
        for arg_str in argument_list:
            arg = Term.from_string(arg_str)
            arguments.append(arg)

        return cls(name, arguments)

    def unify(self, t2, theta):
        """
        returns True if this term and t2 are unifiable, false otherwise
        theta is a dict of substitutions that make the two terms identical

        (based on the unification algorithm given in S.Russell, P.Norvig -
            Artificial Intelligence. A Modern Approach)
        """
        if self == t2:
            return True
        if self.is_variable():
            return self.unify_var(t2, theta)
        if t2.is_variable():
            return t2.unify_var(self, theta)
        if self.is_compound() and t2.is_compound():
            # check if the functions/predicates are the same
            if self.name != t2.name:
                return False
            # unification of function/predicate terms
            for i in range(len(self.arguments)):
                try:
                    if not self.arguments[i].unify(t2.arguments[i], theta):
                        return False
                except:
                    return False
            return True
        else:
            return False

    def unify_var(self, t2, theta):
        """
        called by unify when a variable is reached
        params: self is a variable, t2 may or may not be a variable
        """
        if self.name in theta:
            return Term.from_string(theta[self.name]).unify(t2, theta)
        if t2.name in theta:
            return Term.from_string(theta[t2.name]).unify(self, theta)
        if self.occur_check(t2):
            return False
        theta[self.name] = str(t2)
        return True

    def is_variable(self):
        return not self.is_compound() and self.name.islower()

    def is_compound(self):
        return bool(self.arguments)

    def occur_check(self, t2):
        if self == t2:
            return True
        res = False
        for arg in t2.arguments:
            res = res or self.occur_check(arg)
        return res

    def substitute(self, theta):
        if self.name in theta:
            self.name = theta[self.name]
        if not self.arguments:
            return
        for arg in self.arguments:
            arg.substitute(theta)


class Clause:
    """
    A class used to represent a clause in CNF

    Attributes
    ----------
    literals : list
        a list of Term's denoting literals in the clause
    parent   : list
        a list of 2 Clause's which were used to produce this Clause
    level    : int
        the level of the Clause in the proof tree
        for the clauses given as input, this value is 0
    """
    def __init__(self, literals):
        self.literals = literals
        self.parent = None
        self.level = 0

    def __str__(self):
        if not self.literals:
            return "empty"
        literals = [str(l) for l in self.literals]
        return '+'.join(literals)

    def __eq__(self, c2):
        """
        returns True if all literals are the same with those in c2
        order of literals may be different
        (string representations of the two clauses may not be the same)
        """
        for l1 in self.literals:
            flag = False
            for l2 in c2.literals:
                if l1 == l2:
                    flag = True
            if not flag:
                return False
        return flag

    def __le__(self, c2):
        """
        returns True if the clause is subsumed by c2
        """
        theta = {}
        for l2 in c2.literals:
            flag = False
            for l1 in self.literals:
                if l1.unify(l2, theta):
                    l2_copy = Term.from_string(str(l2))
                    l2_copy.substitute(theta)
                    if l2_copy == l1:
                        flag = True
            if not flag:
                return False
        return True

    @classmethod
    def from_string(cls, clause_str):
        """
        dissects the given input str and call Term.from_string for each literal
        """
        literals = []
        literals_str = clause_str.split('+')
        for ls in literals_str:
            lit = Term.from_string(ls)
            literals.append(lit)
        return cls(literals)

    def factor(self):
        """
        searches the clause for two literals that are unifiable
        applies the unifier to the entire clause
        binary resolution + factoring : complete
        """
        theta = {}
        lit_len = len(self.literals)
        for i in range(lit_len - 1):
            l1 = self.literals[i]
            for l2 in self.literals[i + 1:]:
                if l1.unify(l2, theta):
                    self.literals.remove(l1)
                    self.substitute(theta)
                    return True
        return False

    def is_tautology(self):
        lit_len = len(self.literals)
        for i in range(lit_len - 1):
            l1 = self.literals[i]
            for l2 in self.literals[i + 1:]:
                if l1 == ~l2:
                    return True
        return False

    def resolve(self, clause2, resolvent):
        """
        params:
        -------
        clause2 : Clause
            the clause with which self is to be resolved
        resolvent : Clause
            initially self + clause2, will be updated if two literals from the
            two clauses have been found that are negation of each other and can
            be unified (in which case return value will be True)
        """
        for l1 in self.literals:
            for l2 in clause2.literals:
                theta = {}
                if l1.unify(~l2, theta):
                    l1_copy = Term.from_string(str(l1))
                    l1_copy.substitute(theta)
                    l2_copy = Term.from_string(str(l2))
                    l2_copy.substitute(theta)
                    if l1_copy != ~l2_copy:
                        continue
                    resolvent.eliminate(l1)
                    resolvent.eliminate(l2)
                    resolvent.substitute(theta)
                    return True
        return False

    def eliminate(self, literal):
        for sl in self.literals:
            if sl == literal:
                self.literals.remove(sl)

    def substitute(self, theta):
        for l in self.literals:
            l.substitute(theta)

    def is_subsumed_by(self, clause_list):
        for c in clause_list:
            if self <= c:
                return True
        return False


def split(arguments_str):
    """
    given an input string such as "x,f(x,y),z",
    returns the list ['x', 'f(x,y)', 'z']
    """
    argument_list = []

    while arguments_str:
        if arguments_str.find(',') == -1:
            argument_list.append(arguments_str)
            return argument_list
        if arguments_str.find('(') == -1:
            return argument_list + arguments_str.split(',')
        if arguments_str.find(',') < arguments_str.find('('):
            arg_partition = arguments_str.partition(',')
            argument_list.append(arg_partition[0])
            arguments_str = arg_partition[2]
        else:
            index = find_end_of_first_arg(arguments_str)
            argument_list.append(arguments_str[:index])
            arguments_str = arguments_str[index:]
            if arguments_str:
                arguments_str = arguments_str[1:]  # rid of leading comma

    return argument_list


def find_end_of_first_arg(arguments_str):
    """
    returns 1 + index of right parenthesis matching the leftmost parenthesis,
    which also marks the end of the first argument in arguments_str
    """
    i = 0
    counter = 0
    for c in arguments_str:
        i += 1
        if c == '(':
            counter += 1
        if c == ')':
            counter -= 1
            if counter == 0:
                break
    return i


def theorem_prover(base_clauses_str, negated_query_str):
    """
    a theorem prover for First Order Predicate Logic by using Resolution
    Refutation technique and Set of Support strategy with Breadth-First order.
    This function gets two lists of clauses, namely the list of base clauses
    and the list of clauses obtained from the negation of the theorem.
    """
    base_clause_list = []
    set_of_support = []
    construct_clauses_from_strings(base_clauses_str, base_clause_list)
    construct_clauses_from_strings(negated_query_str, set_of_support)

    while set_of_support:
        q = set_of_support.pop(0)

        for p in base_clause_list:
            resolvent = Clause.from_string(str(p) + "+" + str(q))
            resolved = p.resolve(q, resolvent)
            if resolved:
                subsumed = (resolvent.is_subsumed_by(set_of_support)
                            or resolvent.is_subsumed_by(base_clause_list))
                if subsumed or resolvent.is_tautology():
                    continue

                # apply factorization until no literals left to reduce
                while resolvent.factor():
                    pass
                resolvent.parent = [q, p]
                resolvent.level = max(p.level, q.level) + 1

                if not resolvent.literals:  # contradiction reached
                    print_resolution_path(resolvent)
                    return

                set_of_support.append(resolvent)

        base_clause_list.append(q)

    print("no", [])


def print_resolution_path(clause):
    output = []
    path = [clause]

    while path:
        c = pop_clause_with_max_level(path)
        if c.level:
            output.append(str(c.parent[0]) + "$"
                          + str(c.parent[1]) + "$"
                          + str(c))
            path.append(c.parent[0])
            path.append(c.parent[1])

    print("yes", output[::-1])


def pop_clause_with_max_level(path):
    max_k = path[0].level
    index = 0

    for i in range(1, len(path)):
        curr_k = path[i].level
        if curr_k > max_k:
            index = i
            max_k = curr_k

    return path.pop(index)


def construct_clauses_from_strings(clauses_str, clauses_list):
    """
    given a list of clauses in string form,
    constructs a list of Clause objects
    """
    for c_str in clauses_str:
        clause = Clause.from_string(c_str)
        clauses_list.append(clause)
