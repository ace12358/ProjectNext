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
from collections import defaultdict
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
        "-d", "--data",
        action='store_true',
        default=False,
        help="add feature: data(e.g. manth)"
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
    parser.add_argument(
        "-e", "--extent_modality",
        action='store_true',
        default=False,
        help="add feature: extent modality such as zunda if you this option, you use -z option and assign tsutsuji file"
    )
    parser.add_argument(
        "-z", "--zunda",
        dest="zunda_file",
        type=argparse.FileType("r"),
        default=sys.stdout,
        help="zunda filename as zunda data"
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
        if word in mecab_result_list[i]:
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
    if not window_list: #window_list is empty. mecab divide word
        for i in range(len(mecab_result_list)):
            if word in mecab_result_list[i]+mecab_result_list[i+1]:
                mecab_result_list[i]=mecab_result_list[i]+mecab_result_list[i+1]
                mecab_result_list.pop(i+1)
                break
            elif word in mecab_result_list[i]+mecab_result_list[i+1]+mecab_result_list[i+2]:
                mecab_result_list[i]=mecab_result_list[i]+mecab_result_list[i+1]+mecab_result_list[i+2]
                mecab_result_list.pop(i+1)
                mecab_result_list.pop(i+2)
                break
        for i in range(len(mecab_result_list)):
            if word in mecab_result_list[i]:
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
def FeatureZunda(tweet, word, index,zunda_feature_dict):
    """
    wordのあとのzunda素性を抜き出す関数
    入力:tweet,word,index,zunda_feature_candidate
    出力:zunda_feature_list
    """
    zunda_feature_list=list()
    zunda_feature_candidate_dict=zunda_feature_dict[str(index)]
    tagger = MeCab.Tagger('-Owakati')
    mecab_result = tagger.parse(tweet)
    mecab_result_list = mecab_result.strip().split()
    word_flag = False
    for i in range(len(mecab_result_list)):
        if word in mecab_result_list[i]:
            word_flag=True
        elif word_flag:
            if mecab_result_list[i] in zunda_feature_candidate_dict:
                zunda_feature_list.append("%s=%s" %(mecab_result_list[i], zunda_feature_candidate_dict[mecab_result_list[i]]))
                break
 
    if not word_flag:
        for i in range(len(mecab_result_list)):
            if word in mecab_result_list[i]+mecab_result_list[i+1]:
                mecab_result_list[i]=mecab_result_list[i]+mecab_result_list[i+1]
                mecab_result_list.pop(i+1)
                break
            elif word in mecab_result_list[i]+mecab_result_list[i+1]+mecab_result_list[i+2]:
                mecab_result_list[i]=mecab_result_list[i]+mecab_result_list[i+1]+mecab_result_list[i+2]
                mecab_result_list.pop(i+1)
                mecab_result_list.pop(i+2)
                break
        for i in range(len(mecab_result_list)):
            if word in mecab_result_list[i]:
                word_flag=True
            elif word_flag:
                if mecab_result_list[i] in zunda_feature_candidate_dict:
                    zunda_feature_list.append("%s=%s" %(mecab_result_list[i], zunda_feature_candidate_dict[mecab_result_list[i]]))
                    break
    return zunda_feature_list


def FeatureNgram(tweet, word, window=4):
    """
    wordを中心とする文字ngramを抜き出す関数
    ngramのnのデフォルトは
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
        return ID_list
    re_word_end_index = re_word.search(tweet).end()
    tweet_right = tweet[re_word_end_index:re_word_end_index+15]
    ####部分文字列の取得
    for s in range(len(tweet_right)):
        for e in range(s, len(tweet_right)):
            part_tweet_right = tweet_right[s:e]
            if part_tweet_right in TsutsujiDict and len(part_tweet_right)>=1:
                ID_list.append(TsutsujiDict[part_tweet_right][0:2])
                if len(ID_list)>=5: # 5 is best (I don't know why this is best)
                    return ID_list
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
    if args.extent_modality:
        zunda_feature_dict = defaultdict(lambda:dict())
        for line in args.zunda_file:
            item_list=line.strip().split()
            index = item_list[0]
            feature = item_list[1]
            key = feature.split('=')[0]
            flag = feature.split('=')[1]
            zunda_feature_dict[index][key]=flag
        
    #for count line
    #lines = args.train_file.readlines()
    #counter
    cnt = 0 #tweet index
    pos_cnt = 0
    neg_cnt = 0
    neu_cnt = 0
    invalid_data_cnt = 0
    
    #file reading
    for line in args.train_file:
        cnt += 1
        itemList = line.strip().split('\t')
        flag = itemList[0] #0 or 1
        data = itemList[1] #data
        tweet = itemList[3] #tweet

        if "インフルエンザ" not in tweet \
            and "インフル" not in tweet \
            and "ｲﾝﾌﾙｴﾝｻﾞ" not in tweet \
            and "ｲﾝﾌﾙ" not in tweet:
            invalid_data_cnt += 1
            continue
        target_word = str()
        if "インフルエンザ" in tweet:
            target_word = "インフルエンザ"
        elif "インフル" in tweet:
            target_word = "インフル"
        elif "ｲﾝﾌﾙｴﾝｻﾞ" in tweet:
            target_word = "ｲﾝﾌﾙｴﾝｻﾞ"
        elif "ｲﾝﾌﾙ" in tweet:
            target_word = "ｲﾝﾌﾙ"

        if flag == "?":
            neu_cnt += 1
            continue
        elif flag == "0":
            neg_cnt += 1
            flag = "-1"
        elif flag == "1" or flag == "+1":
            pos_cnt += 1
        else:
            print "invalid flag in line %d" %cnt
            invalid_data_cnt += 1
            continue
        # feature extraction
        f_url = FeatureUrl(tweet)
        f_mention = FeatureMention(tweet)
        f_window_list = FeatureWindow(tweet,target_word)
        f_data = data.split('/')[1]
        if args.modality:
            f_tsutsuji_list = FeatureTsutsuji(tweet,target_word,TsutsujiDict) #右のwindow 3つ
        f_ngram = FeatureNgram(tweet, target_word)
        if args.extent_modality:
            f_zunda_list = FeatureZunda(tweet,target_word,cnt,zunda_feature_dict)
        ####comment for classias
        args.model_file.write("# %s\n" %tweet)
        args.model_file.write("%s " %flag)

        ####feature write
        #add feature: windowBOW
        #print target_word
        for f_window in f_window_list:
            args.model_file.write("%s " %f_window)
        if args.data:
            args.model_file.write("%s " %f_data)
        if args.URL: 
            args.model_file.write("url=%d " %f_url)
        if args.atmark:
            args.model_file.write("mentoin=%d " %f_mention)
        if args.ngram:
            for i in range(len(f_ngram)/2):
                args.model_file.write("f_ngram_l=%s " %f_ngram.split("|")[0][0:0+i+1].encode("utf-8"))
                args.model_file.write("f_ngram_r=%s " %f_ngram.split("|")[1][0:0+i+1].encode("utf-8"))
        ####つつじの意味ID素性を作成
        if args.modality:
            for f_tsutsuji in f_tsutsuji_list:
                args.model_file.write("f_tsutsuji_ID=%s " %f_tsutsuji)
        ####zudna feature add
        if args.extent_modality:
            for f_zunda in f_zunda_list:
                args.model_file.write("%s " %f_zunda)

        args.model_file.write("\n")

        #print "\r%f" %(float(cnt)/10935),
        print "\r%d" %cnt,
    print "finish!"
    print "positive=%d, negative=%d, neutal=%d,invalid_data=%d total=%d" %(pos_cnt,neg_cnt,neu_cnt,invalid_data_cnt, cnt)
if __name__=="__main__":
    args=getArgs()
    main()
