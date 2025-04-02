# README.mdファイルを走査して、セトリの曲開始時間からYoutubeのタイムスタンプURLを自動付与するスクリプト
#
# 各配信について、以下のフォーマットでREADME.mdに記載しておくと曲の開始時間から再生されるURLを
# 自動的に付与してくれる。
#
# ``` README.md
# ## 2025-03-16 [【弾き語り】確定申告終わりました歌枠](https://www.youtube.com/watch?v=uUTYwl_U9RY)
# 
# 1. 5:19 チェリー / スピッツ
# 1. 16:44 怪獣の花唄 / Vaundy
# 1. 22:51 灰色と青 / 米津玄師 ( + 菅田将暉) 
# ```
# ↓処理後
# 
# ``` README.md
# ## 2025-03-16 [【弾き語り】確定申告終わりました歌枠](https://www.youtube.com/watch?v=uUTYwl_U9RY)
#
# 1. 5:19 [チェリー / スピッツ](https://www.youtube.com/watch?v=uUTYwl_U9RY&t=319s)
# 1. 16:44 [怪獣の花唄 / Vaundy](https://www.youtube.com/watch?v=uUTYwl_U9RY&t=1004s)
# 1. 22:51 [灰色と青 / 米津玄師 ( + 菅田将暉) ](https://www.youtube.com/watch?v=uUTYwl_U9RY&t=1371s)
# ```
#
# 処理語のREADME.mdに対して追記して処理することも可能。既にタイムスタンプURLが付与されている行も
# 再生成されるので、開始時間を修正する場合は曲名の前の時間だけ修正して実行すれば良い。

import re
import shutil

def main():
    # 一応バックアップファイルを作成（メインはgitで）
    shutil.copyfile("./README.md", "./README-backup.md")

    # 編集前のファイルをメモリ上に読み込む
    f = open("README.md", mode="r", encoding="utf-8")
    lines = f.read().splitlines()  # 改行コードを除いて行ごとに格納
    f.close()

    # 新規ファイルを作成
    f = open("README.md", mode="w", encoding="utf-8")
    parent_url = ''
    for i, line in enumerate(lines):
        print(line)
        if len(line) <= 1:
            f.write(line)
            f.write("\n")
            continue

        # 先頭が"##"で始まる行から親URLを取り出す。
        if line[0] == '#' and line[1] == '#':
            match = re.search(r'\((https?://[^\s)]+)\)', line)
            if not match:
                print("An error occurred while processing line {}. The parent URL does not exist.".format(i))
                print("Line {} text: {}".format(i, line))
                break
            else:
                parent_url = match.group(1)

        # セトリに曲開始時間のURLを追加する
        if line[0] == '1' and line[1] == '.':
            line = add_timestamp_link(line, parent_url)

        # 書き込む
        f.write(line)
        f.write("\n")
    
    f.close()
    print("Succeeded!")

# hh:mm:ss 形式の文字列を s(秒) 形式の文字列に変換する。
# mm:ssやss形式になっている場合には0埋めしてhh:mm:ssに修正した文字列を返す。
def time_reformatter(time_str: str) -> str:
    h = 0
    m = 0
    s = 0
    tmp = time_str.split(':')
    if len(tmp) == 1:
        s = int(tmp[0])
    elif len(tmp) == 2:
        m, s = map(int, tmp)
    elif len(tmp) == 3:
        h, m, s = map(int, tmp)
    else:
        print("Time paese error.")

    hhmmss_str = "{:0>2}:{:0>2}:{:0>2}".format(h, m, s)
    second_str = str(h * 3600 + m * 60 + s)

    return (hhmmss_str, second_str)


def add_timestamp_link(line: str, parent_url: str) -> str:
    """Markdownの歌リストに開始時間のURLを追加する"""

    split_space = line.split(' ', 2)  # 3回目以降の空白は分割しない
    (hhmmss_str, second_str) = time_reformatter(split_space[1])
    timestamp_url = parent_url + "&t=" + second_str + 's'

    # タイトルを取り出す。既に [title](timestamp_url) の形式になっている場合にも対応。
    title = ''
    match = re.search(r'\[(.*?)\]\((https?://[^\s)]+)\)', line)
    print(match)
    if match == (None, None) or match == None:
        title = split_space[2]
    else:
        title = match.group(1)

    new_line = "{} {} [{}]({})".format(split_space[0], hhmmss_str, title, timestamp_url)

    return new_line

# 実行
main()