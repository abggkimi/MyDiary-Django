# My日記 Djangoアプリケーション

## アプリ概要

このアプリケーションはスクール内ので再作をした。Webアプリケーションです。
ユーザーが日記を書いたり他のユーザーと共有したりすることができます。

## 使用技術

![](https://skillicons.dev/icons?i=html,css,python,django,sqlite)

## 環境

Python 3.14.9
Django 5.2.18

## 環境設定

当環境は Django 5.2.18 を使用しています。作業ディレクトリは `manage.py` がある場所です。

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install "Django==5.2.18"
```

秘密鍵はリポジトリに置かず、プロジェクト直下の `.env` に書きます。このファイルは Git の対象外です。

```bash
python -c "import secrets; print('DJANGO_SECRET_KEY=' + secrets.token_urlsafe(64))" > .env
python manage.py migrate
```

管理画面を使うときは、スーパーユーザーを作成します。

```bash
python manage.py createsuperuser
```

## 起動方法

開発サーバは HTTP で動きます。`DJANGO_DEBUG` を付けない起動は HTTPS へ転送されるため、画面は開きません。

```bash
source .venv/bin/activate
python manage.py migrate
DJANGO_DEBUG=true python manage.py runserver
```

ブラウザで http://127.0.0.1:8000/ を開きます。管理画面は http://127.0.0.1:8000/admin/ です。

`diary_diary` がないというエラーが出るときは、テーブルが未作成です。`python manage.py migrate` を実行してから、ページを再読み込みします。

## 環境変数

値は環境変数か `.env` に書きます。同じ名前があるときは、環境変数が優先されます。

| 変数 | 既定 | 役割 |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | なし | セッションなどの署名に使う秘密鍵。`DEBUG` が無効なときは必須 |
| `DJANGO_DEBUG` | `false` | `true` で開発用の HTTP 起動。未設定時は本番向けの設定 |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1,[::1]` | 許可するホスト名。カンマ区切り |
| `DJANGO_USE_HTTPS` | `DEBUG` が無効なら有効 | HTTPS への転送と Secure Cookie を使うか |
| `DJANGO_SECURE_HSTS_SECONDS` | `31536000` | HTTPS 利用時の HSTS の秒数。導入初期は短い値から始める |
| `DJANGO_SKIP_DOTENV` | 無効 | `true` のとき `.env` を読まない。テストの子プロセス用 |

本番では、実際のホスト名を `DJANGO_ALLOWED_HOSTS` に設定します。TLS をリバースプロキシで終端する場合は、プロキシが `X-Forwarded-Proto: https` を付けます。

## コマンド

仮想環境を有効にした状態で実行します。

`check` と `check --deploy` は、`.env` に `DJANGO_SECRET_KEY` があれば追加の指定なしで実行できます。テストはテスト用のホスト `testserver` を許可し、HTTP のまま実行します。
