#!/usr/bin/python
#coding:utf-8

"""
classiasにいれるmodel fileを作るプログラム


実行方法
python baseline.py --input [fileaname] --output [output filename]

form of input file 
"flag\tdata\ttweet"
"""

__author__ = "@Ace12358"
__version__ = "1.0"
__date__ = "2014/10/1"

import sys
import MeCab
import re
import argparse
import csv
import string

def getArgs():
    """
    optional argument setting
    """
    parser = argparse.ArgumentParser(description="make classias model")

    parser.add_argument(
        "-i", "--input",
        dest="train_file",
        type=argparse.FileType("r"),
        required=True,
        help="input filename as train data"
    )

    parser.add_argument(
        "-o", "--output",
        dest="model_file",
        type=argparse.FileType("w"),
        default=sys.stdout,
        help="output filename as classias model"
    )
    parser.add_argument(
        "-t", "--tsutsuji",
        dest="tsutsuji_file",
        type=argparse.FileType("r"),
        default=sys.stdout,
        help="tsutsuji filename as tsutsuji data"
    )

    return parser.parse_args()

def FeatureUrl(tweet):
    """
    urlの有無を返す関数
    入力: tweet
    出力: 0 or 1
    """
    re_url = re.compile("https?://[\w/:%#\$&\?\(\)~\.=\+\-]+") #URLの正規表現
    re_url_search = re_url.search(tweet)
    if re_url_search == None:
        return 0
    else:
        return 1

def FeatureMention(tweet):
    """
    Mention（@がついているか）なのかそうでないかを返す関数
    入力：tweet
    出力：0 or 1
    """
    re_account = re.compile("@[0-9a-zA-Z_]{1,15}")
    re_account_search = re_account.search(tweet)
    if re_account_search == None:
        return 0
    else:
        return 1

def FeatureWindow(tweet, word, window=6):
    """
    wordを中心とする周辺単語を抜き出す関数
    window幅のデフォルトは6(前3つ,後3つ)
    入力:tweet
    出力:window_list(を含む前後のwindowのを抽出)
    """
    window_list=list() #全体のwindowのリスト
    r_window_list = list() #wordの右のwindowのリスト
    l_window_list = list() #wordの左のwindowのリスト
    tagger = MeCab.Tagger('-Owakati')
    mecab_result = tagger.parse(tweet)
    mecab_result_list = mecab_result.strip().split()
    for i in range(len(mecab_result_list)):
        if mecab_result_list[i]==word or mecab_result_list[i]=="インフル" or mecab_result_list[i]=="シュタインフルエンザ":
            for j in range(window/2):
                try:
                    l_window_list.append(mecab_result_list[i-(window/2)+j])
                except(IndexError):
                    l_window_list.append("None")
            #print " ".join(l_window_list), "LEFT"
            for j in range(window/2):
                try:
                    r_window_list.append(mecab_result_list[i+1+j])
                except(IndexError):
                    r_window_list.append("None")
            #print " ".join(r_window_list), "RIGHT"
    window_list = l_window_list + r_window_list
    return window_list

def FeatureNgram(tweet, word, window=4):
    """
    wordを中心とする文字ngramを抜き出す関数
    ngramのnのデフォルトは4
    入力:tweet
    出力:文字ngram
    """
    word = word.decode("utf-8")
    tweet = tweet.decode("utf-8")
    re_word = re.compile(word)
    re_word_search = re_word.search(tweet) #修正の余地あり
    try:
        start_index = re_word_search.start(0)
        end_index = re_word_search.end(0)
        r_ngram = tweet[end_index:end_index+window]
        l_ngram = tweet[start_index-window:start_index]
        #半角スペースを0に変換
        l_ngram = l_ngram.translate({ord(u' '): u'0'})
        r_ngram = r_ngram.translate({ord(u' '): u'0'})
        #どちらも文字列がwindow数の大きさになるまで"0"をつめる
        while (len(r_ngram)) != window:
            r_ngram+="0"
        while (len(l_ngram)) != window:
            l_ngram = "0" + l_ngram
        ngram = l_ngram + "|" + r_ngram
        return ngram
    except(AttributeError):
        #wordがないものがあるのでその場合はNoneを返す
        return None

def main():
    """
    main関数
    classiasのモデルを作れるような形式でfileを作成
    """
    cnt = 1 #tweet index
    pos_cnt = 0
    neg_cnt = 0
    neu_cnt = 0
    #Reader = csv.reader(args.train_file)
    for line in args.train_file:
	print "tweet %d" %cnt
	cnt += 1
        itemList = line.strip().split('\t')
        flag = itemList[0] #0 or 1
        if flag == "?":
            neu_cnt += 1
            continue
        elif flag == "0":
            neg_cnt += 1
            flag = "-1"
        else:
            pos_cnt += 1

        data = itemList[1] #data
        tweet = itemList[3] #tweet
        # feature extraction
        f_url = FeatureUrl(tweet)
        f_mention = FeatureMention(tweet)
        f_window_list = FeatureWindow(tweet,"インフルエンザ")
        if len(f_window_list)==0:
            print "line: %d invalid tweet data" %cnt
            continue
        f_ngram = FeatureNgram(tweet, "インフルエンザ")
        if f_ngram == None: #インフルエンザが入っていないtweet
            f_ngram = FeatureNgram(tweet, "インフル")
            if f_ngram == None: #インフルが入っていないtweet
                continue
        args.model_file.write("# %s\n" %tweet)
        args.model_file.write("%s " %flag) 
        #args.model_file.write("url=%d " %f_url)
        #args.model_file.write("mentoin=%d " %f_mention)
        """
        for i in range(len(f_ngram)/2):
        #    print i
            args.model_file.write("f_ngram_l=%s " %f_ngram.split("|")[0][0:0+i+1].encode("utf-8"))
            args.model_file.write("f_ngram_r=%s " %f_ngram.split("|")[1][0:0+i+1].encode("utf-8"))
        """
        ####windowをBOWで入れる
        args.model_file.write("%s " %f_window_list[0])
        args.model_file.write("%s " %f_window_list[1])
        args.model_file.write("%s " %f_window_list[2])
        args.model_file.write("%s " %f_window_list[3])
        args.model_file.write("%s " %f_window_list[4])
        args.model_file.write("%s " %f_window_list[5])

        args.model_file.write("\n")

    print "finish!"
    print "positive=%d, negative=%d, neutal=%d" %(pos_cnt,neg_cnt,neu_cnt)
if __name__=="__main__":
    args=getArgs()
    main()
