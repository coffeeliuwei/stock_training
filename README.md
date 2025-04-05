# Tushare数据可视化实训项目

## 项目概述

本实训项目旨在帮助学生掌握使用Tushare API获取金融数据，并利用Python进行数据可视化的技能。通过本项目，学生将学习如何获取股票数据、绘制K线图，以及计算和展示常用技术指标。

## 学习目标

1. 了解并使用Tushare API获取股票数据
2. 学习数据处理和清洗技术
3. 掌握K线图绘制方法
4. 学习计算和可视化常用技术指标（如MACD、RSI、KDJ等）
5. 开发简单的股票数据分析工具

## 项目结构

```
stock_training/
├── README.md                 # 项目说明文档
├── requirements.txt          # 项目依赖
├── config.py                 # 配置文件
├── data_fetcher.py           # 数据获取模块
├── data_processor.py         # 数据处理模块
├── visualization.py          # 可视化模块
├── indicators.py             # 技术指标计算模块
└── main.py                   # 主程序入口
```

## 实训内容

### 第一阶段：数据获取与处理

1. 学习Tushare API的使用方法
2. 获取股票基本信息和日K线数据
3. 数据清洗与预处理

### 第二阶段：K线图绘制

1. 学习使用matplotlib和mplfinance绘制K线图
2. 实现基本K线图的绘制
3. 添加成交量显示

### 第三阶段：技术指标计算与可视化

1. 学习常用技术指标的计算方法
2. 实现MACD、RSI、KDJ等指标的计算
3. 将技术指标添加到K线图中

### 第四阶段：综合应用

1. 开发一个完整的股票数据分析工具
2. 实现多种图表和指标的组合显示
3. 添加简单的数据分析功能

## 技术要求

- Python 3.7+
- pandas
- numpy
- matplotlib
- mplfinance
- tushare

## 评估标准

1. 数据获取的完整性和准确性
2. K线图的美观度和信息展示
3. 技术指标计算的准确性
4. 代码的可读性和可维护性
5. 项目文档的完整性

## 命令行使用
pip install -r e:\tushare\stock_training\requirements.txt
python e:\tushare\stock_training\main.py --fetch --code 000001.SZ
python e:\tushare\stock_training\example.py