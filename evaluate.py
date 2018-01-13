#!/usr/bin/env python
import click as ck
import numpy as np
import pandas as pd
from utils import get_ontology, get_anchestors, EXP_CODES
from sklearn.metrics import roc_curve, auc
from matplotlib import pyplot as plt


@ck.command()
def main():
    global go
    go = get_ontology('data/go.obo')
    scores = load_scores()
    annots = load_annotations()
    common = set(scores).intersection(set(annots))
    print('Evaluating proteins: ', len(common))
    test = list()
    pred = list()
    for prot in common:
        for go_id, score in scores[prot].items():
            pred.append(score)
            if go_id in annots[prot]:
                test.append(1)
            else:
                test.append(0)
    compute_roc(pred, test)

def compute_roc(scores, test):
    # Compute ROC curve and ROC area for each class
    fpr, tpr, _ = roc_curve(test, scores)
    roc_auc = auc(fpr, tpr)
    plt.figure()
    plt.plot(
        fpr,
        tpr,
        label='ROC curve (area = %0.2f)' % roc_auc)
    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curve - Protein Functions')
    plt.legend(loc="lower right")
    plt.savefig('ROC.png')
    print('ROC AUC: ', roc_auc)
    return roc_auc

def load_scores():
    scores = dict()
    with open('data/cosine.out') as f:
        for line in f:
            it = line.strip().split()
            prot = it[0].strip('()\',')
            go_id = it[1].strip('()\',').upper()
            score = float(it[2].strip('()\','))
            if prot not in scores:
                scores[prot] = {}
            if go_id in go:
                gos = get_anchestors(go, go_id)
                gos.add(go_id)
                for g_id in gos:
                    if g_id not in scores[prot]:
                        scores[prot][g_id] = score
                    else:
                        scores[prot][g_id] = max(scores[prot][g_id], score)
    return scores


def load_annotations():
    mapping = load_mapping()
    annots = dict()
    with open('data/goa_human.gaf') as f:
        for line in f:
            if line.startswith('!'):
                continue
            it = line.strip().split('\t')
            ac = it[1]
            if it[3] == 'NOT' or it[6] not in EXP_CODES:
                continue
            go_id = it[4]
            if ac not in mapping:
                continue
            prot = mapping[ac]
            if prot not in annots:
                annots[prot] = set()
            if go_id in go:
                annots[prot].add(go_id)
                annots[prot] |= get_anchestors(go, go_id)
    return annots
            

def load_mapping():
    mapping = dict()
    with open('data/mapping.tab') as f:
        next(f)
        for line in f:
            it = line.strip().split()
            mapping[it[0]] = it[1].lower()

    return mapping

if __name__ == '__main__':
    main()
