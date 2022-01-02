

# 目的

1.佳明码表不支持erg、mrc或者zwo格式的课程文件，只支持fit文件。所以很多课程文件不能直接应用到佳明码表上，略显鸡肋。

2.佳明Connect的课程编辑不支持FTP的百分比设置,但是很多课程都是根据FTP的百分比来的，所以这些课程需要转换成具体功率数值，且需要在Connect上新建课程。

所以，为了解决以上问题，本项目孕育而生。

# 功能
v1.0（2022.1.3）

1. 支持将本地erg文件转换并导入到佳明Connect,且佳明码表可直接使用
2. 支持erg课程文件由FTP百分比设置、具体功率设置
3. 支持佳明账号（目前只支持海外账号）登录

# 使用方式

## 转化并导入
```
> git clone https://github.com/lsy1072915121/fitlek.git
> cd fitlek
> python3 ./cli.py --file-path=./MyCathySpeical.erg --ftp=250 --username="your account name" --password="your password"
```

## 佳明Connect

erg课程文件

![workout](http://media.liushiyao.top/picgo/20220103011118.png)

Connect App

![workout](http://media.liushiyao.top/picgo/ConnectApp.jpeg)

佳明码表

![]()（码表不在身边，后补）


# 感谢

- 登录模块和佳明课程格式是基于 [fitlek](https://github.com/sesh/fitlek.git) 开发(虽然一开始测试的时候，这个登录模块并不可用，后来顺手把登录方式优化更新了)。不管怎样，为了表示感谢，项目沿用之前的名字。

# 最后

- 欢迎广大骑友使用，并提供宝贵意见🚴🏻⛰