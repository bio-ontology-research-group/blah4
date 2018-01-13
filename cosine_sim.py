#!/usr/bin/env python

import numpy as np
import pandas as pd
import click as ck
from multiprocessing import Pool
from sklearn.metrics.pairwise import cosine_similarity
from scipy.spatial.distance import cosine

@ck.command()
def main():
    pool = Pool(12)
    go_embeds = load_vectors('data/gos.vec')
    gos, go_vecs = [], []
    for go in go_embeds:
        go_id, go_vec = go
        gos.append(go_id)
        go_vecs.append(go_vec)
        
    prot_embeds = load_vectors('data/prots.vec')
    k = 100
    for prot in prot_embeds:
        prot_id, vec = prot
        prot_vecs = [vec] * len(go_vecs)
        vecs = zip(prot_vecs, go_vecs)
        res = pool.map(cosine_sml, vecs)
        res = zip(gos, res)
        res = sorted(res, key=lambda x: x[1], reverse=True)
        for i in range(k):
            print(prot_id, res[i][0], res[i][1])

def cosine_sml(vec):
    prot_vec, go_vec = vec
    return 1 - cosine(prot_vec, go_vec)

    
def load_vectors(filename):
    res = list()
    with open(filename) as f:
        for line in f:
            it = line.strip().split()
            vec = np.array(map(float, it[1:]), dtype=np.float32)
            res.append((it[0], vec))
    return res


if __name__ == '__main__':
    main()
