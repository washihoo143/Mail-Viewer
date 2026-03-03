# Mail Viewer

mbox形式のメールをブラウザで閲覧・検索できるシンプルなWebアプリです。

---

## 📌 概要

- mboxファイルを読み込み
- SQLiteに保存
- ブラウザで検索・閲覧可能
- HTMLメール対応
- ページネーション対応

ローカル環境で動作します。

---

## 🛠 必要環境

- Python 3.9 以上

---

## 📦 必要ライブラリ

以下をインストールしてください。

```bash
pip install flask
```

※ sqlite3 / mailbox / email はPython標準ライブラリのため追加インストール不要です。

---

## 🚀 セットアップ手順

### ① ライブラリのインストール

```bash
pip install flask
```

※ sqlite3 / mailbox / email はPython標準ライブラリのため追加インストール不要です。

---

### ② mboxファイルをデータベースに変換

```bash
python mbox_to_sqlite.py
```

実行すると `input.mbox` が読み込まれて `mail.db` が生成されます。
※ `input.mbox` ファイルはあらかじめ同じディレクトリに配置してください。

---

### ③ アプリ起動

```bash
python viewer.py
```

---

### ④ ブラウザでアクセス

```
http://localhost:5000
```

---

## 🗄 データベースについて

- SQLiteを使用しています
- `mbox_to_sqlite.py` 実行時に `mail.db` が自動生成されます

保存内容：

- 件名
- 送信者
- 受信日時
- テキスト本文
- HTML本文
- 全文検索インデックス（FTS5）

### ⚠ 重要

事前に `mbox_to_sqlite.py` を実行して、mboxファイルをSQLiteデータベースに変換する必要があります。

---

## 📂 ディレクトリ構成例

```
project/
│
├── input.mbox（メールファイル）
├── mbox_to_sqlite.py
├── viewer.py
├── templates/
│   ├── index.html
│   └── mail.html
├── mail.db（自動生成）
└── README.md
```

---

## 🔍 機能

- **検索機能**：キーワードで件名・送信者・本文から全文検索
- **日付フィルタ**：受信日時の範囲で絞り込み
- **ページネーション**：50件ずつ表示
- **HTML対応**：HTML形式のメールも表示可能
- **全文検索**：FTS5によって高速な検索を実現

---

## 🛠 技術スタック

- **Backend**：Python + Flask
- **Database**：SQLite + FTS5
- **Frontend**：HTML + CSS + JavaScript

---

## ⚠ 注意事項

- mboxファイルや mail.db はGit管理しないことを推奨します
- `.gitignore` に以下を追加してください：
  ```
  input.mbox
  mail.db
  ```
- 個人情報を含むデータの扱いに注意してください
- 本アプリはローカル利用を前提としています

---

## 📌 今後の拡張例

- 添付ファイル表示
- ダウンロード機能
- Docker対応
- クラウドデプロイ
