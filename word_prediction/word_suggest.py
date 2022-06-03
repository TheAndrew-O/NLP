"""
@encoding: UTF_8
@smoothing: add-one smoothing is used (laplace smoothing).
@commands:
        python3 readl.py authorlist.txt
                        or
        python3 readl.py authorlist.txt -test <file>.txt

"""
import re
import sys
import nltk


"""
Get list of files from authorlist
"""
def authorlist(file):
    with open(file) as fp:
        lines = [line.rstrip('\n') for line in fp]
    return lines

#Calc the probability of the next word given the previous word, apply add-one smoothing
def calc_prob(prev_word, word, vocab_len, n_grams, smoothed_n_grams):
    prev_word = tuple(prev_word)
    #Get frequency of word
    prev_word_count = n_grams.get(prev_word, 0)
    #Laplace smoothing with constant 1
    denominator = prev_word_count + (1.0 * vocab_len)
    #combine tuples
    laplace = prev_word + (word,)
    #If the word doesn't appear in training data (vocab) set the count to 0 and add 1
    laplace_count = smoothed_n_grams.get(laplace, 0) + 1.0
    prob = laplace_count / denominator

    return float(prob)

def calc_all_probs(prev_word, vocab, n_grams, smoothed_n_grams):
    prev_word = tuple(prev_word)
    #Add unknown word token to vocab
    vocab.update(["<unk>"])
    vocab_len = len(vocab)
    probs = dict([])
    #Calc the probability of the next word given the previous word
    for word in vocab:
        prob_word = calc_prob(prev_word, word, vocab_len, n_grams, smoothed_n_grams)
        probs[word] = prob_word
    #Sort the probability in descending order
    probs = sorted(probs.items(), key=lambda x: x[1], reverse=True)
    return probs
#num_words is type of model
def create_ngram_model(words, num_words):
    n_grams = dict([])
    for word in words:
        #Generate random bigram that starts with <s> until </s>
        word = (["<s>"] * num_words) + word + ["</s>"]
        word = tuple(word)
        length = len(word) - (num_words - 1)
        #Count freqeuncy of words
        for i in range(0, length):
            n_gram = word[i: i + num_words]
            if n_gram in n_grams: 
                n_grams[n_gram] += 1
            else:
                n_grams[n_gram] = 1

    return n_grams


def test_flag(authors,file):
    test_lines = []
    fp = open(file,'r')
    lines = fp.readlines()
    l = []
    vocab = set([])
    vocabs = []
    bigram_models = []
    unigram_models = []
    trigram_models = []
    #Get dev set from testfile
    for line in lines:
        regex = re.sub(r'([^\w\s]|_)','',line.strip())
        words = regex.lower()
        temp = nltk.word_tokenize(words)
        test_lines.append(temp)
 
    #Read authorlist
    for author in authors:
        with open(author) as f:
            for line in f:
                temp = []
                #Get training data
                for word in line.split():
                    regex = re.sub(r'([^\w\s]|_)','',word)
                    word = regex.lower()
                    temp.append(word)
                    vocab.add(word)
                vocabs.append(vocab)
                l.append(temp)
            bigrams = create_ngram_model(l,2)
            uni = create_ngram_model(l,1)
            trigrams = create_ngram_model(l,3)
            trigram_models.append(trigrams)
            bigram_models.append(bigrams)
            unigram_models.append(uni)
            l = []
            vocab = set([])
    
    line_count = 0
    length = len(bigram_models)
    total = 0
    correct = 0
    tri_correct = 0
    for test_line in test_lines:
        devlength = len(test_line)
        
        print("Classifying Line: " + str(line_count))
        line_count += 1
        #iterate over authors
        for i in range(0,length):
            #iterate test sentence
            for j in range(0,devlength - 1):
             
                curr_word = test_line[j]
                next_word = test_line[j+1]
                last_bigram = test_line[-2:]
                is_word = re.match(r'[A-Za-z]',curr_word)
                is_word2 = re.match(r'[A-Za-z]',next_word)
                if(not is_word):
                    continue
                elif(not is_word2):
                    continue
                #Guess next word
                estimation = calc_all_probs(curr_word, vocabs[i], unigram_models[i], bigram_models[i])
                tri_estimation = calc_all_probs(last_bigram,vocab[i],bigram_models[i],trigram_models[i])
                tri_next = tri_estimation[0][0]
                approx_nextWord = estimation[0][0]
                if(approx_nextWord == ""):
                    approx_nextWord = estimation[1][0]
                if(tri_next == ""):
                    tri_next = tri_estimation[1][0]
                    
                if approx_nextWord == next_word:
                    correct += 1
                if tri_next == next_word:
                    tri_correct += 1
                total += 1
            print(authors[i] + "-language bigram model: " + str(correct) + "/" + str(total) + " correct")
            print(authors[i] + "-language trigram model: " + str(tri_correct) + "/" + str(total) + " correct")
            total = 0
            correct = 0
            tri_correct = 0
  

def main():
    l = []
    dev = []
    input = sys.argv[1]

    vocab = set([])
    random_sample = 0
    authors = authorlist(input)
    print("This will take a while...")
    #Test flag option
    if(len(sys.argv) == 4):
        test_flag(authors,sys.argv[3])
        return
    correct = 0
    total = 0
    tri_correct = 0
    for author in authors:
        with open(author) as f:
            for line in f:
                temp = []
                #Get dev set on every 13th line
                if(random_sample == 13):
                    tokens = re.sub(r'([^\w\s]|_)','',line)
                    tokens = re.sub(r'([“”’\\?!.()\";/\\|`])','',tokens)
                    tokens = nltk.word_tokenize(line)
                    toks = [tok.lower() for tok in tokens]
                    for k in toks:
                        dev.append(k)
                    random_sample = 0
                    continue

                random_sample += 1
                #Get training data
                for word in line.split():
                    regex = re.sub(r'([^\w\s]|_)','',word)
                    word = regex.lower()
                    temp.append(word)
                    vocab.add(word)
                l.append(temp)
    
            #Create bigram and unigram models
            trigrams = create_ngram_model(l,3)
            bigrams = create_ngram_model(l,2)
            uni = create_ngram_model(l,1)
           
            devlength = len(dev)
            
            for i in range(0,devlength - 1):
                curr_word = dev[i]
                next_word = dev[i+1]
                last_bigram = dev[-2:]
                #Check if word is just [punctuation or some number]
                is_word = re.match(r'[A-Za-z]',curr_word)
                is_word2 = re.match(r'[A-Za-z]',next_word)
                #Forgive me....
                if(not is_word):
                    continue
                elif(not is_word2):
                    continue
                
                estimation = calc_all_probs(curr_word,vocab,uni,bigrams)
                tri_estimation = calc_all_probs(last_bigram,vocab,bigrams,trigrams)
                approx_nextWord = estimation[0][0]
                tri_next = tri_estimation[0][0]
                if(approx_nextWord == ""):
                    approx_nextWord = estimation[1][0]
                if(tri_next == ""):
                    tri_next = tri_estimation[1][0]
                    
                if approx_nextWord == next_word:
                    correct += 1
                if tri_next == next_word:
                    tri_correct += 1
                total += 1
            print(author + "-language bigram model: " + str(correct) + "/" + str(total) + " correct")
            print(author + "-language trigram model: " + str(tri_correct) + "/" + str(total) + " correct")
            
            correct = 0
            total = 0
            tri_correct = 0
            random_sample = 0
            l = []
            dev = []
            vocab = set([])
    

main()

