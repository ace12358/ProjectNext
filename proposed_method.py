#/usr/bin/python
#coding:utf-8

"""
classiasにいれるmodel fileを作るプログラム


実行方法
python proposed_method.py --input [fileaname] --output [output filename] --tsutsuji [tsutsujifilename]
form of input file 
"flag\tdata\ttweet"
"""

__author__ = "@Ace12358"
__version__ = "1.0"
__date__ = "2014/12/1"

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

    parser.add_argument(
        "-d", "--debug",
        action='store_true',
        default=False,
        help="debug mode if this flag is set (default: False)"
    )
    parser.add_argument(
        "-u", "--URL",
        action='store_true',
        default=False,
        help="add feature: URL"
    )
    parser.add_argument(
        "-a", "--atmark",
        action='store_true',
        default=False,
        help="add feature: @*** tweet (mention tweet)"
    )
    parser.add_argument(
        "-n", "--ngram",
        action='store_true',
        default=False,
        help="add feature: ngram"
    )
    parser.add_argument(
        "-m", "--modality",
        action='store_true',
        default=False,
        help="add feature: modality if you this option, you use -t option and assign tsutsuji file"
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

def FeatureTsutsuji(tweet, word, TsutsujiDict):
    """
    tweet中の機能表現にマッチするもののリストを返す
    入力:tweet,着目word, tsutsujiの辞書(key=表層, value=意味ID)
    出力:マッチした機能表現の意味IDリスト
    """
    ID_list = list()
    tweet = tweet.decode("utf-8")
    re_word = re.compile(word.decode("utf-8"))
    if re_word.search(tweet) == None:
        print "%s is not in tweet"
        return ID_list
    re_word_end_index = re_word.search(tweet).end()
    tweet_right = tweet[re_word_end_index:re_word_end_index+15]
    ####部分文字列の取得
    for s in range(len(tweet_right)):
        for e in range(s, len(tweet_right)):
            part_tweet_right = tweet_right[s:e]
            if part_tweet_right in TsutsujiDict and len(part_tweet_right)>=1:
                ID_list.append(TsutsujiDict[part_tweet_right])
                print part_tweet_right, TsutsujiDict[part_tweet_right]
    return ID_list
def main():
    """
    main関数
    classiasのモデルを作れるような形式でfileを作成
    """
    #つつじの辞書の読み込み
    if args.modality:
        TsutsujiDict = dict()
        for line in args.tsutsuji_file:
            itemList = line.strip().split(",")
            surface = itemList[0].decode("utf-8")
            wordsenseID = itemList[3]
            TsutsujiDict[surface] = wordsenseID
    #for count line
    #lines = args.train_file.readlines()
    #counter
    cnt = 0 #tweet index
    pos_cnt = 0
    neg_cnt = 0
    neu_cnt = 0
    
    #file reading
    for line in args.train_file:
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
        if args.modality:
            f_tsutsuji_list = FeatureTsutsuji(tweet,"インフル",TsutsujiDict) #右のwindow 3つ
        if len(f_window_list)==0:
            #print "line: %d invalid tweet data. label=%s tweet=%s" %(cnt,flag,tweet)
            continue
        f_ngram = FeatureNgram(tweet, "インフルエンザ")
        if f_ngram == None: #インフルエンザが入っていないtweet
            f_ngram = FeatureNgram(tweet, "インフル")
            if f_ngram == None: #インフルが入っていないtweet
                continue
        args.model_file.write("# %s\n" %tweet)
        args.model_file.write("%s " %flag)
        if args.URL: 
            args.model_file.write("url=%d " %f_url)
        if args.atmark:
            args.model_file.write("mentoin=%d " %f_mention)
        if args.ngram:
            for i in range(len(f_ngram)/2):
                args.model_file.write("f_ngram_l=%s " %f_ngram.split("|")[0][0:0+i+1].encode("utf-8"))
                args.model_file.write("f_ngram_r=%s " %f_ngram.split("|")[1][0:0+i+1].encode("utf-8"))
        """
        for i in range(len(f_ngram)/2):
        #    print i
            args.model_file.write("f_ngram_l=%s " %f_ngram.split("|")[0][0:0+i+1].encode("utf-8"))
            args.model_file.write("f_ngram_r=%s " %f_ngram.split("|")[1][0:0+i+1].encode("utf-8"))
        """
        #add feature: windowBOW
        args.model_file.write("%s " %f_window_list[0])
        args.model_file.write("%s " %f_window_list[1])
        args.model_file.write("%s " %f_window_list[2])
        args.model_file.write("%s " %f_window_list[3])
        args.model_file.write("%s " %f_window_list[4])
        args.model_file.write("%s " %f_window_list[5])
        ####つつじの意味ID素性を作成
        if args.modality:
            for f_tsutsuji in f_tsutsuji_list:
                args.model_file.write("f_tsutsuji_ID=%s " %f_tsutsuji)

        args.model_file.write("\n")

        print "\r%f" %(float(cnt)/10935),
        print cnt,
    print "finish!"
    print "positive=%d, negative=%d, neutal=%d, total=%d" %(pos_cnt,neg_cnt,neu_cnt, cnt)
if __name__=="__main__":
    args=getArgs()
    main()
