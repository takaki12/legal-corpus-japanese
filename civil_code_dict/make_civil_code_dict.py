# 民法の辞書を作成する

import os
import re
import csv
import pickle
from convert_kansuji_to_number import convert_kansuji_to_number

# リストと辞書
# 漢数字
kansuji_list = ['零','一','二','三','四','五','六','七','八','九','十','十一','十二','十三','十四','十五','十六','十七','十八','十九','二十','二十一','二十二','二十三','二十四','二十五']
# 大文字の数字の辞書
large_num_dict = {1:'１',2:'２',3:'３',4:'４',5:'５',6:'６',7:'７',8:'８',9:'９'}
# 大文字の数字の辞書
large_num_dict_re = {'１':1,'２':2,'３':3,'４':4,'５':5,'６':6,'７':7,'８':8,'９':9}

#"次に掲げる"の後に出てくる単語のリスト(例として次に掲げる原因)、第何条に規定するxxの時も使用
#next_list = ['場合', '事由', '事項', 'とき', '時', 'もの' ,'ところ', '行為', '区分', '者', '方式', '錯誤', '事実', '原因', '債務', '要件', '順序', '書面','催告','責任','権利','死亡','期間','規定','追認','合意','書面','公正証書','申し込み','広告','意思表示','不適合','委任','組合員','組合','目録','権限','公示','義務','期日','仲裁合意','意思表示','和解']
next_list = []
next_listfile = open('/home/tonaga/PycharmProjects/COLIEE2023/data/external/next_list.txt', 'r')
next_listline = next_listfile.readlines()
for line in next_listline:
    next_list.append(re.sub("\n","",line))

def check_article_num(data, article_num):  # (第一条 債権は...)を[債権は,1]のように返す、numはString型で返却される点に注意、(例,第二百五十五条の二　→　255-2)
    m1 = re.match('第[一|二|三|四|五|六|七|八|九|十|百]+条の[一|二|三|四|五|六|七|八|九|十|百]+', data)
    m2 = re.match('第[一|二|三|四|五|六|七|八|九|十|百]+条', data)
    if m1:
        stringobje = re.sub('第', '', m1.group())
        stringobje = re.sub('条の[一|二|三|四|五|六|七|八|九|十|百]+', '', stringobje)
        num = str(convert_kansuji_to_number(stringobje))
        stringobje = re.sub('第.*条の', '', m1.group())
        num = num + '-' + str(convert_kansuji_to_number(stringobje))
    elif m2:
        stringobje = re.sub('第', '', m2.group())
        stringobje = re.sub('条', '', stringobje)
        num = str(convert_kansuji_to_number(stringobje))
    else:
        num = str(article_num)
    data = re.sub("第[一|二|三|四|五|六|七|八|九|十|百]+条の[一|二|三|四|五|六|七|八|九|十|百]+((\u3000)|( )|(　))","", data)
    data = re.sub("第[一|二|三|四|五|六|七|八|九|十|百]+条((\u3000)|( )|(　))","", data)
    data = re.sub("\u3000","",data)
    data = re.sub("\n","",data)
    return data, num

# 辞書を作成するメソッド
def make_civil_code_dict(input_dir='', output_dir=''):
    """
    input_dir : 民法条文のファイルパス
    output_dir : 辞書の出力先
    """

    if input_dir == '':
        input_dir = 'data/civil_code_jp.txt'
    if output_dir == '':
        output_dir = 'output'
    
    civil_code_dict = {} # 民法の辞書、条番号をkeyとし、それに含まれる条文のリストをvalueとする
    civil_code_dict_Kakugou = {} # 民法の"各号"を保存
    civil_code_dict_withKou = {} # 民法の辞書、条番号+_項番号をkeyとし、それに含まれる条文のリストをvalueとする
    tuginikakageru_beforetext = ''
    tuginikakageru_aftertext = ''
    condition = 0 # 次に掲げる等で代入を行う際に使用
    Kou_num = "1" # 項番号を記載

    article_num = '0'
    f = open(input_dir,'r')
    datalist = f.readlines()
    for data in datalist:
        if condition != 0: # 次に掲げるにより単なる条文でない場合の処理
            if data.startswith(kansuji_list[condition]):#「次に掲げる」に関する文章
                data = data.replace(kansuji_list[condition],'',1)
                data = data.replace('。','')
                condition += 1
            elif data.startswith('イ') or data.startswith('ロ') or data.startswith('ハ'):
                #イロハは保留:
                pass
            else: # それ以外の文章、次の文章に移っている
                civil_code_dict_Kakugou[article_num+"_"+Kou_num] = KakugouList
                condition = 0
        Beforearticle_num = article_num
        data,article_num = check_article_num(data,article_num) # 条番号を取得する,dataを整形する(第何条などの情報を削除)
        if not ( Beforearticle_num  == article_num ):
            Kou_num = "1"
        for smallint,Largenum in large_num_dict.items():#"２　組合の業務の決定及び執行は",などの大文字の数字を削除
            if data.startswith(Largenum):
                Kou_num = str(smallint)
                data = data[1:]

        if '次に掲げる'  in data or '次の各号に掲げる' in data or '次のとおり' in data:#次に掲げるの処理,詳細は次行
            #1行目　Aは次に掲げる権利を持つ,2行目　人権,三行目 投票権　のようになっているため、一行目を読み飛ばし二行目から代入していく
            #tuginikakageru_beforetextに "Aは" ,tuginikakageru_aftertextに "を持つ" を代入する
            findNext = False
            for Next in next_list:
                if ('次に掲げる'+Next) in data:
                    tuginikakageru_beforetext = re.split(('次に掲げる'+Next),data)[0]
                    tuginikakageru_aftertext = re.split(('次に掲げる'+Next),data)[1]
                    findNext=True
            if '次の各号に掲げる' in data:
                tuginikakageru_beforetext = re.split('次の各号に掲げる',data)[0]
                tuginikakageru_aftertext = re.split('次の各号に掲げる',data)[1]
                findNext=True
            if '次のとおり' in data:
                tuginikakageru_beforetext = re.split('次のとおり',data)[0]
                tuginikakageru_aftertext = re.split('次のとおり',data)[1]
                findNext=True
            if not findNext:
                print('new次に掲げる:'+data)
            condition = 1
            KakugouList = [] #”各号”を保存

        if condition == 1:#何の文章かチェック、「次に掲げる」の文章の時読み飛ばす
            pass
        elif data.startswith('イ') or data.startswith('ロ') or data.startswith('ハ')\
            or '三主たる債務者（法人であるものを除く。以下この号において同じ。）と共同して事業を行う者又は主たる債務者が行う事業に現に従事している主たる債務者の配偶者' in data:
            #イロハ、主たる債務者...は保留
            pass
        elif re.search('。',data) or condition != 0:#条文などのとき
            
            if condition !=0:#次に掲げる内の箇条書きの処理
                KakugouList.append(data)
                data = tuginikakageru_beforetext + data + tuginikakageru_aftertext

            if article_num in civil_code_dict: # 民法辞書を作成、代入や検索の時に使用するために、条番号と条文内容の辞書を作成
                civil_code_dict[article_num].append(data)
            else:
                civil_code_dict[article_num] = [data]

            if article_num + "_" + Kou_num in civil_code_dict_withKou:
                civil_code_dict_withKou[article_num + "_" + Kou_num].append(data)
            else:
                civil_code_dict_withKou[article_num + "_" + Kou_num] = [data]

            T1 = T2 = data

        elif re.search('(.*)',data) or re.search('第.章',data) \
        or re.search('第.節',data) or re.search('第.款',data):#()、章、節、款のとき読み飛ばす
            pass
        else: # 上記のどれにも当てはまらない時
            print('error20221:' + data)

    # 出力
    # 各号
    with open(output_dir + '/civil_code_dict_Kakugou.pkl', 'wb') as fp:
        pickle.dump(civil_code_dict_Kakugou, fp)

    # 民法そのまま
    with open(output_dir + '/civil_code_dict.pkl', 'wb') as fp:
        pickle.dump(civil_code_dict, fp)
    
    # 民法を項単位で分割したもの
    with open(output_dir + '/civil_code_dict_withKou.pkl', 'wb') as fp:
        pickle.dump(civil_code_dict_withKou, fp)

if __name__=='__main__':
    make_civil_code_dict()