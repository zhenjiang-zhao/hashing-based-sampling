import random
from z3 import Solver


class XORSampler:
    def __init__(self, smt_str, sample_var_list, sample_constraints="", no_of_xor=5, p=.5, max_sample=100, max_loop=1000,
                 need_only_one_sol=True, need_blocking=False):
        self.smt_str = smt_str
        self.sample_var_list = sample_var_list
        self.no_of_xor = no_of_xor
        self.p = p
        self.max_sample = max_sample
        self.max_loop = max_loop
        self.need_only_one_sol = need_only_one_sol
        self.need_blocking = need_blocking

        self.smt2_content = {"original" : smt_str+"\n\n"+sample_constraints+"\n\n", "xor" : [], "blocking_loop1" : [], "blocking_loop2" : "", "check" : "\n(check-sat)\n(get-model)"}
        self.blocking_str = ""
        self.res = dict()
        self.samples = list()

    def create_input_string(self, in_loop_1=True):
        # update the self.smt_str
        smt_str = ""
        smt_str += self.smt2_content["original"]

        for lines in self.smt2_content["xor"]:
            smt_str += "%s" % lines
        for lines in self.smt2_content["blocking_loop1"]:
            smt_str += "%s" % lines
        if not in_loop_1:
            smt_str += "%s" % self.smt2_content["blocking_loop2"]
        smt_str += self.smt2_content["check"]
        self.smt_str = smt_str

    def analysis_z3Output(self, in_loop_1=True):
        # find a solution of self.smt_str
        solver = Solver()
        solver.from_string(self.smt_str)
        if "unsat" == str(solver.check()):
            # there is no solution
            return False
        elif in_loop_1:
            # save the found solution to self.res
            model = solver.model()
            for item in model:
                self.res[str(item)] = str(model[item])
        return True  # sat

    def have_sol(self):
        self.create_input_string()
        if self.analysis_z3Output():
            self.blocking_str = ""
            for var in self.sample_var_list:
                self.blocking_str += " (= " + var + " " + self.res[var].lower() + ")"
            return True
        else:
            return False

    def generate_XOR(self):
        # generate XOR clauses
        self.smt2_content["xor"].clear()
        for _ in range(0, self.no_of_xor):
            xor_str = ""
            for var in self.sample_var_list:
                if random.random() > self.p:
                    xor_str += " " + var
            if random.random() > 0.5:
                xor_str = xor_str + " true"
            if xor_str != "":
                self.smt2_content["xor"].append("(assert (xor%s))\n" % xor_str)

    def have_another_sol(self):
        self.smt2_content["blocking_loop2"] = "(assert (not (and%s)))\n" % self.blocking_str
        self.create_input_string(in_loop_1=False)
        self.smt2_content["blocking_loop2"] = ""
        return self.analysis_z3Output(in_loop_1=False)

    def generate_simple_ins(self):
        res = list()
        for var in self.sample_var_list:
            res.append(self.res[var].lower())
        self.samples.append(res)

    def add_blocking(self):
        self.smt2_content["blocking_loop1"].append("(assert (not (and%s)))\n" % self.blocking_str)

    def sample(self):
        """
        The goal here is to sample the solutions of the given SMT formula (i.e., self.smt_str) by hashing-based sampling.
        """
        # check if self.smt_str has any solution
        solver = Solver()
        solver.from_string(self.smt_str + "\n(check-sat)\n(get-model)")
        if "unsat" == str(solver.check()):
            # if self.smt_str does not have any solution, there is no need for sampling
            return False, []

        satFlag = False
        i = 0
        no_of_sample = 0

        while i < self.max_loop and no_of_sample < self.max_sample:
            i += 1
            # randomly generate XOR Clauses
            self.generate_XOR()
            # sample a solution
            satFlag = self.have_sol()

            if satFlag:
                # sat: found a solution
                if self.need_only_one_sol:
                    # check whether a solution is unique or not
                    if not self.have_another_sol():
                        # the solution is unique
                        pass
                    else:
                        # have found another solution
                        # do not save this solution as a sample
                        continue

                # add the solution to the set of samples (i.e., self.samples)
                self.generate_simple_ins()
                no_of_sample += 1
                if self.need_blocking:
                    self.add_blocking()
            else:
                # unsat: there is no solution found
                continue

        return True if len(self.samples) != 0 else False, self.samples