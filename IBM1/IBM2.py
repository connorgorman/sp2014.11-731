
# coding: utf-8

import os, sys
import numpy as np
import pdb
import shutil
import ast

import collections

import IBM1


t_e_f, e_set, f_set = IBM1.IBM1_model()

print "Got Values from IBM1"

a = {}

for k in range(0, len(e_set)):
    e_sentence = e_set[k]
    f_sentence = f_set[k]

    lf = len(f_sentence)
    le = len(e_sentence)

    for i in range(0, lf):
        for j in range(0, le):
            a_tuple = (i, j, le, lf)
            a[a_tuple] = float(1.0 / (lf + 1))

# e_set = [ ["the", "house"], ["the","book"], ["a", "book"],["a", "house"] ]
# f_set = [ ["das", "haus" ], ["das", "buch"], ["ein", "buch"], ["ein", "haus"] ]
            
sent_limit = len(e_set)

iterations = 5

for iteration in range(0, iterations):
    print "IBM MODEL 2 ITERATION ", iteration

    count = collections.defaultdict(float)
    count_a = collections.defaultdict(float)

    total_f = collections.defaultdict(float)
    total_a = collections.defaultdict(float)

    s_total = collections.defaultdict(float)

    for sent_idx in range(0, sent_limit):
        
        e_sent = e_set[sent_idx]
        f_sent = f_set[sent_idx]
        le = len(e_sent)
        lf = len(f_sent)
        
        for j, e_word in enumerate(e_sent):

            s_total[e_word] = float(0.0)

            for i, f_word in enumerate(f_sent):
                key = (e_word, f_word)

                s_total[e_word] += t_e_f[key] * a[(i, j, le, lf)]


        for j, e_word in enumerate(e_sent):
            for i, f_word in enumerate(f_sent):
                word_tuple = (e_word, f_word)

                c = t_e_f[word_tuple] * a[(i, j, le, lf)] / s_total[e_word]

                count[word_tuple] += float(c)
                total_f[f_word] += float(c)
                count_a[(i, j, le, lf)] += float(c)
                total_a[ (j, le, lf) ] += float(c)
    
    for (e_word, f_word) in count.keys():
        t_e_f[(e_word, f_word)] = count[(e_word, f_word)] / total_f[f_word]

    for (i, j, le, lf) in a.keys():
        a[(i, j, le, lf)] = count_a[(i, j, le, lf)] / total_a[(j, le, lf)]

# Calculate Alignments
 
print "Writing alignments"

f = open("ibm2.out", "w")

for k, f_sent in enumerate(f_set):
    e_sent = e_set[k]

    le = len(e_sent)
    lf = len(f_sent)

    for j, e_word in enumerate(e_sent):

        best_f_e = (-1, -1)
        best_prob = 0.0

        for i, f_word in enumerate(f_sent):

            t_key = (e_word, f_word)
            a_key = (i, j, le, lf)

            if t_e_f[t_key] * a[a_key] > best_prob:
                best_prob = t_e_f[t_key] * a[a_key] 
                best_f_e = (i, j)

        f.write( str(best_f_e[0]) + "-" + str(best_f_e[1]))
        if j != len(e_sent) - 1:
            f.write(" ")
    f.write("\n")

f.close()

shutil.copy("ibm1.out", "../hw1/ibm1.out")
shutil.copy("ibm2.out", "../hw1/ibm2.out")