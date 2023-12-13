from XORSampler_smt import XORSampler


if __name__ == "__main__":
    smtstr = open("3cnf-10-20.smt2", 'r').read()
    sample_var_list = ['x1', 'x2', 'x3', 'x4', 'x5', 'x6', 'x7', 'x8', 'x9', 'x10']

    sampler = XORSampler(smtstr, sample_var_list=sample_var_list,
                         no_of_xor=5, p=.5, max_sample=100, max_loop=1000,
                         need_only_one_sol=True, need_blocking=False)
    res, samples = sampler.sample()

    print(f"{len(samples)} solution samples from the given SMT constraints were produced through xor sampling, as listed below:")
    for sample in samples:
        print(",".join(sample))