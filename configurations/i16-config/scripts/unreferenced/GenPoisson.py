from __future__ import generators
import math
import random


def GenPoisson(lambd):
    """
    Generates random Poisson variates with parameter I{lambd}.

    @type   lambd: C{float}
    @param  lambd: mean of Poisson pmf
    @rtype:        generator of I{ints}
    @return:       generator of independent Poisson variates
    """
    if lambd < 10:
        rand = random.random
        L = math.exp(-lambd)
        while True:
            k = 0
            p = 1
            while p >= L:
                k += 1
                p *= rand()
            yield k - 1
    else:
        alpha = int(7 * lambd / 8)
        gamma_var = random.gammavariate
        while True:
            X = gamma_var(alpha, 1)
            if X < lambd:
                new_lambd = lambd - X
                yield alpha + poisson_variate(new_lambd)
            else:
                yield binomial_variate(alpha - 1, lambd / X)

def poisson_variate(lambd):
    """
    Returns a random Poisson variate with parameter I{lambd}.

    @type   lambd: C{float}
    @param  lambd: mean of Poisson pmf
    @rtype:        I{int}
    @return:       Poisson variate
    """
    if lambd < 10:
        rand = random.random
        L = math.exp(-lambd)
        k = 0
        p = 1
        while p >= L:
            k += 1
            p *= rand()
        return k - 1
    else:
        a = int(7 * lambd / 8)
        X = random.gammavariate(a, 1)
        if X < lambd:
            new_lambd = lambd - X
            return a + poisson_variate(new_lambd)
        else:
            return binomial_variate(a - 1, lambd / X)


def binomial_variate(n, p):
    """
    Returns a random binomial variate with parameters I{n}
    and I{p}.

    @type  n: C{int}
    @param n: number of trials
    @type  p: C{float}
    @param p: probability of success
    @rtype:   I{int}
    @return:  number of successful trials
    """
    if n < 10:
        rand = random.random
        res = 0
        for _ in range(n):
            if rand() < p:
                res += 1
        return res
    else:
        a = 1 + n // 2
        b = n - a + 1
        X = random.betavariate(a, b)
        if X >= p:
            return binomial_variate(a - 1, p / X)
        else:
            return a + binomial_variate(b - 1, (p - X) / (1 - X))