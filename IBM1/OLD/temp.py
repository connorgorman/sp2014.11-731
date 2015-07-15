
# coding: utf-8

import os, sys
import numpy as np
import pdb
import shutil

f = open("ibm1_table.txt", "r")

line = f.readline()

t_e_f = eval(line)






content = [x.strip('\n') for x in open("dev-test-train.de-en").readlines()]

e_set = []
f_set = []

count_a = {} # i | j, le, lf
total_a = {} # j, le, lf
a_i_j_le_lf = {}

count = 0
for k in range(0, len(content)):

    line = content[k]
    split = line.split("|||")
    
    f_split = [x for x in split[0].split(" ") if x != '' and x != "" ]
    e_split = [x for x in split[1].split(" ") if x != '' and x != "" ]

    lf = len(f_split)
    le = len(e_split)

    for i in range(0, lf):
        for j in range(0, le):
            a_tuple = (i, j, le, lf)

            a_i_j_le_lf[a_tuple] = 1.0 / (lf + 1)            


    for j in range(0, e_sent_len):
        total_tuple = (j, e_sent_len, f_sent_len)
        total_a[total_tuple] = 0.0
        for i in range(0, f_sent_len):
            count_tuple = (i, j, e_sent_len, f_sent_len)
            count_a[count_tuple] = 0.0

            a_i_j_le_lf[count_tuple] = 1.0 / f_sent_len
            # print count_tuple

    f_set.append( f_split )
    e_set.append( e_split )

    # if k > 10:
        # break

# e_set = [ ["the", "house"], ["the","book"], ["a", "book"],["a", "house"] ]
# f_set = [ ["das", "haus" ], ["das", "buch"], ["ein", "buch"], ["ein", "haus"] ]

print "Num Removed", count

e_vocab = []
f_vocab = []

t_e_f = {}

for f_idx, f_sent in enumerate(f_set):
    e_sent = e_set[f_idx]

    for f_word in f_sent:
        for e_word in e_sent:
            index_tuple = (e_word, f_word)
            t_e_f[index_tuple] = 1.0
            
print len(t_e_f)

for key, value in t_e_f.iteritems() :
    t_e_f[key] = t_e_f[key] / len(t_e_f)

sent_limit = len(e_set)

print "Starting Iterations"
    
iterations = 2
for iteration in range(0, iterations):
    
    print "IBM Model 1 Iteration: ", iteration

    count = {}
    total_f = {}

    for key, value in t_e_f.iteritems():
        count[key] = 0.0
        total_f[key[1]] = 0.0

    for sent_idx in range(0, sent_limit):

        # div_iter = sent_limit / 10

        # if sent_idx % div_iter == 0:
        #     print sent_idx
        e_sent = e_set[sent_idx]
        f_sent = f_set[sent_idx]
        
        s_total = np.zeros( len(e_sent) )
        
        for e_idx, e_word in enumerate(e_sent):
            for f_idx, f_word in enumerate(f_sent):
                s_total[e_idx] += t_e_f[(e_word, f_word)]
        
        for e_idx, e_word in enumerate(e_sent):
            for f_idx, f_word in enumerate(f_sent):
                index_tuple = (e_word, f_word)
                
                count[index_tuple] += t_e_f[index_tuple] / s_total[e_idx]
                total_f[f_word] += t_e_f[index_tuple] / s_total[e_idx]
    

    for key, value in t_e_f.iteritems():
            t_e_f[key] = count[key] / total_f[key[1]]
        
    printPData(t_e_f, e_set, f_set)


# Calculate Alignments
 
f = open("ibm1.out", "w")

for f_idx, f_sent in enumerate(f_set):
    e_sent = e_set[f_idx]

    for e_idx, e_word in enumerate(e_sent):
        best_f_e = (-1, -1)
        best_prob = 0.0
        for f_idx, f_word in enumerate(f_sent):
            if t_e_f[(e_word, f_word)] > best_prob:
                best_prob = t_e_f[(e_word, f_word)]
                best_f_e = (f_idx, e_idx)

        f.write( str(best_f_e[0]) + "-" + str(best_f_e[1]))
        if e_idx != len(e_sent) - 1:
            f.write(" ")

    f.write("\n")



iterations = 5

for iteration in range(0, iterations):
    print "IBM MODEL 2 ITERATION ", iteration

    count = {}
    total_f = {}

    for key, value in t_e_f.iteritems():
        count[key] = 0.0
        total_f[key[1]] = 0.0

    for key, value in count_a.iteritems():
        count_a[key] = 0.0

    for key, value in total_a.iteritems():
        total_a[key] = 0.0


    for sent_idx in range(0, sent_limit):

        # div_iter = sent_limit / 10
        # if sent_idx % div_iter == 0:
        #     print sent_idx
        
        e_sent = e_set[sent_idx]
        f_sent = f_set[sent_idx]
        le = len(e_sent)
        lf = len(f_sent)
        
        # if(lf == 9 and le == 6):
        #     pdb.set_trace()

        s_total = np.zeros( le )
        
        for e_idx, e_word in enumerate(e_sent):
            for f_idx, f_word in enumerate(f_sent):
                s_total[e_idx] += t_e_f[(e_word, f_word)] * a_i_j_le_lf[(f_idx, e_idx, le, lf)]
        
        # print "GOT HERE"

        for e_idx, e_word in enumerate(e_sent):
            for f_idx, f_word in enumerate(f_sent):
                word_tuple = (e_word, f_word)

                c = t_e_f[word_tuple] * a_i_j_le_lf[(f_idx, e_idx, le, lf)] / s_total[e_idx]

                count[word_tuple] += c
                total_f[f_word] += c
                count_a[(f_idx, e_idx, le, lf)] += c
                total_a[ (e_idx, le, lf) ] += c
    
    for key, value in t_e_f.iteritems():
        t_e_f[key] = count[key] / total_f[key[1]]

    for key, value in a_i_j_le_lf.iteritems():
        a_i_j_le_lf[key] = count_a[key] / total_a[(key[1], key[2], key[3])]


# Calculate Alignments
 
print "finished"

f = open("ibm2.out", "w")

for f_idx, f_sent in enumerate(f_set):
    e_sent = e_set[f_idx]

    e_len = len(e_sent)
    f_len = len(f_sent)

    for e_idx, e_word in enumerate(e_sent):
        best_f_e = (-1, -1)
        # best_a = (-1, -1, -1, -1)
        best_prob = 0.0
        for f_idx, f_word in enumerate(f_sent):
            word_index = (e_word, f_word)

            for j in range(0, e_len):
                align_index = (f_idx, j, e_len, f_len)

            if t_e_f[word_index] * a_i_j_le_lf[align_index] > best_prob:
                best_prob = t_e_f[(e_word, f_word)] * a_i_j_le_lf[align_index]
                best_f_e = (f_idx, e_idx)
                # best_a = align_index

        f.write( str(best_f_e[0]) + "-" + str(best_f_e[1]))
        if e_idx != len(e_sent) - 1:
            f.write(" ")
    f.write("\n")

f.close()

shutil.copy("ibm1.out", "../hw1/ibm1.out")
shutil.copy("ibm2.out", "../hw1/ibm2.out")