#encoding=utf-8
import re
import ssl
import nltk
from nltk.tokenize import WordPunctTokenizer
import nltk.stem
from nltk import SnowballStemmer
from nltk.corpus import brown
from nltk.corpus import conll2000
from rake_nltk import Rake
from textblob import TextBlob
from textblob import Word
from textblob.wordnet import VERB
from gensim.test.utils import common_texts, get_tmpfile
from gensim.models import word2vec
ssl._create_default_https_context = ssl._create_unverified_context
# nltk.download()
import collections
from nltk.corpus import wordnet as wn
# this class is used for chunk.
class UnigramChunker(nltk.ChunkParserI):
    """
        一元分块器，
        该分块器可以从训练句子集中找出每个词性标注最有可能的分块标记，
        然后使用这些信息进行分块
    """
    def __init__(self, train_sents):
        """
            构造函数
            :param train_sents: Tree对象列表
        """
        train_data = []
        for sent in train_sents:
            # 将Tree对象转换为IOB标记列表[(word, tag, IOB-tag), ...]
            conlltags = nltk.chunk.tree2conlltags(sent)

            # 找出每个词性标注对应的IOB标记
            ti_list = [(t, i) for w, t, i in conlltags]
            train_data.append(ti_list)

        # 使用一元标注器进行训练
        self.__tagger = nltk.UnigramTagger(train_data)

    def parse(self, tokens):
        """
            对句子进行分块
            :param tokens: 标注词性的单词列表
            :return: Tree对象
        """
        # 取出词性标注
        tags = [tag for (word, tag) in tokens]
        # 对词性标注进行分块标记
        ti_list = self.__tagger.tag(tags)
        # 取出IOB标记
        iob_tags = [iob_tag for (tag, iob_tag) in ti_list]
        # 组合成conll标记
        conlltags = [(word, pos, iob_tag) for ((word, pos), iob_tag) in zip(tokens, iob_tags)]

        return nltk.chunk.conlltags2tree(conlltags)
"""
test_sents = conll2000.chunked_sents("test.txt", chunk_types=["NP"])
train_sents = conll2000.chunked_sents("train.txt", chunk_types=["NP"])
unigram_chunker = UnigramChunker(train_sents)
print(unigram_chunker.evaluate(test_sents))
"""

# rake-nltk
# Uses stopwords for english from NLTK, and all puntuation characters by
# default
#r = Rake()

# Extraction given the text.
#r.extract_keywords_from_text("Python is a high-level, general-purpose programming language.")
#print(r.get_ranked_phrases())
#print(r.get_ranked_phrases_with_scores())
#print(r.get_word_degrees())
#print(r.get_word_frequency_distribution())

# Extraction given the list of strings where each string is a sentence.
#r.extract_keywords_from_sentences(["Uses stopwords for english from NLTK, and all puntuation characters by","Uses stopwords for english from NLTK, and all puntuation characters by"])

# text-blob http://textblob.readthedocs.io/en/dev/quickstart.html
# text-blob wordnet interface http://www.nltk.org/howto/wordnet.html
#w = Word("octopi")
#print(w.lemmatize())
#w = Word("went")
#print(w.lemmatize("v"))

# WordNet Integration
#'And now for something completely different'

def extract_keyword(text):
    r = Rake()
    keyword = r.extract_keywords_from_text(text)
    return keyword

def extract_word(text):
    words = nltk.word_tokenize(text)
    return words

def extract_noun(text):
    words = nltk.word_tokenize(text)
    word_tag = nltk.pos_tag(words)
    noun = []
    for word in word_tag:
        if word[1] == "NN" or word[1] == "NNP":
            noun.append(word[0])
    return noun


def extract_word_freq(text):
    words = nltk.word_tokenize(text)
    freq = nltk.FreqDist(words)
    return freq


def extract_adj(text):
    words = nltk.word_tokenize(text)
    word_tag = nltk.pos_tag(words)
    adj = []
    for word in word_tag:
        if word[1] == "JJ":
            adj.append(word[0])
    return adj

def extract_verb(text):
    words = nltk.word_tokenize(text)
    word_tag = nltk.pos_tag(words)
    verb = []
    for word in word_tag:
        if word[1] == "VB":
            verb.append(word[0])
    return verb


def extract_noun_phrase(text):
    nounphrase_tb = TextBlob(text)
    return nounphrase_tb.noun_phrases


def extract_ner(text):
    #tokens = nltk.word_tokenize('I am very excited about the next generation of Apple products.')
    #tokens = nltk.pos_tag(tokens)
    #tree = nltk.ne_chunk(tokens)
    #print(tree)
    words = nltk.word_tokenize(text)
    word_tag = nltk.pos_tag(words)
    ner = []
    for word in word_tag:
        if word[1] == "NNP":
            ner.append(word[0])
    return ner


def splitSentence(paragraph):
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    sentences = tokenizer.tokenize(paragraph)
    return sentences

def wordtokenizer(sentence):
    words = WordPunctTokenizer().tokenize(sentence)
    return words


def para2senc2words(text):
    sen = splitSentence(text)
    result = []
    for i in sen:
        words = wordtokenizer(i)
        result.append(words)
    return result


def extract_relation(text):
    sentences = splitSentence(text)
    relation = []
    for sentence in sentences:
        words = nltk.word_tokenize(sentence)
        word_tag = nltk.pos_tag(words)
        number = 0
        temp = []
        for word in word_tag:
            if word[1] == "NN" or word[1] == "NNP":
                number += 1
                if word[0] not in temp:
                    temp.append(word[0])
        if len(temp) >= 2:
            for i in range(0,len(temp)-1):
                for j in range(i+1, len(temp)):
                    relation.append((temp[i], temp[j], "co"))
    return relation


def word2vec_initialize(text):
    #sent = para2senc2words(text)
    #print(sent)
    #open('corpus.txt','w').write(text)
    #sentences = word2vec.Text8Corpus("corpus.txt")
    sentences = para2senc2words(text)
    model = word2vec.Word2Vec(sentences, size=100, window=5, min_count=1, workers=4)
    model.save("knowledgeB.model")
    return 0

#this function doesn't work now!!!! And I reaaly can't find out why.
def word2vec_trainmore(text):
    text = para2senc2words(text)
    model = word2vec.Word2Vec.load("knowledgeB.model")
    model.train(text, total_examples=1, epochs=1)
    return 0


def word2vec_result(word):
    new_model = word2vec.Word2Vec.load("knowledgeB.model")
    #print(new_model[word])
    return new_model[word]


#词干提取 fishing-fish shops-shop
def word_stem(word):
    s = nltk.stem.SnowballStemmer('english')
    if(s.stem(word)):
        return s.stem(word)
    else:
        return word


#词形还原 octopi-octopus
def word_lemmatized(word):
    w = Word(word)
    return w.lemmatize()


#返回一个词语所在的词语集合，一个词语会在多个词语集合中
def wordnet_synsets(word):
    if(wn.synsets(word)):
        return wn.synsets(word)
    else:
        return 1


#输入一个同义词集，返回词集中的所有词条
def wordnet_lemma_names(wordset):
    return wn.synset(wordset).lemma_names


def wordnet_similarity(word1,word2):
    worda = word_stem(word1)
    wordb = word_stem(word2)
    if(wordnet_synsets(worda)!= 1 and wordnet_synsets(wordb)!= 1):
        word1_synsets = wordnet_synsets(worda)
        word2_synsets = wordnet_synsets(wordb)
        word1_synset = word1_synsets[0]
        word2_synset = word2_synsets[0]
        return word1_synset.path_similarity(word2_synset)
    else:
        return 0
#if __name__ == '__main__':
    #print(para2senc2words('I am very excited about the next generation of Apple products. But I am csk! So I am not afraid of you. I am very excited about the next generation of Apple products. But I am csk! So I am not afraid of you.'))
    #word2vec_initialize("I am very excited about the next generation of Apple products. But I am csk! So I am not afraid of you.")
    #word2vec_trainmore("And now for something completely different.")
    #word2vec_trainmore("I hate Apple products.")
    #word2vec_result("I")
    #extract_word_freq("Hello world, I am csk")
    #model = word2vec.Word2Vec.load("knowledgeB.model")
    #print(model.similarity("I","Apple"))
    #print(word_stem('shops'))
    #print(word_stem('chicken'))

