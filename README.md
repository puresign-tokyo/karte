# karte
リプ会主催者用自動ダウンローダ

## 機能
- L-uploaderの情報をもとに3分毎に以下のことを行います
  - リプレイの指定ディレクトリへの自動ダウンロード
    - `thXX_udXXXX.rpy` 形式が使えないファイルは `thXX_XX.rpy` 形式に自動でリネームする
  - メタデータの記載
    - ユースケースはリプレイ大会等の場でタイトルにメタデータを記載するときなど

## 由来
- Keep And Record Touhou Experience

## ファイル構成
```
.
├── main.exe
└── settings.json
```

## 設定ファイル
- 設定ファイルはjson5形式なので末尾カンマ, `//` によるコメントが許される

```json
{
    "timezone": "Asia/Tokyo",
    "backend_url": "http://l-uploader-api.puresign.tokyo",
    "search_days_back": 15,
    "optional_tag": "",
    "karte_homedir": "/home/wefmaika/karte",
    "posts_per_page": 10,
    "max_page": 50,
    "replay_summary": "{game_name} {user_name}さん {upload_comment}",
    "user_name_truncate_with": 15,
    "upload_comment_truncate_with": 35,
    "games": {
        "alco": {
            "game_name": "黄昏酒場",
            "path": "E:/DIRECTORY/黄昏酒場～Uwabami Breakers～/replay",
            "ud_replay_rename_limit": 25,
        },
        "th20": {
            "game_name": "錦上京",
            "path": "C:/Users/USER_NAME/AppData/Roaming/ShanghaiAlice/th20/replay",
            "ud_replay_rename_limit": 0,
        },
    },
}
```

- timezone
  - IANAによって定義されるタイムゾーン
  - `Asia/Tokyo` など
- backend_url
  - えるろだのバックエンドサーバを記載する
- search_days_back
  - 何日前までを検索スコープとするか
- optional_tag
  - このタグが書かれているもののみ検索する
  - 全てのリプレイを検索したいときは`""`とする
- karte_homedir
  - 内部ファイルやメタデータ記載ファイルを保存するディレクトリ
  - 絶対パスで記載すること
- posts_per_page
  - GUI上の1ページあたりの表示上限
  - 検索中これより少ない数のページを見つけると, それが最古のページとみなしそれ以上検索しない
- max_page
  - GUI上の何ページ目まで検索するかを設定する
- replay_summary
  - ダウンロードしてきたメタデータをどのような文字列で記載するか
  - 以下のタグが使用可能
    - game_name
      - ゲーム名
      - ゲームIDに対して後述する `games.{ゲームID}.game_name` によって指定されるゲーム名を記載する
    - user_name
      - ユーザ名
    - upload_comment
      - アップロード時のコメント
- user_name_truncate_with
  - リプレイメタデータにユーザ名を書くときに何文字で区切るか
- upload_comment_truncate_with
  - リプレイメタデータにアップロードコメントを書くときに何文字で区切るか
- games
  - ゲームのメタデータを記載する
  - ゲームIDをキーに辞書形式で書くこと
    - ゲームIDはリプレイファイルの先頭についているものと思って貰ってよい
  - ゲームIDには以下のキーがある
    - game_name
      - リプレイメタデータに記載するゲーム名
    - path
      - リプレイをどこにダウンロードするか
    - ud_replay_rename_limit
      - 何個目のものからud形式のリプレイに変換するか
      - アルゴリズムを含めた詳細な説明
        - Karteはデフォルトでリプレイを`thXX_YY.rpy`形式に変換しようとする
        - `ud_replay_rename_limit`が0ならリネームせずに保存する
        - `thXX_YY.rpy`の`YY`の値を1から`ud_replay_rename_limit`まで変えて存在しないファイル名があればそのファイル名で保存する
        - 以上の探索で全てのファイル名が存在していた場合リネームせずに保存する

## pyinstallerによる実行ファイル作成手順
- Python環境がない人には実行ファイルとして渡さなければならない。
```
$ pyinstaller --clean --onefile --hidden-import json5 --hidden-import requests --hidden-import tzdata --hidden-import colorama main.py
```