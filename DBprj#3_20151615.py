#-*- coding: utf-8 -*-

import datetime
import time
import sys
import MeCab
import operator
from pymongo import MongoClient
from bson import ObjectId
from itertools import combinations

stop_word = {}
DBname = "db20151615"
conn = MongoClient('dbpurple.sogang.ac.kr')
db = conn[DBname]
db.authenticate(DBname, DBname)

def make_stop_word():
    f = open("wordList.txt", 'r')
    while True:
        line = f.readline()
        if not line:
            break
        stop_word[line.strip('\n')] = line.strip('\n')
    f.close()

def printMenu() :
    print "0. CopyData"
    print "1. Morph"
    print "2. print morphs"
    print "3. print wordset"
    print "4. frequent item set"
    print "5. association rule"

def morphing(content):
    t = MeCab.Tagger('-d/usr/local/lib/mecab/dic/mecab-ko-dic')
    nodes = t.parseToNode(content.encode('utf-8'))
    MorpList = []
    while nodes:
        if nodes.feature[0] == 'N' and nodes.feature[1] == 'N':
            w = nodes.surface
            if not w in stop_word:
                try:
                    w = w.encode('utf-8')
                    MorpList.append(w)
                except:
                    pass
        nodes = nodes.next
    return MorpList

def p0() :
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
    for doc in db['news_freq'].find():
        doc['morph'] = morphing(doc['content'])
        db['news_freq'].update({"_id":doc['_id']}, doc)

def p2(url):
    col = db['news_freq']
    for doc in col.find():
        if doc['url'] == url:
            for w in doc['morph']:
                print(w.encode('utf-8'))
            break
    """
       TODO :
       input : news url
       output : news morphs
    """

def p3():
    col1 = db['news_freq']
    col2 = db['news_wordset']
    col2.drop()
    for doc in col1.find():
        new_doc = {}
        new_set = set()
        for w in doc['morph']:
            new_set.add(w.encode('utf-8'))
        new_doc['word_set'] = list(new_set)
        new_doc['url'] = doc['url']
        col2.insert(new_doc)

def p4(url):
    col = db['news_wordset']
    for doc in col.find():
        if doc['url'] == url:
            for w in doc['word_set']:
                print(w.encode('utf-8'))
            break
    """
       TODO :
       input : news url
       output : news morphs
    """

def p5(length):
    col_freq = db['news_freq']
    col_word = db['news_wordset']

    min_sup = db.news.count() * 0.1

    col_cand1 = db['candidate_L1']
    col_cand1.drop()

    temp_dic = {}
    temp_set = set()
    temp_list = list()
    
    # C1
    for doc in col_word.find():
        for w in doc['word_set']:
            w = w.encode('utf-8')
            temp_set.add(w)
            if w in temp_dic:
                temp_dic[w] += 1
            else:
                temp_dic[w] = int(1)
    temp_list = list(temp_set)
    temp_list3 = list()

    # L1
    for w in temp_list:
        if temp_dic[w] >= min_sup:
            temp_doc = {}
            temp_doc['item_set'] = w
            temp_doc['support'] = temp_dic[w]
            col_cand1.insert(temp_doc)
            temp_list3.append(w)

    if length == 1:
        return

    col_cand2 = db['candidate_L2']
    col_cand2.drop()

    temp_list2 = list()
    # C2 - candidate
    for i in range(0, len(temp_list3)-1):
        for j in range(i+1, len(temp_list3)):
            sumin = list()
            sumin.append(temp_list3[i])
            sumin.append(temp_list3[j])
            temp_list2.append(sumin)

    temp_list = list()

    # C2
    for wduo in temp_list2:
        count = 0
        for doc in col_word.find():
            if wduo[0].decode('utf-8') in doc['word_set'] and wduo[1].decode('utf-8') in doc['word_set']:
                count += 1
        #L2
        if count >= min_sup:
            temp_list.append(wduo)
            temp_doc = {}
            temp_doc['item_set'] = wduo
            temp_doc['support'] = count
            col_cand2.insert(temp_doc)

    if length == 2:
        return

    col_cand3 = db['candidate_L3']
    col_cand3.drop()

    count = 0
    temp_list2 = list()

    # C3 - candidate
    for i in range(0, len(temp_list) - 1):
        for j in range(i+1, len(temp_list)):
            if temp_list[i][1] == temp_list[j][0]:
                search = list()
                search.append(temp_list[i][0])
                search.append(temp_list[j][1])
                if search in temp_list:
                    sumin = list(temp_list[i])
                    sumin.append(temp_list[j][1])
                    temp_list2.append(sumin)

    temp_list = list()
    # C3
    for wtrio in temp_list2:
        count = 0
        for doc in col_word.find():
            if wtrio[0].decode('utf-8') in doc['word_set'] and wtrio[1].decode('utf-8') in doc['word_set'] and wtrio[2].decode('utf-8') in doc['word_set']:
                count += 1
        #L3
        if count >= min_sup:
            temp_list.append(wtrio)
            temp_doc = {}
            temp_doc['item_set'] = wtrio
            temp_doc['support'] = count
            col_cand3.insert(temp_doc)
    """
        TODO:
        make frequent item_set
        and insert new dbs (dbname = candidate_L+"length")
        ex) l-th frequent item set dbname = candidate_Ll
    """

def p6(length):
    col_cand1 = db['candidate_L1']
    col_cand2 = db['candidate_L2']
    col_cand3 = db['candidate_L3']
    min_conf = 0.5

    if length == 2 :
        for doc in col_cand2.find():
            wduo = doc['item_set']
            support = doc['support']
            for doc2 in col_cand1.find():
                conf = float(support)/doc2['support']
                if conf < min_conf:
                    continue;
                if wduo[0] == doc2['item_set']:
                    print('%s\t=>%s\t%f' % (wduo[0].decode('utf-8'), wduo[1].decode('utf-8'), float(support)/doc2['support']))
                if wduo[1] == doc2['item_set']:
                    print('%s\t=>%s\t%f' % (wduo[1].decode('utf-8'), wduo[0].decode('utf-8'), float(support)/doc2['support']))
    elif length == 3 :
        for doc in col_cand3.find():
            wtrio = doc['item_set']
            support = doc['support']
            for doc2 in col_cand2.find():
                conf = float(support)/doc2['support']
                if conf < min_conf:
                    continue;
                if wtrio[0] in doc2['item_set'] and wtrio[1] in doc2['item_set']:
                    print('%s, %s\t=>%s\t%f' % (wtrio[0].decode('utf-8'), wtrio[1].decode('utf-8'), wtrio[2].decode('utf-8'), float(support)/doc2['support']))
                if wtrio[1] in doc2['item_set'] and wtrio[2] in doc2['item_set']:
                    print('%s, %s\t=>%s\t%f' % (wtrio[1].decode('utf-8'), wtrio[2].decode('utf-8'), wtrio[0].decode('utf-8'), float(support)/doc2['support']))
                if wtrio[2] in doc2['item_set'] and wtrio[0] in doc2['item_set']:
                    print('%s, %s\t=>%s\t%f' % (wtrio[2].decode('utf-8'), wtrio[0].decode('utf-8'), wtrio[1].decode('utf-8'), float(support)/doc2['support']))
            for doc2 in col_cand1.find():
                conf = float(support)/doc2['support']
                if conf < min_conf:
                    continue;
                if wtrio[0] == doc2['item_set']:
                    print('%s\t=>%s, %s\t%f' % (wtrio[0].decode('utf-8'), wtrio[1].decode('utf-8'), wtrio[2].decode('utf-8'), float(support)/doc2['support']))
                if wtrio[1] == doc2['item_set']:
                    print('%s\t=>%s, %s\t%f' % (wtrio[1].decode('utf-8'), wtrio[2].decode('utf-8'), wtrio[0].decode('utf-8'), float(support)/doc2['support']))
                if wtrio[2] == doc2['item_set']:
                    print('%s\t=>%s, %s\t%f' % (wtrio[2].decode('utf-8'), wtrio[0].decode('utf-8'), wtrio[1].decode('utf-8'), float(support)/doc2['support']))
    else:
        print('Invalid length')

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
