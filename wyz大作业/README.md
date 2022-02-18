### 实验任务

>请同学们在整理了 CVPR 2021 、 CVPR 2020 和 CVPR 2019 全部发表论文的网页中（网页链接下附），利用 python 编写爬虫，逐年爬取论文题目中含某些关键词的全部文章题目（关键词下附），并实现利用 python ，将爬取到的论文题目逐行自动存储在一个 Excel 文件中，**每年一个表格**，同时输出显示含**该关键词**的**每年论文数量**。与此同时，各位还需要编程统计含这些关键词文章题目中其他单词的**出现频率**，并从高到低排列，输出到 txt 文档中，每一行包含一个单词以及该单词对应的频数（因为这些高频出现的单词，往往代表作者使用的技术，如，含 domain adaptation 关键词的文章，也许会同时经常出现关键词 clustering ，即代表学者们在某一年常用聚类思想解决域自适应问题，这代表了学者们使用的前沿技术，有利于各位在科研时确定自己的调研方向），注意，高频关键词需要排除掉 a、an、the、of、for、in、on 等无实际意义的量词介词等。最后，通过词云进行可视化。
>
>- 注意：
>
>所需爬取的关键词每个人不同，各位同学需要根据自己学号2020212×××中的最后一位数字，爬取对应关键词，注意，不区分大小写，比如对于Object Detection，Object Detection、object detection和Object detection等，均需要爬取出来。
>
>- 爬取网页：
>
>​       CVPR 2021：https://dblp.uni-trier.de/db/conf/cvpr/cvpr2021.html
>
>​        CVPR 2020：https://dblp.uni-trier.de/db/conf/cvpr/cvpr2020.html
>
>​       CVPR 2019：https://dblp.uni-trier.de/db/conf/cvpr/cvpr2019.html
>
>- 关键词：
>
> object detection

### 实验步骤

首先分析目标网站，发现需要的信息就在网站的源代码里面，如下图所示：

![image-20220110102610679](https://gitee.com/ceyewan/pic/raw/master/images/image-20220110102610679.png)

我们发现所有的标题都是  `itemprop="name">(标题)</span>` 的格式，因此可以用正则表达式匹配标题，`re.S` 表示忽略换行：

```python
# 正则表达式匹配所有的标题
obj = re.compile(r'itemprop="name">.*?</span>', re.S)
```

上面虽然会匹配到非标题内容，不过因为我们还会有一个 judge 函数，所以不用管。因此，我们就可以编写爬虫了。用requests爬取内容后，正则表达式匹配所有的标题，逐年写入文件。标题我们先需要切片，去除正则表达式获得的内容中的 `itemprop="name">` 和 `</span>`，判断是否含有我们需要的关键词。计数并且写入文件，最后再写入符合要求的标题的数量。

```python
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
```

我们的 `judge` 函数需要区分大小写判断是否含有关键词 `Object Detection`，先全部小写然后利用内置方法 `find` 查找是否含有 `object detection`:

```python
def judge_title_have_target_word(ans):
    """ 判断 ans 中是否含有 object detection """
    # 区分大小写，所以先都转化成小写
    temp = ans.lower()
    # 如果 temp 中找到了 object detection
    if temp.find("object detection") >= 0:
        return True
    else:
        return False
```

此时我们得到了三个文件，展示 2019 年的如下，我们可以看到该年共计有 43 篇论文含有关键词。

![image-20220110104414772](https://gitee.com/ceyewan/pic/raw/master/images/image-20220110104414772.png)

接下来，我们统计高频词。依次读取三个文件，将标题添加到 `wordlist` 字符串中，因为文件中还有一行说明论文数量的，那一行我们跳过。然后将标点符号全部删除，转换成小写（我们认为大写和小写是同一个词，统计词频不能区分开），然后用  `split`  方法将字符串转换成列表，用 `count` 方法统计出现的次数。将次数和单词写入字典，并且删除无效词，最后按照词频排序，写入文件。这里我们只写入前 20 个高频词。这里我们将得到的 `wordlist` 作为 `ciyun_words ` 返回，用于后续词云制作。

```python
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
```

我们得到的高频词如下：

![image-20220110110125097](https://gitee.com/ceyewan/pic/raw/master/images/image-20220110110125097.png)

最后一步，生成词云可视化。就是把参数填入即可。

这里我选择的图片是（主要是因为这张图片有清晰的轮廓）：

![yyqx](https://gitee.com/ceyewan/pic/raw/master/images/yyqx.jpg)

```python
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
        mask=img                    # 背景图片
    )
    # 根据文本数据生成词云
    wc.generate(ciyun_words)
    # 保存词云文件
    wc.to_file('ciyun.jpg')
```

最后我们得到的词云图片是：

![ciyun](https://gitee.com/ceyewan/pic/raw/master/images/ciyun.jpg)

### 完整代码如下：

```python
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
        mask=img                    # 背景图片
    )
    # 根据文本数据生成词云
    wc.generate(ciyun_words)
    # 保存词云文件
    wc.to_file('ciyun.jpg')


def main():
    """ 主函数 """
    get_target_titles_to_csv()
    ciyun_words = get_high_frequency_words()
    generate_word_cloud(ciyun_words)


# 函数入口
if __name__ == "__main__":
    main()
```

