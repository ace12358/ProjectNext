####ProjectNext Web応用 に関するプログラム

Help on module ModelMaker:

NAME
    ModelMaker - classiasにいれるmodel fileを作るプログラム

FILE
    /Users/kitagawayoshiaki/Works/ProjectNext/scripts/ModelMaker.py

DESCRIPTION
    ####実行方法
    ---
    > python ModelMaker.py --input [csv形式のfile名] --output [output filename]
    
    ####csv の形式(field)
    ---
    "flag", "data", "tweet"

FUNCTIONS
    FeatureMention(tweet)
        @ での返信なのかそうでないかを返す関数
        入力：tweet
        出力：0 or 1
    
    FeatureNgram(tweet, word, window=4)
        wordを中心とする文字ngramを抜き出す関数
        ngramのnのデフォルトは4
        入力:tweet
        出力:文字ngram
    
    FeatureUrl(tweet)
        urlの有無を返す関数
        入力: tweet
        出力: 0 or 1
    
    FeatureWindow(tweet, word, window=6)
        wordを中心とする周辺単語を抜き出す関数
        window幅のデフォルトは6(前3つ,後3つ)
        入力:tweet
        出力:window_list(を含む前後のwindowのを抽出)
    
    getArgs()
        optional argument setting
    
    main()
        main関数
        classiasのモデルを作れるような形式でfileを作成

DATA
    __author__ = '@Ace12358'
    __date__ = '2014/10/1'
    __version__ = '1.0'

VERSION
    1.0

DATE
    2014/10/1

AUTHOR
    @Ace12358


