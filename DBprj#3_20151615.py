#-*- coding: utf-8 -*-

import datetime
import time
import sys
import MeCab
import operator
from pymongo import MongoClient
from bson import ObjectId
from itertools import combinations

# DB info
DBname = "db******"
conn = MongoClient('******.sogang.ac.kr')
db = conn[DBname]
db.authenticate(DBname, DBname)

# Variables
stop_word = {}

def make_stop_word():
    """Make stop_word"""
    while True:
        line = f.readline()
        if not line:
            break
        stop_word[line.strip('\n')] = line.strip('\n')
    f.close()

def printMenu() :
    """Print menu script"""
    print "0. CopyData"
    print "1. Morph"
    print "2. print morphs"
    print "3. print wordset"
    print "4. frequent item set"
    print "5. association rule"

def morphing(content):
    """Make list of encoded non-stop_words"""
    t = MeCab.Tagger('-d/usr/local/lib/mecab/dic/mecab-ko-dic')
    nodes = t.parseToNode(content.encode('utf-8'))
    MorpList = []
    while nodes:
        if nodes.feature[0] == 'N' and nodes.feature[1] == 'N':
            word = nodes.surface
            if not word in stop_word:
                try:
                    word = word.encode('utf-8')
                    MorpList.append(word)
                except:
                    pass
        nodes = nodes.next
    return MorpList

def p0() :
    """CopyData news to news_freq"""
    col1 = db['news']
    col2 = db['news_freq']

    col2.drop()

    for doc in col1.find():
        contentDic = {}
        for key in doc.keys():
            if key != "_id":
                contentDic[key] = doc[key]
        col2.insert(contentDic)

def p1():
    """Morph news and update news db"""
    for doc in db['news_freq'].find():
        doc['morph'] = morphing(doc['content'])
        db['news_freq'].update({"_id":doc['_id']}, doc)

def p2(url):
    """Print news morph which match url"""
    col = db['news_freq']
    for doc in col.find():
        if doc['url'] == url:
            for word in doc['morph']:
                print(word.encode('utf-8'))
            break

def p3():
    """Copy news morph to new db named news_wordset"""
    col_freq = db['news_freq']
    col_word = db['news_wordset']
    col_word.drop()
    for doc in col_freq.find():
        new_doc = {}
        new_set = set()
        for word in doc['morph']:
            new_set.add(word.encode('utf-8'))
        new_doc['word_set'] = list(new_set)
        new_doc['url'] = doc['url']
        col_word.insert(new_doc)

def p4(url):
    """Print news wordset which match url"""
    col = db['news_wordset']
    for doc in col.find():
        if doc['url'] == url:
            for word in doc['word_set']:
                print(word.encode('utf-8'))
            break

def p5(length):
    """
    Make frequent item set of given length
    Insert new dbs (dbname = candidate_L+"length")
    ex) db['candidate_L3']
    Duplicated Code, Long Method - Nedd Refactoring!!
    """
    col_freq = db['news_freq']
    col_word = db['news_wordset']
    min_sup = db.news.count() * 0.1

    temp_list = ()
    temp_dic = {}
    temp_set = set()

    col_cand1 = db['candidate_L1']
    col_cand1.drop()
    c1 = list()
    l1 = list()
    
    # Make c1
    for doc in col_word.find():
        for word in doc['word_set']:
            word = word.encode('utf-8')
            temp_set.add(word)
            if w in temp_dic:
                temp_dic[word] += 1
            else:
                temp_dic[word] = int(1)
    c1 = list(temp_set)

    # Make l1, candidate_L1
    for word in c1:
        if temp_dic[word] >= min_sup:
            temp_doc = {}
            temp_doc['item_set'] = word
            temp_doc['support'] = temp_dic[word]
            col_cand1.insert(temp_doc)
            l1.append(word)

    if length == 1:
        return

    col_cand2 = db['candidate_L2']
    col_cand2.drop()

    c2 = list()
    l2 = list()

    # Make c2
    for i in range(0, len(l1)-1):
        for j in range(i+1, len(l1)):
            temp_list = list()
            temp_list.append(l1[i])
            temp_list.append(l1[j])
            c2.append(temp_list)

    for word_duo in c2:
        count = 0
        for doc in col_word.find():
            if word_duo[0].decode('utf-8') in doc['word_set'] 
                    and word_duo[1].decode('utf-8') in doc['word_set']:
                count += 1
        # Make l2, candidate_L2
        if count >= min_sup:
            l2.append(word_duo)
            temp_doc = {}
            temp_doc['item_set'] = word_duo
            temp_doc['support'] = count
            col_cand2.insert(temp_doc)

    if length == 2:
        return

    col_cand3 = db['candidate_L3']
    col_cand3.drop()

    c3 = list()
    l3 = list()

    # Make c3
    for i in range(0, len(l2) - 1):
        for j in range(i+1, len(l2)):
            if l2[i][1] == l2[j][0]:
                # if two words continuous
                temp_list = list()
                temp_list.append(l2[i][0])
                temp_list.append(l2[j][1])
                if temp_list in l2:
                    temp_list.append(l2[i][1])
                    c3.append(temp_list)

    for word_trio in c3:
        count = 0
        for doc in col_word.find():
            if word_trio[0].decode('utf-8') in doc['word_set']
                    and word_trio[1].decode('utf-8') in doc['word_set']
                    and word_trio[2].decode('utf-8') in doc['word_set']:
                count += 1
        # Make l3, candidate_L3
        if count >= min_sup:
            l3.append(word_trio)
            temp_doc = {}
            temp_doc['item_set'] = word_trio
            temp_doc['support'] = count
            col_cand3.insert(temp_doc)

def p6(length):
    """
    Make strong association rule
    Print all of strong them
    Duplicated Code, Long Method - Nedd Refactoring!!
    """
    col_cand1 = db['candidate_L1']
    col_cand2 = db['candidate_L2']
    col_cand3 = db['candidate_L3']
    min_conf = 0.5

    if length == 2 :
        for doc in col_cand2.find():
            word_duo = doc['item_set']
            support = doc['support']
            for doc2 in col_cand1.find():
                conf = float(support)/doc2['support']
                if conf < min_conf:
                    continue
                if word_duo[0] == doc2['item_set']:
                    print('%s\t=>%s\t%f' % (
                        word_duo[0].decode('utf-8'), word_duo[1].decode('utf-8'),
                        float(support)/doc2['support']))
                if word_duo[1] == doc2['item_set']:
                    print('%s\t=>%s\t%f' % (
                        word_duo[1].decode('utf-8'), word_duo[0].decode('utf-8'),
                        float(support)/doc2['support']))
    elif length == 3 :
        for doc in col_cand3.find():
            word_trio = doc['item_set']
            support = doc['support']
            for doc2 in col_cand2.find():
                conf = float(support)/doc2['support']
                if conf < min_conf:
                    continue
                if word_trio[0] in doc2['item_set'] and word_trio[1] in doc2['item_set']:
                    print('%s, %s\t=>%s\t%f' % (
                        word_trio[0].decode('utf-8'), word_trio[1].decode('utf-8'),
                        word_trio[2].decode('utf-8'), float(support)/doc2['support']))
                if word_trio[1] in doc2['item_set'] and word_trio[2] in doc2['item_set']:
                    print('%s, %s\t=>%s\t%f' % (
                        word_trio[1].decode('utf-8'), word_trio[2].decode('utf-8'),
                        word_trio[0].decode('utf-8'), float(support)/doc2['support']))
                if word_trio[2] in doc2['item_set'] and word_trio[0] in doc2['item_set']:
                    print('%s, %s\t=>%s\t%f' % (
                        word_trio[2].decode('utf-8'), word_trio[0].decode('utf-8'),
                        word_trio[1].decode('utf-8'), float(support)/doc2['support']))
            for doc2 in col_cand1.find():
                conf = float(support)/doc2['support']
                if conf < min_conf:
                    continue
                if word_trio[0] == doc2['item_set']:
                    print('%s\t=>%s, %s\t%f' % (
                        word_trio[0].decode('utf-8'), word_trio[1].decode('utf-8'),
                        word_trio[2].decode('utf-8'), float(support)/doc2['support']))
                if word_trio[1] == doc2['item_set']:
                    print('%s\t=>%s, %s\t%f' % (
                        word_trio[1].decode('utf-8'), word_trio[2].decode('utf-8'),
                        word_trio[0].decode('utf-8'), float(support)/doc2['support']))
                if word_trio[2] == doc2['item_set']:
                    print('%s\t=>%s, %s\t%f' % (
                        word_trio[2].decode('utf-8'), word_trio[0].decode('utf-8'),
                        word_trio[1].decode('utf-8'), float(support)/doc2['support']))
    else:
        print('Invalid length')

# Main
if __name__ == "__main__" :
    make_stop_word()
    printMenu()
    selector = input()
    if selector == 0:
        p0()
    elif selector == 1:
        p1()
        p3()
    elif selector == 2:
        url = str(raw_input("input news url:"))
        p2(url)
    elif selector == 3:
        url = str(raw_input("input news url:"))
        p4(url)
    elif selector == 4:
        length = int(raw_input("input length of the frequent item:"))
        p5(length)
    elif selector == 5:
        length = int(raw_input("input length of the frequent item:"))
        p6(length)
