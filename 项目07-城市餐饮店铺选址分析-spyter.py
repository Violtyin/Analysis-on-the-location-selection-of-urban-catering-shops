# -*- coding: utf-8 -*-
"""
Created on Sun May 26 11:33:29 2019

@author: Administrator
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import warnings
warnings.filterwarnings('ignore')

#(1) 加载数据
os.chdir('D:\\工作\\数据分析学习\\数据分析师（网易）\\【代码+软件+课后答案】课程资料\\【非常重要】Python数据分析师微专业_课程资料\\CLASSDATA_ch06数据挖掘实战')
df = pd.read_excel('上海餐饮数据.xlsx',sheetname = 0,header = 0)
print('加载数据%i 条' %len(df))

# (2) 数据清洗 + 添加字段
# 删除空白值，取口味人均消费均大于0的值，增加字段
data = df[['类别','口味','环境','服务','人均消费']]
data.dropna(inplace=True)
data = data[(data['口味']>0)&(data['人均消费']>0)]
data['性价比'] = (df['口味'] + df['环境'] + df['服务'])/df['人均消费']
print('处理数据%i条' %len(data[(data['口味']<=0)|(data['人均消费']<=0)]))

# （3）处理异常值
def f2(data,col):
    s = data[col].describe()     # 要是没有这一步的话，新版会报错（摊手）
    q1 = s['25%']
    q3 = s['75%']
    iqr = q3 - q1
    mi = q1 - 1.5 * iqr
    ma = q3 + 1.5 * iqr
#     data_e = data[(data[col] >= mi)&(data[col] <= ma)][['类别','服务']]
    return data[(data[col] >= mi)&(data[col] <= ma)][['类别','服务']]

# 做一次异常值清洗过后，其实还会有异常值，。。。一直都有异常值的
    
data_kw = f2(data, '口味')
data_rj = f2(data,'人均消费')
data_xjb = f2(data,'性价比')

# （4）分组——均值——标准化 
data = data.groupby('类别').mean()
data['口味_norm'] = (data['口味'] - data['口味'].min() )/ (data['口味'].max()-data['口味'].min())
data['性价比_norm'] = (data['性价比'] - data['性价比'].min() )/ (data['性价比'].max()-data['性价比'].min())
data['人均消费_norm'] = (data['人均消费'] - data['人均消费'].min() )/ (data['人均消费'].max()-data['人均消费'].min())
data_final_q = data[['口味','口味_norm','性价比','性价比_norm','人均消费','人均消费_norm']]
#print(data_final_q)

# （5）开始以图做参考

from bokeh.layouts import gridplot
from bokeh.plotting import figure, show, output_file
from bokeh.models import ColumnDataSource
# 添加Tool工具、十字标线
from bokeh.models import HoverTool
from bokeh.models.annotations import BoxAnnotation

output_file('project07_h1,html')
data_final_q['size'] = data_final_q['口味_norm']*40    # 乘以40，只是为了让数字本省扩大一点
data_final_q.index.name = 'type'
data_final_q.columns = ['kw','kw_norm','xjb','xjb_norm','price','price_norm','size']
#print(data_final_q)


source = ColumnDataSource(data_final_q)   #创建数据
hover = HoverTool(tooltips =[('餐饮类型','@type'),
                             ('人均消费','@price'),
                             ('性价比得分','@xjb_norm'),
                             ('口味得分','@kw_norm')])  # 把Tools加到result、kw、price上
    
# 散点图
result = figure(plot_width = 800,
                plot_height = 300,
                title = '餐饮类型得分',
                x_axis_label = '人均消费',
                y_axis_label = '性价比得分',
                tools=[hover,'box_select,reset,xwheel_zoom,pan,crosshair'])
result.circle(x= 'price' ,
              y = 'xjb_norm',
              source = source, 
              line_color = 'black',
              line_dash = [6,4],
              fill_alpha = 0.6 ,
              size = 'size')

# 柱状图1
data_type = data_final_q.index.tolist()     # 因为呈现的横坐标为文字，所以先要将index转化成list

kw = figure(plot_width = 800,
            plot_height = 300,
            title = '餐饮类型得分',
            x_range = data_type,tools=[hover,'box_select,reset,xwheel_zoom,pan,crosshair'])
kw.vbar(x = 'type',top = 'kw_norm',source = source,width = 0.8,alpha = 0.7,color = 'red')

# 柱状图2
price = figure(plot_width = 800,
               plot_height = 300,
               title = '人均消费得分',
               x_range = data_type,
               tools=[hover,'box_select,reset,xwheel_zoom,pan,crosshair'])
price.vbar(x = 'type',top = 'price_norm',source = source,width = 0.8,alpha = 0.7,color = 'green')

p = gridplot([[result],[kw],[price]])
show(p)
print('Yes,you have done!)