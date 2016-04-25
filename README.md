# PMCA+
PMCAv0.0.6r10をベースに改修中。
fullpython化しようとしていたが、モデル編集部分はCじゃないと速度が稼げないと判明。

# Bug
* [o] ファイル/読み込み sample2.cnl
* [ ] 外部モデル
* [o] テクスチャパス
* [ ] 鞄の位置

# ToDo
* [ ] Info
    - [ ]Author/License
* [o] menu移植
    - [o] ファイル/読み込み
    - [o] ファイル/保存
    - [o] ファイル/モデル保存
    - [o] ファイル/一括組み立て
    - [o] ファイル/PMDフォーマットチェック
    - [o] ファイル/PMD概要確認
    - [o] ファイル/PMD詳細確認
* [ ] 編集/PMCA設定
* [ ] パーツ所属アセット名表示
* [o] listに文字列ではなくオブジェクトを格納する。__str__
* [ ] 外部モデル

# 済み
* GUIをtkinterからPyQt4に変更
* Python3.2 32bitからPython3.5 64bit(Anaconda)に変更
* PMCA.pydからOpenGL関連をPyOpenGLに移動
* PARTS定義をAssetsディレクトリに移動。追加パーツのディレクトリをAssetsディレクトリにコピーすれば読み込める

