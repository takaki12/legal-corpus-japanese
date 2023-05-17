# 判例をスクレイピングする
[裁判例検索](https://www.courts.go.jp/app/hanrei_jp/search1?reload=1) より収集

downlad_precedent.pyを実行することで収集できる。
pdf_filesフォルダが作成され、その中に収集した判例のpdfが保存される。  
  
その後、pdfファイルだと扱いづらいため、pdfファイルをtxtファイルに変換するために、convert_pdf_to_text.pyを使う。text_filesフォルダが作成され、その中の出力される。