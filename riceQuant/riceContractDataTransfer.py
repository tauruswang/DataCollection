# -*- coding: utf-8 -*-

import time
import pandas as pd
from datetime import datetime
import os


# 时间格式转换
def getEndutc(ricedf):
    # print ricedf['Unnamed: 0']
    # 有些的时间列没有index 的列名，要使用'Unnamed: 0'
    return int(time.mktime(time.strptime(ricedf['Unnamed: 0'], '%Y-%m-%d %H:%M:%S')))


def getEndutcfor1d(ricedf):
    # print ricedf['Unnamed: 0']
    # 有些的时间列没有index 的列名，要使用'Unnamed: 0'
    return int(time.mktime(time.strptime(ricedf['Unnamed: 0'] + ' 00:00:00', '%Y-%m-%d %H:%M:%S')))


def getstrtime(ricedf):
    return datetime.fromtimestamp(ricedf['utc_time'], tz=None).strftime('%Y-%m-%d %H:%M:%S') + '+08:00'


def getstrendtime(ricedf):
    return datetime.fromtimestamp(ricedf['utc_endtime'], tz=None).strftime('%Y-%m-%d %H:%M:%S') + '+08:00'


# 2018-04-02：米筐数据转换
def riceToMyquant1m(symbollist, domain_symbol, enddate):
    rawfolder = ("riceToMyquant %s\\" % domain_symbol)
    #rawfolder = ("rqdata_raw_%s\\" % domain_symbol)
    bar_type = 60
    for symbol in symbollist:
        print('Processing %s of %s bartype%d enddate %s' % (symbol, domain_symbol, bar_type, enddate))
        filename = rawfolder + "%s_%s_1m.csv" % (symbol, enddate)
        #filename = rawfolder + "rqdata_raw_%s_of_%s_1m.csv" % (symbol, domain_symbol)
        exchange, sec = domain_symbol.split('.')
        ricedf = pd.read_csv(filename)
        ricedf['utc_endtime'] = ricedf.apply(lambda t: getEndutc(t), axis=1)
        ricedf['utc_time'] = ricedf['utc_endtime'] - bar_type
        ricedf['strtime'] = ricedf.apply(lambda t: getstrtime(t), axis=1)
        ricedf['strendtime'] = ricedf.apply(lambda t: getstrendtime(t), axis=1)
        myquantdf = pd.DataFrame()
        myquantdf['strtime'] = ricedf['strtime']
        myquantdf['strendtime'] = ricedf['strendtime']
        myquantdf['utc_time'] = ricedf['utc_time']
        myquantdf['utc_endtime'] = ricedf['utc_endtime']
        myquantdf['open'] = ricedf['open']
        myquantdf['high'] = ricedf['high']
        myquantdf['low'] = ricedf['low']
        myquantdf['close'] = ricedf['close']
        myquantdf['volume'] = ricedf['volume']
        myquantdf['amount'] = ricedf['total_turnover']
        myquantdf['position'] = ricedf['open_interest']
        myquantdf['limit_up'] = ricedf['limit_up']
        myquantdf['limit_down'] = ricedf['limit_down']
        myquantdf['adj_factor'] = 0
        myquantdf['pre_close'] = 0
        myquantdf['trading_date'] = ricedf['trading_date']
        myquantdf['exchange'] = exchange
        myquantdf['sec_id'] = sec
        myquantdf['symbol'] = symbol
        myquantdf['bar_type'] = bar_type
        tofilename = "%s %d_%s.csv" % (symbol, bar_type, enddate)
        myquantdf.to_csv("riceToMyquant " + domain_symbol + "\\" + tofilename, index=False)
        #myquantdf.to_csv(rawfolder + tofilename, index=False)


def transfer1mTo5m15m(symbollist, domain_symbol, enddate):
    """使用1m的数据生成5m和15m数据"""
    rawfolder = ("riceToMyquant %s\\" % domain_symbol)
    exchange, sec = domain_symbol.split('.')
    minlist = [5, 15]
    for min in minlist:
        bar_type = min * 60
        for symbol in symbollist:
            print('Processing %s bartype %d %s ' % (symbol, bar_type, enddate))
            fname = "%s 60_%s.csv" % (symbol, enddate)
            df1m = pd.read_csv(rawfolder + fname)
            barlist = []
            i = 0
            datalen = df1m.shape[0]
            while i < datalen:
                starti = i
                endi = i + min
                strtime = df1m.ix[starti]['strtime']
                strendtime = df1m.ix[endi - 1]['strendtime']
                utc_time = df1m.ix[starti]['utc_time']
                utc_endtime = df1m.ix[endi - 1]['utc_endtime']
                tradingdate = df1m.ix[starti]['trading_date']
                open = df1m.ix[starti]['open']
                high = df1m.iloc[starti:endi].high.max()
                low = df1m.iloc[starti:endi].low.min()
                close = df1m.ix[endi - 1]['close']
                volume = df1m.iloc[starti:endi].volume.sum()
                amount = df1m.iloc[starti:endi].amount.sum()
                position = df1m.ix[endi - 1]['position']
                limit_up = df1m.ix[starti]['limit_up']
                limit_down = df1m.ix[starti]['limit_down']
                barlist.append([strtime, strendtime, utc_time, utc_endtime, open, high, low, close, volume, amount, position, limit_up,
                                limit_down, 0, 0, tradingdate, exchange, sec, symbol, bar_type])
                i = endi
            df10m = pd.DataFrame(barlist,
                                 columns=['strtime', 'strendtime', 'utc_time', 'utc_endtime', 'open', 'high', 'low', 'close', 'volume', 'amount', 'position', 'limit_up',
                                          'limit_down', 'adj_factor', 'pre_close', 'trading_date', 'exchange', 'sec_id', 'symbol', 'bar_type'])
            tofname = "%s %d_%s.csv" % (symbol, bar_type, enddate)
            df10m.to_csv(rawfolder + tofname, index=False)
            pass


def transfer1mTo3m(symbollist, domain_symbol, enddate):
    """使用1m的数据生成3m数据"""
    rawfolder = ("riceToMyquant %s\\" % domain_symbol)
    exchange, sec = domain_symbol.split('.')
    minlist = [3]
    for min in minlist:
        bar_type = min * 60
        for symbol in symbollist:
            print('Processing %s bartype %d %s ' % (symbol, bar_type, enddate))
            fname = "%s 60_%s.csv" % (symbol, enddate)
            df1m = pd.read_csv(rawfolder + fname)
            barlist = []
            i = 0
            datalen = df1m.shape[0]
            while i < datalen:
                starti = i
                endi = i + min
                strtime = df1m.ix[starti]['strtime']
                strendtime = df1m.ix[endi - 1]['strendtime']
                utc_time = df1m.ix[starti]['utc_time']
                utc_endtime = df1m.ix[endi - 1]['utc_endtime']
                tradingdate = df1m.ix[starti]['trading_date']
                open = df1m.ix[starti]['open']
                high = df1m.iloc[starti:endi].high.max()
                low = df1m.iloc[starti:endi].low.min()
                close = df1m.ix[endi - 1]['close']
                volume = df1m.iloc[starti:endi].volume.sum()
                amount = df1m.iloc[starti:endi].amount.sum()
                position = df1m.ix[endi - 1]['position']
                limit_up = df1m.ix[starti]['limit_up']
                limit_down = df1m.ix[starti]['limit_down']
                barlist.append([strtime, strendtime, utc_time, utc_endtime, open, high, low, close, volume, amount, position, limit_up,
                                limit_down, 0, 0, tradingdate, exchange, sec, symbol, bar_type])
                i = endi
            df10m = pd.DataFrame(barlist,
                                 columns=['strtime', 'strendtime', 'utc_time', 'utc_endtime', 'open', 'high', 'low', 'close', 'volume', 'amount', 'position', 'limit_up',
                                          'limit_down', 'adj_factor', 'pre_close', 'trading_date', 'exchange', 'sec_id', 'symbol', 'bar_type'])
            tofname = "%s %d_%s.csv" % (symbol, bar_type, enddate)
            df10m.to_csv(rawfolder + tofname, index=False)
            pass


def transfer1mTo10m(symbollist, domain_symbol, enddate):
    """
    将ricequant转换成myquant后的1m数据，转换成10m的数据
    主要是解决14：55分的K线问题
    遍历时间，如果当前时间是下午14:55，则range=5，其他时候range=10
    """
    rawfolder = ("riceToMyquant %s\\" % domain_symbol)
    exchange, sec = domain_symbol.split('.')
    bar_type = 600
    for symbol in symbollist:
        print('Processing %s bartype %d %s ' % (symbol, bar_type, enddate))
        fname = "%s 60_%s.csv" % (symbol, enddate)
        df1m = pd.read_csv(rawfolder + fname)
        list10m = []
        i = 0
        datalen = df1m.shape[0]
        if exchange == 'CFFEX':
            aligtime = '15:15'
        else:
            aligtime = '14:55'
        while i < datalen:
            starti = i
            strtime = df1m.ix[starti]['strtime']
            if aligtime in strtime:
                range10m = 5
            else:
                range10m = 10
            endi = i + range10m
            strendtime = df1m.ix[endi - 1]['strendtime']
            utc_time = df1m.ix[starti]['utc_time']
            utc_endtime = df1m.ix[endi - 1]['utc_endtime']
            tradingdate = df1m.ix[starti]['trading_date']
            open = df1m.ix[starti]['open']
            high = df1m.iloc[starti:endi].high.max()
            low = df1m.iloc[starti:endi].low.min()
            close = df1m.ix[endi - 1]['close']
            volume = df1m.iloc[starti:endi].volume.sum()
            amount = df1m.iloc[starti:endi].amount.sum()
            position = df1m.ix[endi - 1]['position']
            limit_up = df1m.ix[starti]['limit_up']
            limit_down = df1m.ix[starti]['limit_down']
            list10m.append([strtime, strendtime, utc_time, utc_endtime, open, high, low, close, volume, amount, position, limit_up,
                            limit_down, 0, 0, tradingdate, exchange, sec, symbol, bar_type])
            i = endi
        df10m = pd.DataFrame(list10m, columns=['strtime', 'strendtime', 'utc_time', 'utc_endtime', 'open', 'high', 'low', 'close', 'volume', 'amount', 'position', 'limit_up',
                                               'limit_down', 'adj_factor', 'pre_close', 'trading_date', 'exchange', 'sec_id', 'symbol', 'bar_type'])
        tofname = "%s %d_%s.csv" % (symbol, bar_type, enddate)
        df10m.to_csv(rawfolder + tofname, index=False)


def transfer1mTo30m(symbollist, domain_symbol, enddate):
    """
    将ricequant转换成myquant后的1m数据，转换成10m的数据
    主要是解决14：55分的K线问题
    遍历时间，如果当前时间是下午14:45，则range=15，其他时候range=30
    CFFEX:直接30根对齐
    其他交易所：14:45对齐
    """
    rawfolder = ("riceToMyquant %s\\" % domain_symbol)
    exchange, sec = domain_symbol.split('.')
    bar_type = 1800
    for symbol in symbollist:
        print('Processing %s bartype %d %s ' % (symbol, bar_type, enddate))
        fname = "%s 60_%s.csv" % (symbol, enddate)
        df1m = pd.read_csv(rawfolder + fname)
        list30m = []
        i = 0
        datalen = df1m.shape[0]
        if exchange == 'CFFEX':
            aligtime = '15:15'
        else:
            aligtime = '14:45'
        while i < datalen:
            starti = i
            strtime = df1m.ix[starti]['strtime']
            if aligtime in strtime:
                range30m = 15
            else:
                range30m = 30
            endi = i + range30m
            strendtime = df1m.ix[endi - 1]['strendtime']
            utc_time = df1m.ix[starti]['utc_time']
            utc_endtime = df1m.ix[endi - 1]['utc_endtime']
            tradingdate = df1m.ix[starti]['trading_date']
            open = df1m.ix[starti]['open']
            high = df1m.iloc[starti:endi].high.max()
            low = df1m.iloc[starti:endi].low.min()
            close = df1m.ix[endi - 1]['close']
            volume = df1m.iloc[starti:endi].volume.sum()
            amount = df1m.iloc[starti:endi].amount.sum()
            position = df1m.ix[endi - 1]['position']
            limit_up = df1m.ix[starti]['limit_up']
            limit_down = df1m.ix[starti]['limit_down']
            list30m.append([strtime, strendtime, utc_time, utc_endtime, open, high, low, close, volume, amount, position, limit_up,
                            limit_down, 0, 0, tradingdate, exchange, sec, symbol, bar_type])
            i = endi
        df10m = pd.DataFrame(list30m, columns=['strtime', 'strendtime', 'utc_time', 'utc_endtime', 'open', 'high', 'low', 'close', 'volume', 'amount', 'position', 'limit_up',
                                               'limit_down', 'adj_factor', 'pre_close', 'trading_date', 'exchange', 'sec_id', 'symbol', 'bar_type'])
        tofname = "%s %d_%s.csv" % (symbol, bar_type, enddate)
        df10m.to_csv(rawfolder + tofname, index=False)


if __name__ == '__main__':
    os.chdir('D:\\002 MakeLive\DataCollection\\ricequant data\\')
    month_mode = False   # 为True表示是月度更新模式，则只更新该月涉及的合约
    if month_mode:
        startdate = '2018-06-01'
        enddate = '2018-07-01'
        domain_map = pd.read_excel('D:\\002 MakeLive\DataCollection\public data\\domainMap.xlsx')
        contract_map = pd.read_csv('D:\\002 MakeLive\DataCollection\public data\\contractMap.csv')
        active_domain_list = domain_map.loc[domain_map['active'] == True]['symbol'].tolist()
        start_utc = int(time.mktime(time.strptime(startdate + ' 00:00:00', '%Y-%m-%d %H:%M:%S')))
        for domain_symbol in active_domain_list:
            symbol_contract_map = contract_map.loc[contract_map['domain_symbol'] == domain_symbol]
            modify_symbol = symbol_contract_map.loc[(symbol_contract_map['domain_start_utc'] > start_utc) | (symbol_contract_map['domain_end_utc'] > start_utc)]
            idlist = modify_symbol['symbol'].tolist()
            riceToMyquant1m(idlist, domain_symbol, enddate)
            #transfer1mTo3m(idlist, domain_symbol, enddate)
            transfer1mTo5m15m(idlist, domain_symbol, enddate)
            transfer1mTo10m(idlist, domain_symbol, enddate)
            transfer1mTo30m(idlist, domain_symbol, enddate)
    else:
        symboldf = pd.read_csv('D:\\002 MakeLive\DataCollection\public data\\contractMap.csv')
        domain = 'SHFE.RB'
        enddate = '2018-08-20'
        rbdf = symboldf.loc[symboldf['domain_symbol'] == domain]
        #idlist = rbdf['symbol'].tolist()
        idlist = ['RB1901']
        riceToMyquant1m(idlist, domain, enddate)
        #transfer1mTo3m(idlist, domain, enddate)
        #transfer1mTo5m15m(idlist, domain, enddate)
        #transfer1mTo10m(idlist, domain, enddate)
        #transfer1mTo30m(idlist, domain, enddate)
