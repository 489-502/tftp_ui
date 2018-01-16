# tftp_ui
tftp tool for ecid  
获取ecid tftp监测数据并图形化显示

[//]: # (Image References)
[image1]: ./images/layout.png
[image2]: ./images/visualization.png

## 预期读者
工具使用者、开发者

## 运行方式
### 可执行文件
直接双击dist目录下的main.exe即可运行程序。

### 源代码
在[anaconda](https://www.anaconda.com/download/#windows) python 2.7环境下，可在命令行中输入`python main.py`运行程序。

## 使用说明
1. 配置本机IP，与EIOCOM2 IP处于一个网段。

2. 打开程序，界面如下图所示：

 ![alt text][layout]

 [layout]: ./images/layout.png "layout"

3. 输入EIOCOM2 IP，若可以`ping`通，继续；否则，先查网络问题。

4. 选择Rack机笼号、Slot槽道号、板卡类型、CPU、文件名。

   Slot No定义参见附录。

5. 点击*fetch*，可获取相应文件；点击*fetch and show*，可获取相应文件并显示；点击*show*，可显示弹出对话框中选择的文件。

6. 图形化显示如下图所示：

 ![alt text][indication power and current]

 [indication power and current]: ./images/visualization.png "indication power and current"

7. tftp消息头、版本消息、err消息直接显示在*Log*文本框中。

## 使用注意事项:
* 本工具目前仅支持PDDM5板卡。
* PDDM5板卡的监测信息：

| 监测信息 | 文件名 | CPU |
| - | - | - |
| 版本信息 | ftp_vers | CPUA |
| 道岔表示电压和电流信息 | ftp_indi | CPUB |
| 道岔驱动电压 | ftp_volt | CPUB |
| 道岔驱动电流 | ftp_phase | CPUB |
| 故障信息 | ftp_err | CPUA or CPUB |

* 使用前请关闭防火墙。
* 有问题联系：hetiantian@casco.com.cn

## 扩展其他板卡

### 文件结构视图
* base
  * __init__.py
  * basedevice.py
  * xmlparser.py
  * loglog.py
  * tftplib.py
  * cop.py
* guest
  * pddm5.py 
* config
  * pddm5_message.xml
* log
  * pddm5.log
* main.py
* ui.py
* setup.py

### 静态类视图
TODO

### How to do
1. 安装[anaconda](https://www.anaconda.com/download/#windows) python 2.7环境
2. 在guest目录下增加`guest.py`文件，主要为创建用于各个tftp文件解析的函数, **大头在这**
3. 在config目录下增加`guest_message.xml`文件，描述需要解析的消息，不含消息头
4. 在log目录下增加`guest.log`文件
5. 在`main.py`中所有`TODO`处根据注释添加板卡相关代码，包括板卡类型、实例化、信号/槽道绑定、板卡相关tftp文件名
6. 在命令行中type `python main.py`可调试运行

### 生成可执行文件
基于py2exe实现程序打包，可在不含python的机器中运行。 
1. Type "python setup.py py2exe" in the command line to generate exe file in the `dist` folder.
2. Add mkl_*.dll and libiomp5md.dll into the dist folder.
3. Add config, log and platforms into the dist folder.

### 注意事项
支持Windows XP or Win7

## TODO
setup.py glob

## 附录
* 有轨电车机架图
