#!/usr/bin/env python
import click as ck
import numpy as np
import pandas as pd
import gzip
from nltk.corpus import stopwords
import string
from utils import get_ontology, filter_specific

@ck.command()
def main():
    global stop
    stop = set(stopwords.words('english'))
    normalize_corpus()
    # remove_superclasses()


def remove_superclasses():
    data = list()
    go = get_ontology('data/go.obo')
    w = open('data/human_go_matches_specific.tsv', 'w')
    with open('data/human_go_matches_sorted.tsv') as f:
        for line in f:
            it = line.strip().split('\t')
            pid = it[0]
            st = it[1]
            ed = it[2]
            annots = it[3]
            if annots.startswith('GO'):
                gos = [go_id for go_id in annots.split('|') if go_id in go]
                gos = filter_specific(go, gos)
                annots = ' '.join(gos)
            w.write('%s\t%s\t%s\t%s\n' % (pid, st, ed, annots))
            
    
def sort_annotations():
    data = list()
    with open('data/human_go_matches_merged.tsv') as f:
        next(f)
        for line in f:
            it = line.strip().split('\t')
            pid = int(it[0])
            st = int(it[1])
            ed = int(it[2])
            annots = it[3]
            data.append((pid, st, ed, annots))
    data = sorted(data, key=lambda x: (x[0], x[1], x[2]))
    with open('data/human_go_matches_sorted.tsv', 'w') as f:
        for it in data:
            f.write('%d\t%d\t%d\t%s\n' % it)

def ok(word):
    if len(word) < 3:
        return False
    if word in stop:
        return False
    return True


def remove_stopwords():
    w = open('data/corpus_final.txt', 'w')
    with open('data/corpus.txt') as f:
        for line in f:
            words = line.strip().split()
            words = [word.strip(':') for word in words if ok(word)]
            if len(words) > 0:
                w.write(words[0])
                for i in range(1, len(words)):
                    w.write(' ' + words[i])
                w.write('\n')
    w.close()

def normalize_corpus():
    f1 = open('data/medline_abstract_filtered.tsv')
    f2 = open('data/human_go_matches_specific.tsv')
    w = open('data/corpus.txt', 'w')
    punctuation = '!"#$%&\'()*+,-_./;<=>?@[\\]^`{}~'
    for line in f1:
        it = line.strip().split('\t')
        pid = int(it[0])
        title = it[1]
        if len(it) > 2:
            abstract = it[2]
        else:
            abstract = ''
        text = title + ' ' + abstract
        annots = list()
        apid = -1
        while True:
            if apid == -1 or pid >= apid:
                line = next(f2, '').strip()
                if line == '':
                    break
                it = line.split('\t')
                apid = int(it[0])
                start = int(it[1])
                end = int(it[2])
                annot = it[3]
                # print(pid, apid)
                if pid == apid:
                    annots.append((start, end, annot))
            else:
                break
        # annots = sorted(annots, key=lambda x: (x[0], x[1]))
        start = 0
        new_text = ''
        for ann in annots:
            s, e, gene_id = ann
            new_text += text[start:s] + ' ' + gene_id + ' '
            start = e + 1
        new_text += text[start:]
        new_text = new_text.lower()
        table = string.maketrans("", "")
        new_text = new_text.translate(table, punctuation)
        new_text = new_text.replace("  ", " ")
        words = new_text.split()
        words = [word.strip(':') for word in words if ok(word)]
        if len(words) > 0:
            w.write(words[0])
            for i in range(1, len(words)):
                w.write(' ' + words[i])
            w.write('\n')
    f1.close()
    f2.close()
    w.close()


def run():
    pids = set()
    with open('data/human_go_matches_sorted.tsv') as f:
        for line in f:
            it = line.strip().split('\t')
            pids.add(int(it[0]))

    w = open('data/medline_abstract_filtered.tsv', 'w')
    data = list()
    with open('data/medline_abstracts.tsv') as f:
        for line in f:
            it = line.strip().split('\t')
            pid = int(it[0])
            if pid in pids:
                data.append((pid, line))
    data = sorted(data, key=lambda x: x[0])
    for it in data:
        w.write(it[1])
    w.close()


def merge_annotations():
    w = open('data/human_go_matches_merged.tsv', 'w')
    with open('data/human_go_matches.tsv') as f:
        for i in range(2):
            next(f)
        cpid = ''
        cst = ''
        cend = ''
        cgo_id = ''
        for line in f:
            it = line.strip()[1: -1].split(',')
            if len(it) != 4:
                continue
            pid = it[0]
            st = it[1]
            end = it[2]
            go_id = it[3]
            if cpid == pid and cst == st and cend == end:
                cgo_id += '|' + go_id
            else:
                w.write('%s\t%s\t%s\t%s\n' % (cpid, cst, cend, cgo_id))
                cpid = pid
                cst = st
                cend = end
                cgo_id = go_id
    w.close()
            


if __name__ == '__main__':
    main()
