# -*- coding: utf-8 -*-
"""
Created on Thu Oct 27 17:08:12 2022

@author: tomls
"""

import random
import numpy as np
from DGHedging import DGHedging
import matplotlib.pyplot as plt

random.seed(123)
#Assume one year is 252 days, so we use 0.25 year as 63 days.
#T,S0,sigma,mu,rf
#random.seed(100)

K = 100
T = 0.25
S0 = 100
sigma = 0.2
mu = 0.1
rf = 0.02
N = 91
semiband = 0.05


#Q1 Time-based Hedging
'''
money_account = 0
final_pnl = []

for i in range(10000):
    basemodel = DGHedging(T,S0,sigma,mu,rf,N)
    St = basemodel.StockPriceSim()

    pre_delta = 0
    money_account = 0
    
    for k in range(len(St)-1):
        if k == 0:
            pre_delta = basemodel.putDelta(S0, 0)
            money_account = - pre_delta * S0 + basemodel.putPrice(S0, 0) 
        else:
            current_delta = basemodel.putDelta(St[k], k*T/(len(St)-1))
            change_delta = current_delta - pre_delta
            money_account = basemodel.getBankReturn(money_account,1) - change_delta * St[k] - basemodel.transactionfee(change_delta, 0)
            pre_delta = current_delta

    if St[-1] < K:
        money_account = money_account + current_delta * St[-1] + (-K + St[-1]) - basemodel.transactionfee(current_delta, 0)
    else:
        money_account = money_account + current_delta * St[-1] - basemodel.transactionfee(current_delta, 0)

    final_pnl.append(money_account * np.exp(-rf * 0.25))
    print(i)

plt.hist(final_pnl,bins=20)
'''

#Q1 Move-based Hedging
money_account = 0
final_pnl = []

for i in range(10000):
    basemodel = DGHedging(T,S0,sigma,mu,rf,N)
    St = basemodel.StockPriceSim()

    pre_delta = 0
    money_account = 0
    upper_band = 0
    lower_band = 0
    interest_days = 0
    for k in range(len(St)-1):
        interest_days += 1
        if k == 0:
            pre_delta = basemodel.putDelta(S0, 0)
            money_account = - pre_delta * S0 + basemodel.putPrice(S0, 0) 
            upper_band = pre_delta + semiband
            lower_band = pre_delta - semiband
        
        else:
            current_delta = basemodel.putDelta(St[k], k*T/(len(St)-1))

            if current_delta > upper_band:
                change_delta = current_delta - pre_delta
                money_account = basemodel.getBankReturn(money_account,interest_days) - change_delta * St[k] - basemodel.transactionfee(change_delta, 0)
                pre_delta = current_delta
                upper_band = current_delta + semiband
                lower_band = current_delta - semiband
                if upper_band > -0.01 and current_delta < -0.01:
                    upper_band = -0.01
                elif current_delta > -0.01:
                    upper_band = 0
                    lower_band = -0.01
                elif lower_band < -0.99 and current_delta > -0.99:
                    lower_band = -0.99
                elif current_delta < -0.99:
                    upper_band = -0.99
                    lower_band = -1
                interest_days = 0
    
                    
            elif current_delta < lower_band:
                change_delta = current_delta - pre_delta
                money_account = basemodel.getBankReturn(money_account,interest_days) - change_delta * St[k] - basemodel.transactionfee(change_delta, 0)
                pre_delta = current_delta
                upper_band = current_delta + semiband
                lower_band = current_delta - semiband
                if upper_band > -0.01 and current_delta < -0.01:
                    upper_band = -0.01
                elif current_delta > -0.01:
                    upper_band = 0
                    lower_band = -0.01
                elif lower_band < -0.99 and current_delta > -0.99:
                    lower_band = -0.99
                elif current_delta < -0.99:
                    upper_band = -0.99
                    lower_band = -1
                interest_days = 0


    if St[-1] < K:
        money_account = money_account + current_delta * St[-1] + (-K + St[-1]) - basemodel.transactionfee(current_delta, 0)
    else:
        money_account = money_account + current_delta * St[-1] - basemodel.transactionfee(current_delta, 0)

    final_pnl.append(money_account*np.exp(-rf * 0.25))
    if np.abs(money_account) > 2:
        print(current_delta,St[-1],money_account,i,k)

plt.hist(final_pnl,bins=20)



print(basemodel.clientCharge(basemodel.cVar(final_pnl)))


#Q2
