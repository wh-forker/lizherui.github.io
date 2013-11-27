Date: 2013-11-27
Title: 局部缓存的应用
Category: Tech
Tags: esi, 缓存
Slug: esi

##源起
* * *
一般来讲，各个网站对页面做的缓存都是整体缓存，用户发请求的时候，缓存服务器会返回整个页面。

于是每次上线新版本的时候，我们都需要清除全部缓存才能使新版本立即生效。

在平时，这样没有任何问题。

但是在一些特殊的场景下，比如天猫双十一的当天，面对那种规模的流量，没有任何人敢清除全部的缓存。而这个时候突然来了一个非常紧急且需要立即生效的上线需求，我们该怎么办？

再比如页面中有一些定时变动的部分，比如活动相关的页面片段。总不能每次到了新活动的时间都需要我们手动清除线上缓存吧？

所以，将整体缓存切割成局部缓存势在必行，这意味着低风险和自动化。

最近我参与了这个缓存局部化的项目，感觉挺有意思，也有所收获。

##技术
* * *
局部缓存主要用的是ESI技术，是一种标记语言。

为了方便叙述，我们定义缓存服务器的名字叫Swift(类似开源界的Varnish，可处理ESI标签)，定义web应用叫malldetail。

ESI，即Edge Side Includes，是一种数据缓冲/缓存服务器，它提供将Web网页的部分（这里指页面的片段）进行缓冲/缓存的技术及服务。
详见[Wikipedia](http://en.wikipedia.org/wiki/Edge_Side_Includes)。

ESI标签由Swift负责解析回源，并且Swift会对ESI请求做缓存，并且提供如下特性：
* 需要定时做全站变更的页面模块用ESI的include实现，时间判断放在应用服务器处理回源请求的时候。* 回源以后，应用服务器可设置缓存失效的时间。* Swift提供合并回源，不会重复回源，防止失效后的高并发回源给应用服务器带来冲击。* Swift在ESI的缓存失效后回源，回源的请求处理期间不会挂起外部请求，会继续向客户端返回老版本的页面，回源请求处理完以后更新成新版本。类似copy on write，防止回源请求挂起导致前端服务器挂起。* ESI回源时对response header的操作不会发到客户端。

一个ESI的模块处理过程如下图：

![1](https://lh3.googleusercontent.com/-dquEAiu6EhU/UpMGaPl3_WI/AAAAAAAAAVU/WFTeL1Y0U4Q/s336/esi.png)

完整步骤如下：

* 在Malldetail首次被访问到的时候，在页面上生成带ESI标签的页面。       > ESI标签在Malldetail返回给Swift服务器的页面中，但是不被包含在最终页面中。    
   
   > ESI请求和当前的Malldetail页面的请求是两个请求，不能共用上下文。
      > ESI请求是一个单独的http请求，其中用到的参数和上下文信息需要在Malldetail页面渲染的时候加到ESI请求的URL中。* Swift服务器拿到页面后会进行ESI标签的解析，解析完成后向Malldetail服务器发送单独的ESI请求，并且将响应结果放在页面上。* Malldetail处理ESI请求：   > 根据参数处理业务逻辑。   > 设置此ESI模块的失效时间。   > ESI请求对response header的处理不会发送到客户端浏览器。* Swift缓存ESI结果，在失效时间到之前命中缓存。

##应用
* * *
###把模板中对风险敏感的变量ESI化

模板指的是velocity或jsp，由于没有改动java，所以上线的过程中不会发生编译，直接对velocity/jsp这样的静态文件做替换就能生效。

我们定义只修改模板并上线的形式叫模板发布，既修改模板又修改java文件的上线叫全量发布。

以版本号为例，模板中有一个变量代表css/js的版本号，比如1.0，1.1之类的数字。

我们把原来直接输出版本号的地方变成esi标签的形式，比如原先的形式是：

    assetsVersion = 1.0

修改成

    assetsVersion = <!--esi <esi:include src="/esi/esiAssets.htm?assetsVersionInEsi=1.0"/> -->     然后写对应esiAssets.java和esiAssets.vm(esiAssets.jsp也行)，直接输出1.0。模板发布的整个流程如下：

1. 开发/前端升级版本号assetsVersion并模板发布
2. PE清除线上assetsVersion对应的esi局部缓存
3. 失效后swift回源到malldetail，走assets的esi流程 
4. assets的esi走流程到模板渲染时，取本地的esi版本号完成渲染并返回
5. swift拿到新版本assets的渲染结果拼接页面并返回，同时缓存新版本assets。

如此以来，修改模板并上线后，只需要清除esi局部缓存，就能生效。

不过这样存在一个问题，若修改java文件进行全量发布时，会发生下图的异常情况：

![2](https://lh6.googleusercontent.com/-eiLJKhwtBo0/Uo3FbLIYWXI/AAAAAAAAAUc/om8szAMzow8/s757/Screen%2520Shot%25202013-11-21%2520at%252016.32.59.png)

如果老版本的malldetail和新的assets版本号不相互兼容，就会在全量发布的时候出问题。

为了解决这个问题，我们可以添加一个用来校正的vmVesion版本号，并添加进assets esi的uri参数中，比如
    
    assetsVersion = <!--esi <esi:include src="/esi/esiAssets.htm?assetsVersionInEsi=1.0&vmVersionInEsi=1.0.0"/> -->   

assets的esi流程走到模板渲染时，判断esi参数中的vmVersion版本号和本地vmVersion是否一致。如果一致，则返回本地assets版本号的渲染结果；否则返回esi中assets版本号的渲染结果, 如下图：

![3](https://lh6.googleusercontent.com/-9hAfPlw4jFc/Uo3Hfw3x6eI/AAAAAAAAAVA/ZMjwK49BHMM/s767/Screen%2520Shot%25202013-11-21%2520at%252016.41.37.png)

反之亦然。

问题解决。

###把定时变动的部分ESI化

现在页面中有一个片段负责展现活动页面，这个活动页面有一批定时活动，比如8点-9点展现活动1，9点30分-10点展现活动2，11点-12点展现活动3。

ESI有一个功能是可以为某个局部缓存单独设置失效的时间，将它从整体缓存中剥离了出来。

这个问题可以抽象成下图，有3个活动，逆序表示，即在时间上E3>S3>E2>S2>E1>S1：

    * 偶数序号为结束时间EndTime
	* 奇数序号为开始时间StartTime
	* noew代表当前时间
	* |----|           |----|          |----|
	* E3   S3   null   E2   S2   null  E1   S1
	* a)如果now > E3 banner: null cache-control:very long
	* b)如果now > S3 banner: 命中某活动，返回相应页面片段 cache-control:E3-now
	* c)如果now > E2 banner: null cache-control:S3-now
	* d)如果now < S1 banner: null cache-control:S1-now

我们只要按照上图的逻辑设置esi回源的失效时间(设置http response header里的Catch-Control)，即可达到自动化的目的。

##总结
* * *
局部缓存技术的应用场景目前还不是很多，往往都是在一些苛刻的情况下才需要它。

不过这并不重要，重要的是我们需要对低风险和自动化始终保持极限的追求。












