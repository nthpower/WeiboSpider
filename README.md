# 新浪微博爬虫
此开源项目是用Python3.6编写的新浪微博爬虫，包含登录与微博正文爬取功能，爬取后的资源保存在本地磁盘中。 感兴趣的朋友可在公众号ApeClub上找到对应代码的解读。
 
此项目诞生于本人Python的入门学习，也算是Python网络爬虫开发实战的第一步 ，希望志同道合的朋友们能一起从此开启Python爬虫，Python数据分析与机器学习实战之旅 

## 运行
运行前请使用下面命令安装依赖库
```shell
pip3 install -r requirement.txt
```

1. 通过修改[settings.py](/settings.py)文件中的ACCOUNT与PASSWORD来设置微博登录账号。
2. 通过修改[settings.py](/settings.py)文件中的SID来设置爬取的博主。

上面设置完毕后，可以在命令行中直接执行[main.py](/main.py)文件

```shell
./main.py
```
或
```shell
python3 main.py
```

## 保存文件目录
```shell
.
├── cookies
├── resource
│   ├──{sid}
│   │   ├──{time}
│   │   │   ├──image
│   │   │   └──title.txt
│   │   ├──{time}
│   │   │   ├──image
│   │   │   └──title.txt
│   │   └──{time}
│   │       ├──image
│   │       └──title.txt
│   ├──{sid}
│   │   ├──{time}
│   │   │   ├──image
│   │   │   └──title.txt
│   │   ├──{time}
│   │   │   ├──image
│   │   │   └──title.txt
│   │   └──{time}
│   │       ├──image
│   │       └──title.txt
...
```

## 参考资料
1. 《Python 3网络爬虫开发实战》 崔庆才 著 


---
更多技术咨询请关注我们的公众号平台，微信搜索ApeClub，或扫描下方二维码
![](images/apeclub.jpg)