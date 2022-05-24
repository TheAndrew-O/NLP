from collections import defaultdict
import pandas as pd
from typing import Counter
import nltk
import re
from nltk.metrics.distance import edit_distance
from nltk.metrics.distance import jaccard_distance
import sys

def authorlist(file):
    with open(file) as fp:
        lines = [line.rstrip('\n') for line in fp]
    return lines

def AddOne():
    pass

def main():
    authors = authorlist(sys.argv[1])
    file = sys.argv[2]
    test_lines = []
    fp = open(file,'r')
    lines = fp.readlines()
    l = []
    vocab = set([])
    vocabs = []
    test_unigram_model = []
    test_bigram_models = []
    test_trigram_models = []
    #Get dev set from testfile
    print("This will take a while...")
    for line in lines:
        regex = re.sub(r'([^\w\s]|_)','',line.strip())
        words = regex.lower()
        temp = nltk.word_tokenize(words)
        for word in temp:
            test_unigram_model.append(word)
        test_lines.append(temp)
        test_bigram_models.extend(list(nltk.ngrams(temp, 2, pad_left=True, pad_right = True)))
        test_trigram_models.extend(list(nltk.ngrams(temp, 3, pad_left=True, pad_right = True)))
    print(test_bigram_models)
    training_unigram_model = []
    training_bigram_model = []
    training_trigram_model = []
    freq = nltk.FreqDist(test_bigram_models)
    df = pd.DataFrame.from_dict(freq, orient='index')
    df.columns = ['Frequency']
    df.index.name = 'Word'
    cake = nltk.MLEProbDist.f
    print(df)
    # for author in authors:
    #     with open(author) as fp:
    #         for line in fp:
    #             #temp = []
    #             for word in line.split():
    #                 regex = re.sub(r'([^\w\s]|_)','',line.strip())
    #                 words = regex.lower()
    #                 temp = nltk.word_tokenize(words)
    #                 for word in words:
    #                     training_unigram_model.append(word)
    #                 training_bigram_model.extend(list(nltk.ngrams(temp, 2, pad_left=True, pad_right = True)))
    #                 training_trigram_model.extend(list(nltk.ngrams(temp, 3, pad_left=True, pad_right = True)))
    
    # bi_freq = nltk.FreqDist(training_bigram_model)
    # tri_freq = nltk.FreqDist(training_trigram_model)

    # language_model = defaultdict(Counter)
    # for i,j,k in tri_freq:
    #     if(i != None and j != None and k != None):
    #         language_model[i,j] += tri_freq[i,j,k]
    
    # for line in lines:
    #     regex = re.sub(r'([^\w\s]|_)','',line.strip())
    #     words = regex.lower()
    #     temp = nltk.word_tokenize(words)
    #     string = " ".join(temp)
        

main()
