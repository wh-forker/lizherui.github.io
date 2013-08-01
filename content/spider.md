Date: 2013-07-31
Title: 爬取校招信息
Category: Tech
Tags: python, 爬虫

抓取北邮人论坛和水木社区校招信息的爬虫程序, 直接运行main.py即可，非常简洁，可以扩展。

爬虫根据自定义关键字先对校招信息进行过滤，然后存储到本机redis中。本机若有lamp环境，可直接从redis读取信息到web页面上即可。

Talk is cheap, show you the code:<https://github.com/lizherui/spider_python>.

Enjoy it.

