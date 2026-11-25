#!/bin/sh
# 下载要写的字的笔顺数据（hanzi-writer-data，见 README 的许可一节）。用法：./get-hanzi.sh 年 想 你
mkdir -p hanzi
for c in "$@"; do
  curl -fsSL "https://cdn.jsdelivr.net/npm/hanzi-writer-data@2.0/$c.json" -o "hanzi/$c.json" && echo "ok $c"
done
