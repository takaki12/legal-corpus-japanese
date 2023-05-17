# download_precedent.pyで取得した判例(pdf)をテキストファイルに変換する
# text_filesに出力される
# 前処理もできる

import os
import re
import pdfminer
from pdfminer.high_level import extract_text

gengo_list = ["令和","平成","昭和"]

def preprocessing(text):
    """
    PDFが変換されたtexting型の文字列を適切な形に変形する。
    前処理も行う

    Args:
        text (str): 文字列
    """
    # 行頭の不要な見出し語削除
    text = re.sub("(?:^|\n)(?: |　)*(?:[ア-ン]|\(|\)|\（|\）|[0-9]|[０-９]|[一二三四五六七八九])+(?: |　)+","",text)
    # 大文字空白, 小文字空白を削除
    text = re.sub("　| ","",text)
    # ページ番号の削除
    text = re.sub("-[ ]?[0-9]+[ ]?-","",text)
    # 括弧付き数字の削除
    text = re.sub("(?:[⑴-⒇⒜-⒵]|\（[0-9|一二三四五六七八九]\）)","",text)
    #【要旨】などの特殊な括弧をまとめて削除
    text = re.sub("【.*?】","",text)
    # 〇文字の削除
    text = re.sub("[①-⑳❶-❿➊-➓㋐-㋾ⓐ-ⓩ]","",text)
    # 読み込めない文字の削除
    text = re.sub("","",text)
    # 空白行の削除
    text = re.sub("(?:\n)+","\n",text)
    # 半角数字の削除、要検討!
    text = re.sub("[0-9]+","",text)
    # 句点の統一(","と"，" を "、" に)
    text = re.sub(",|，","、",text)

    # 括弧内の処理
    # 一時的に"。"を[MARU]に変えておく
    while(True):
        # 二重括弧の場合などに備え、内側の括弧から順に処理している.
        # 一度括弧を別の文字列に置き替え、二度目のループでは二重括弧の外側の括弧を処理する
        #。の後の括弧を削除
        text = re.sub("。\n?\([^\(\)]*?\)","。\n",text)
        text = re.sub("。\n?\（[^\（\）]*?\）","。\n",text)
        text = re.sub("。\n?\「[^\「\」]*?\」","。\n",text)
        text = re.sub("(?:\n)+","\n",text)

        # 括弧をグループとして抜き出し、括弧内の。を,に置き替える
        parentheses = re.findall("\([^\(\)]*?\)",text)
        parentheses.extend(re.findall("\（[^\（\）]*?\）",text))
        parentheses.extend(re.findall("\「[^\「\」]*?\」",text))

        if parentheses == []:
            break

        for parenthese_line in parentheses:
            parenthese_line_after = re.sub("。","{MARU}",parenthese_line) # 置換
            parenthese_line_after = re.sub("\(",   "{parentheses001}",parenthese_line_after)
            parenthese_line_after = re.sub("\)",   "{parentheses002}",parenthese_line_after)
            parenthese_line_after = re.sub("（",  "{parentheses003}",parenthese_line_after)
            parenthese_line_after = re.sub("）",  "{parentheses004}",parenthese_line_after)
            parenthese_line_after = re.sub("「",  "{parentheses005}",parenthese_line_after)
            parenthese_line_after = re.sub("」",  "{parentheses006}",parenthese_line_after)
            text = text.replace(parenthese_line , parenthese_line_after)

    text = re.sub("{parentheses001}",  "(",   text)
    text = re.sub("{parentheses002}",  ")",    text)
    text = re.sub("{parentheses003}",  "（",   text)
    text = re.sub("{parentheses004}",  "）",   text)
    text = re.sub("{parentheses005}",  "「",   text)
    text = re.sub("{parentheses006}",  "」",   text)

    # 変な文字列の前後の文章を削除するために一度保存してからsave
    beforetext = ""
    # 同様に、変な文字列の後の文章を削除するため
    nexttext = False
    
    text_list = text.split("\n")
    return_text = ""
    save = ""
    for text_line in text_list:
        if "。" in text_line:
            while True:
                if len(save + re.sub("。.*","。",text_line)) >= 10: # 追加した一文が10文字以上
                    if nexttext == True:
                        nexttext = False
                    else:
                        return_text += beforetext
                        beforetext = save + re.sub("。.*","。",text_line) + "\n"
                else:
                    beforetext = ""
                    nexttext = True
                save = ""
                text_line = re.sub("^.*?。","",text_line)
                if text_line == "":
                    break
                elif "。" in text_line:
                    pass
                else:
                    save += text_line
                    break
        elif len(text_line) >= 10:
            save += text_line
        elif text_line == "主文": # 主文前の文章は破棄
            return_text = ""
            save = ""
        elif text_line == "理由" or text_line == "事実及び理由": # 理由前の文章は破棄
            return_text = ""
            save = ""
            pass
        elif text_line == "":
            pass
        else:
            save = ""
    return_text += beforetext

    # 文頭の一文字だけのカタカナ、アルファベットの削除
    return_text = re.sub("(\n)[ア-ンａ-ｚa-z]([^ア-ンａ-ｚa-z])","\\1\\2",return_text)
    # 文頭の一文字だけの数字の削除
    return_text = re.sub("(\n)[０-９]+([^０-９項条月日人])","\\1\\2",return_text)
    # (の前に)が来るなど明らかに変な文章の削除
    return_text = re.sub("\n[^\(\)]*?\).*?。\n","\n",return_text)
    return_text = re.sub("\n[^\（\）]*?\）.*?。\n","\n",return_text)
    return_text = re.sub("\n[^\「\」]*?\」.*?。\n","\n",return_text)
    return_text = re.sub("(?:\n)+","\n",return_text)

    # 最後に[MARU]を”。”に置き替える。
    return_text = re.sub("{MARU}","。",return_text)
    return return_text


if __name__=='__main__':
    pdf_files_dir = 'precedent/pdf_files'
    text_files_dir = 'precedent/text_files'
    gengo_list = os.listdir(pdf_files_dir)
    for gengo in gengo_list:
        year_list = os.listdir(pdf_files_dir + '/' + gengo)
        if not os.path.exists(text_files_dir + '/' + gengo):
            os.makedirs(text_files_dir + '/' + gengo)
        for year in year_list:
            pdf_files = os.listdir(pdf_files_dir + '/' + gengo + '/' + year)
            if not os.path.exists(text_files_dir + '/' + gengo + '/' + year):
                os.makedirs(text_files_dir + '/' + gengo + '/' + year)
            for pdf_file in pdf_files:
                file_path = '/' + gengo + '/' + year + '/' + pdf_file
                text = extract_text(pdf_files_dir + file_path)
                text_processed = preprocessing(text)
                output_dir = text_files_dir + file_path.replace('.pdf','.txt')
                with open(output_dir, 'w') as f:
                    f.writelines(text_processed)