# -*- coding: utf-8 -*-
import re
import csv
import requests
from wordcloud import WordCloud
import cv2

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
}
# 正则表达式匹配所有的标题
obj = re.compile(
    r'itemprop="name">.*?</span>', re.S)


def judge_title_have_target_word(ans):
    """ 判断 ans 中是否含有 object detection """
    # 区分大小写，所以先都转化成小写
    temp = ans.lower()
    # 如果 temp 中找到了 object detection
    if temp.find("object detection") >= 0:
        return True
    else:
        return False


def get_target_titles_to_csv():
    """ 爬取含有关键词的标题写入文件 """
    for i in range(2019, 2022):
        # 获取url
        url = f"https://dblp.uni-trier.de/db/conf/cvpr/cvpr{i}.html"
        resp = requests.get(url, headers=headers)
        page_content = resp.text
        # 获取所有的标题
        result = obj.findall(page_content)
        f = open(f"{i}.csv", mode="w", encoding="utf-8", newline="")
        csvwriter = csv.writer(f)
        # 标题数量计数
        count = 0
        for it in result:
            # 预处理，删除边边角角
            ans = it[16:-7]
            # 如果含有关键词
            if judge_title_have_target_word(ans):
                # 数量加一，写入文件
                count += 1
                csvwriter.writerow([ans])
        # 最后输出含有关键词论文的数量
        csvwriter.writerow(["论文数量是:", count])


def get_high_frequency_words():
    """ 获取高频词 """
    wordlist = ""
    # 读取三个标题文件，将所有的标题写入 wordlist
    for i in range(2019, 2022):
        filename = str(i) + ".csv"
        with open(file=filename, mode="r", encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if row[0] == '论文数量是:':
                    pass
                else:
                    wordlist += " " + row[0][:-1]  # 去除最后的 .
    # 将 wordlist 中的标点全部删除
    wordlist = wordlist.replace(",", "").replace(".", "").replace(
        ":", "").replace(";", "").replace("?", "")
    # 用于后续制作词云
    ciyun_words = wordlist
    # 将 wordlist 转换成小写
    exchange = wordlist.lower()
    # 转换成列表
    split = exchange.split()
    # 统计词频并且写入字典
    dic = {}
    for i in split:
        count = split.count(i)
        dic[i] = count
    # 无效词
    word = ['and', 'the', 'with', 'in', 'by',
            'for', 'of', 'an', 'to', 'a']
    # 删除无效词
    for i in word:
        del(dic[i])
    # 按照词频排序
    dic1 = sorted(dic.items(), key=lambda d: d[1], reverse=True)
    # 将前 20 个高频词写入文件
    with open("high_frequency_words.txt", mode="w", encoding="utf-8", newline="") as f:
        for i in range(20):
            temp = str(dic1[i])
            f.write(temp[1:-1] + "\n")
    return ciyun_words


def generate_word_cloud(ciyun_words):
    """ 制作词云 """
    # 读取图片
    img = cv2.imread('yyqx.jpg')
    # 禁止词，词云中不能出现这些词
    stop_words = ['and', 'the', 'with', 'in', 'by',
                  'for', 'of', 'an', 'to', 'a']
    # 设置参数，创建 WordCloud 对象
    wc = WordCloud(
        background_color='white',   # 设置背景颜色为白色
        stopwords=stop_words,       # 设置禁止词
        mask=img,                    # 背景图片
        scale=2
    )
    # 根据文本数据生成词云
    wc.generate(ciyun_words)
    # 保存词云文件
    wc.to_file('ciyun.jpg')


def main():
    """ 主函数 """
    # get_target_titles_to_csv()
    ciyun_words = get_high_frequency_words()
    generate_word_cloud(ciyun_words)


# 函数入口
if __name__ == "__main__":
    main()
