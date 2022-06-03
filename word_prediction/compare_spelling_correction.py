"""
Jaccard Score: 197
Total: 262
Levenshtein Score: 199
Total: 262
"""
import time
import pandas as pd
import nltk
import re
from nltk.metrics.distance import edit_distance
from nltk.metrics.distance import jaccard_distance
import sys


correct_spelling = nltk.corpus.words.words()

def remove_repeats(word):
    pattern = re.compile(r'(.)\1{2,}')
    return pattern.sub(r'\1\1',word)

def jaccardDistance(lines, n_grams):
    corrected = []
    for line in lines:
        for word in line:
            if(len(word) == 1):
                temp = [(jaccard_distance(set(nltk.ngrams(word, 1)), set(nltk.ngrams(str_, 1))),str_) for str_ in correct_spelling if str_[0]==word[0]]
                lst = sorted(temp, key= lambda val:val[0])
                corrected.append(lst[0][1])
            else:
                temp = [(jaccard_distance(set(nltk.ngrams(word, n_grams)), set(nltk.ngrams(str_, n_grams))),str_) for str_ in correct_spelling if str_[0]==word[0]]
                lst = sorted(temp, key= lambda val:val[0])
                corrected.append(lst[0][1])
    return corrected

def levenshteinDistance(lines):
    corrected = []
    for line in lines:
        for word in line:
            temp = [(edit_distance(word, str_),str_) for str_ in correct_spelling if str_[0]==word[0]]
            suggestions = sorted(temp, key=lambda val:val[0])
            corrected.append(suggestions[0][1])
    return corrected

def main():
    answers_file = sys.argv[1]
    mistakes_file = sys.argv[2]
    correctly_spelled = []
    spelling_mistakes = []
    j_score = 0
    l_score = 0
    with open(answers_file) as fp:
        for line in fp:
            regex = re.sub(r'([^\w\s]|_)','',line.strip())
            words = regex.lower()
            temp = nltk.word_tokenize(words)
            correctly_spelled.extend(temp)
    with open(mistakes_file) as fp:
        for line in fp:
            regex = re.sub(r'([^\w\s]|_)','',line.strip())
            words = regex.lower()
            temp = nltk.word_tokenize(words)
            repeats = []
            for word in temp:
                t = remove_repeats(word)
                repeats.append(t)
            spelling_mistakes.append(temp)
    j_start = time.time()
    j_fixed = jaccardDistance(spelling_mistakes,2)
    j_exec = (time.time() - j_start)
    for i in range(len(j_fixed)):
        if(j_fixed[i] == correctly_spelled[i]):
            j_score += 1
    print("Jaccard Score: " + str(j_score))
    print("Total: " + str(len(j_fixed)))
    print("Execution Time in Seconds: " + str(j_exec))

    l_start = time.time()
    l_fixed = levenshteinDistance(spelling_mistakes)
    l_exec = (time.time() - l_start)
    for i in range(len(l_fixed)):
        if(l_fixed[i] == correctly_spelled[i]):
            l_score += 1
    print("Levenshtein Score: " + str(l_score))
    print("Total: " + str(len(l_fixed)))
    print("Execution Time in Seconds: " + str(l_exec))

if __name__ == '__main__':
    main()
