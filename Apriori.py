from collections import defaultdict
from itertools import combinations
import pandas as pd
import sys


def apriori(data, min_sup):
    output = dict()
    # first scan & test: find frequent 1-itemset
    current = count(data, [])
    current = {k: v for k, v in current.items() if v >= min_sup}

    while current:
        # generate candidate
        prev = current
        output.update(prev)
        candidate = gen_cand(prev)
        # scan & test
        if candidate:
            current = count(data, candidate)
            current = {k: v for k, v in current.items() if v >= min_sup}
        else:
            break

    return output


def count(data, candidate):
    current = defaultdict(lambda: 0)
    if candidate:
        for c in candidate:
            temp_c = set(c)
            for line in data:
                if temp_c == line.intersection(temp_c):
                    current[c] += 1
    else:  # first scan
        for line in data:
            for i in line:
                current[(i,)] += 1

    return current


def gen_cand(prev):
    k_ = len(list(prev.keys())[0]) - 1
    if k_ != 0:
        # self-joining
        temp_candidate = set()
        for i in combinations(prev.keys(), 2):
            target = set(i[0]).union(set(i[1]))
            if len(target) == k_ + 2:
                temp_candidate.add(tuple(target))
        # pruning
        candidate = set()
        for c in temp_candidate:
            done = True
            for i in range(k_ + 2):
                temp_c = tuple(sorted(c[:i] + c[i + 1:]))
                if not prev.get(temp_c):
                    done = False
                    break
            if done:
                candidate.add(tuple(sorted(c)))
        candidate = list(candidate)
    else:
        candidate = [tuple(sorted(set(i[0]).union(set(i[1])))) for i in combinations(prev.keys(), 2)]

    return candidate


def association_rules(frequent_itemsets, data):
    rules = dict()
    for k, v in frequent_itemsets.items():
        if len(k) > 1:
            for i in range(1, len(k)):
                for c in combinations(k, i):
                    c_ = tuple(set(k) - set(c))
                    if not rules.get((c, c_)):

                        count_c = count(data, [c])
                        confidence = 100 * (v / count_c[c])
                        rules[(c, c_)] = (
                        format(100 * (v / len(data)), '.2f'), format(confidence, '.2f'))  # support, confidence
    return rules


if __name__ == '__main__':
    # Data loading
    f = open(sys.argv[2], 'r')
    data = [set(map(int, i.rstrip('\n').split('\t'))) for i in f.readlines()]

    min_sup = float(sys.argv[1]) * 0.01 * len(data)

    # finding association rules using apriori
    frequent_itemsets = apriori(data, min_sup)
    rules = association_rules(frequent_itemsets, data)
    rules = pd.DataFrame([[set(k[0]), set(k[1]), v[0], v[1]] for k, v in rules.items()])

    rules.to_csv(sys.argv[3], sep='\t', header=False, index=False)