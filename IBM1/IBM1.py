
# coding: utf-8

import os, sys
import numpy as np
import pdb
import collections

def printMap(t_map):
    
    for key, value in t_map.iteritems() :
        print key[0], " ", key[1], "  -   ", value

def printPData(t_e_f, e_set, f_set):
    
    total_sum = 0.0
    for f_idx, f_sent in enumerate(f_set):
        e_sent = e_set[f_idx]

        prod = 1.0
        for e_word in e_sent:
            sum_val = 0.0
           
            for f_word in f_sent:
                sum_val += t_e_f[(e_word, f_word)]

            prod *= sum_val
    
        total_sum += np.log(prod)

    print "P(Data): ", total_sum

def IBM1_model():

    content = [x.strip('\n') for x in open("dev-test-train.de-en").readlines()]

    e_set = []
    f_set = []

    count = 0
    for i in range(0, len(content)):

        line = content[i]
        split = line.split("|||")
        
        f_split = [x for x in split[0].split(" ") if x != '' and x != "" ]
        e_split = [x for x in split[1].split(" ") if x != '' and x != "" ]

        # if len(f_split) > 5 or len(e_split) > 5:
        #     count += 1
        #     continue

        f_set.append( f_split )
        e_set.append( e_split )

    # e_set = [ ["the", "house"], ["the","book"], ["a", "book"],["a", "house"] ]
    # f_set = [ ["das", "haus" ], ["das", "buch"], ["ein", "buch"], ["ein", "haus"] ]

    print "Num Removed", count

    t_e_f = {}

    for f_idx, f_sent in enumerate(f_set):
        e_sent = e_set[f_idx]

        for f_word in f_sent:
            # f_vocab.append(f_word)
            for e_word in e_sent:
                index_tuple = (e_word, f_word)
                t_e_f[index_tuple] = 1.0

    print len(t_e_f)

    for key, value in t_e_f.iteritems() :
        t_e_f[key] = t_e_f[key] / len(t_e_f)

    # printPData(t_e_f, e_set, f_set)

    # sent_limit = len(e_set)
    sent_limit = len(e_set)

    print "Starting Iterations"
        
    iterations = 4
    for iteration in range(0, iterations):
        
        print "Iteration: ", iteration

        count = collections.defaultdict(float)
        total_f = collections.defaultdict(float)
                    
        for sent_idx in range(0, sent_limit):

            div_iter = sent_limit / 10
            # if sent_idx % div_iter == 0:
            #     print sent_idx
            
            e_sent = e_set[sent_idx]
            f_sent = f_set[sent_idx]
            
            s_total = collections.defaultdict(float)
            
            for j, e_word in enumerate(e_sent):
                for i, f_word in enumerate(f_sent):
                    s_total[e_word] += t_e_f[(e_word, f_word)]
            
            for j, e_word in enumerate(e_sent):
                for i, f_word in enumerate(f_sent):
                    index_tuple = (e_word, f_word)
                    
                    count[index_tuple] += t_e_f[index_tuple] / s_total[e_word]
                    total_f[f_word] += t_e_f[index_tuple] / s_total[e_word]
        
        for (e_word, f_word) in t_e_f.keys():
                t_e_f[(e_word, f_word)] = count[(e_word, f_word)] / total_f[f_word]

        # printPData(t_e_f, e_set, f_set)

    # Calculate Alignments
     
    f = open("ibm1.out", "w")

    for k, f_sent in enumerate(f_set):
        e_sent = e_set[k]

        for j, e_word in enumerate(e_sent):
            best_f_e = (-1, -1)
            best_prob = 0.0
            
            for i, f_word in enumerate(f_sent):
                if t_e_f[(e_word, f_word)] > best_prob:
                    best_prob = t_e_f[(e_word, f_word)]
                    best_f_e = (i, j)

            f.write( str(best_f_e[0]) + "-" + str(best_f_e[1]))
            if j != len(e_sent) - 1:
                f.write(" ")
        f.write("\n")

    f.close()

    # f = open("ibm1_table.txt", "w")

    # f.write(str(t_e_f))


    return t_e_f, e_set, f_set


# IBM1_model()