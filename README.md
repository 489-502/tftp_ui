# tftp_ui
tftp tool for ecid
获取ecid tftp监测数据并图形化显示

[//]: # (Image References)
[image1]: ./images/layout.png
[image2]: ./images/visualization.png

## 预期读者
工具使用者、工具开发者

## 运行方式
### 可执行文件
直接双击dist目录下的main.exe即可运行程序。

### 源代码
在[anaconda](https://www.anaconda.com/download/#windows) python 2.7环境下，可在命令行中输入`python main.py`运行程序。

## 使用说明
1. 配置本机IP，与EIOCOM2 IP处于一个网段。

2. 打开程序，界面如下图所示：
![alt text][image1]

3. 输入EIOCOM2 IP，若可以`ping`通，继续；否则，先查网络问题。

4. 选择Rack机笼号、Slot槽道号、板卡类型、CPU、文件名。

5. 点击*fetch*，可获取相应文件；点击*fetch and show*，可获取相应文件并显示；点击*show*，可显示弹出对话框中选择的文件。

6. 图形化显示如下图所示：
![alt text][image2]

7. tftp消息头、版本消息、err消息直接显示在*Log*文本框中。

## 使用注意事项:
* 本工具目前仅支持PDDM5板卡
* PDDM5板卡的版本信息*ftp_vers*仅可通过CPUA获取。
* PDDM5板卡的道岔表示电压和电流信息*ftp_indi*、道岔驱动电压*ftp_volt*、道岔驱动电流*ftp_phase*仅可通过CPUB获取。
* PDDM5板卡的故障信息*ftp_err* CPUA和CPUB均可获取。
* 有问题联系：hetiantian@casco.com.cn

## 扩展其他板卡
### 文件结构

### How to do

## TODO
setup.py glob
