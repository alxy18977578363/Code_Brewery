1. 准备内容
python 版本`3.11`, 相关库：`pandas`, `numpy`, `matplotlib`, `kears`, `tensorflow`

2. 数据集
`cleaned_mobike_shanghai_sample.csv`和`天气.csv`，自行车数据太大了，去https://www.heywhale.com/mw/dataset/5d315ebbcf76a60036e565bf/content下载

3. 数据集的清洗
run `原数据to清洗数据.py`,并用`清洗数据模型化.py`将数据变成模型需要的格式。

4. 数据分析
run `数据分析.py`,可以生成小提琴图和上海坐标热力图。

5. 模型训练,进行预测
run `cg.py`，跑cnn-LSTM-Attention的混合模型

6. 蚁群的调度优化
先用`聚类.py`将调度中心聚类出来，结果保存在`station_centers.csv`。然后即可使用`蚁群.py`，输入一个特定的时间，就可以跑得四个周期的结果。利用`蚁群敏感度分析.py`跑得敏感度的具体值，认为填到`敏感度可视化.py`中就可以得到蚁群优化的结果。

7. 可惜的结果
`FCM.py`本来是用FCM进行三等地区的聚类，甚至用到了时间上的稳态聚类中心去得到空间上的聚类中心，可是这和这次的调度后面因为不相关，于是弃用了。

很惊险的一次比赛，下午六点结赛，结果我三点多才挤进去交上，而且没赶上龙舟课。