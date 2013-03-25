import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

import math
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# test
# from hw1 import optimize
# import datetime as dt
# optimize(dt.datetime(2011,1,1), dt.datetime(2011,12,31), ['AAPL', 'GLD', 'GOOG', 'XOM'])
# optimize(dt.datetime(2010,1,1), dt.datetime(2010,12,31), ['AXP', 'HPQ', 'IBM', 'HNZ'])

def simulate(startdate, enddate, equities, allocation, data_object):
    ls_port_syms = equities
    lf_port_alloc = allocation

    c_dataobj = data_object
    ls_all_syms = c_dataobj.get_all_symbols()
    ls_bad_syms = list(set(ls_port_syms) - set(ls_all_syms))
    if len(ls_bad_syms) != 0:
        print "Portfolio contains bad symbols : ", ls_bad_syms
    for s_sym in ls_bad_syms:
        i_index = ls_port_syms.index(s_sym)
        ls_port_syms.pop(i_index)
        lf_port_alloc.pop(i_index)

    dt_start = startdate
    dt_end = enddate
    dt_timeofday = dt.timedelta(hours=16)
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)

    ls_keys = ['close']

    ldf_data = c_dataobj.get_data(ldt_timestamps, ls_port_syms, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    na_price = d_data['close'].values
    na_normalized_price = na_price / na_price[0,:]

    na_normalized_price_w_allocs = na_normalized_price * lf_port_alloc

    na_total_port = na_normalized_price_w_allocs.cumsum(axis=1)[:,3]

    na_rets = na_total_port.copy()
    tsu.returnize0(na_rets)

    std_of_daily_returns = na_rets.std()

    avg_daily_returns = na_rets.mean()

    sharpe_ratio = math.sqrt(252) * avg_daily_returns/std_of_daily_returns

    cum_return = na_total_port[len(ldt_timestamps)-1]

    return std_of_daily_returns, avg_daily_returns, sharpe_ratio, cum_return

def optimize(startdate, enddate, equities):

    c_dataobj = da.DataAccess('Yahoo', cachestalltime=0)

    best_alloc = [0,0,0,0]
    best_sharpe = 0
    best_vol = None
    best_avg_daily_ret = None
    best_cum_ret = None
    
    lst = [0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]
    possible_allocs = []
    for a in lst:
        for b in lst:
            for c in lst:
                for d in lst:
                    possible_allocs.append([a,b,c,d])
    for alloc in possible_allocs:
        if alloc[1]==0.0 and alloc[2]==0.0 and alloc[3]==0.0:
            print str(alloc[0] * 100)+" percentish done"
        if sum(alloc) != 1.0:
            continue
        vol, daily_ret, sharpe, cum_ret = simulate(startdate, enddate, equities, alloc, c_dataobj)
        if sharpe > best_sharpe:
            best_sharpe = sharpe
            best_alloc = alloc
            best_vol = vol
            best_avg_daily_ret = daily_ret
            best_cum_ret = cum_ret

    print 'Start Date: '+startdate.strftime('%B %d, %Y')
    print 'End Date: '+enddate.strftime('%B %d, %Y')
    print 'Symbols: '+str(equities)
    print 'Optimal Allocations: '+str(best_alloc)
    print 'Sharpe Ratio: '+str(best_sharpe)
    print 'Volatility (stdev of daily returns): '+str(best_vol)
    print 'Average Daily Return: '+str(best_avg_daily_ret)
    print 'Cumulative Return: '+str(best_cum_ret)
