# -*- coding: utf-8 -*-
"""
Created on Thu Oct 27 17:08:12 2022

@author: tomls
"""

import random
import numpy as np
from DGHedging import DGHedging
import matplotlib.pyplot as plt
from sklearn.neighbors import KernelDensity
import seaborn as sns
import pandas as pd

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

'''
#Q1 Delta Time-based Hedging

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
            money_account = - pre_delta * S0 + basemodel.putPrice(S0, 0) - basemodel.transactionfee(pre_delta, 0)
        else:
            current_delta = basemodel.putDelta(St[k], k*T/(len(St)-1))
            change_delta = current_delta - pre_delta
            money_account = basemodel.getBankReturn(money_account,1) - change_delta * St[k] - basemodel.transactionfee(change_delta, 0)
            pre_delta = current_delta

    if St[-1] < K:
        money_account = basemodel.getBankReturn(money_account,1) + current_delta * St[-1] + (-K + St[-1]) - basemodel.transactionfee(current_delta, 0)
    else:
        money_account = basemodel.getBankReturn(money_account,1) + current_delta * St[-1] - basemodel.transactionfee(current_delta, 0)

    final_pnl.append(money_account * np.exp(-rf * 0.25))
    print(i)

plt.hist(final_pnl,bins=50)
plt.title('Delta Time-based Hedging')
print(basemodel.clientCharge(basemodel.cVar(final_pnl)))
'''

'''
#Q1 Delta Move-based Hedging
money_account = 0
final_pnl = []
record = []

for i in range(10000):
    basemodel = DGHedging(T,S0,sigma,mu,rf,N)
    St = basemodel.StockPriceSim()    
    pre_delta = 0
    money_account = 0
    upper_band = 0
    lower_band = 0
    interest_days = 0
    current_delta = 0
    stock_position = 0
    flag = 0
    
    for k in range(len(St)-1):
        interest_days += 1
        if k == 0:
            pre_delta = basemodel.putDelta(S0, 0)
            stock_position = pre_delta
            money_account = - pre_delta * S0 + basemodel.putPrice(S0, 0) - basemodel.transactionfee(pre_delta, 0)
            upper_band = pre_delta + semiband
            lower_band = pre_delta - semiband
        else:
            current_delta = basemodel.putDelta(St[k], k*T/(len(St)-1))

            if (current_delta > upper_band or current_delta < lower_band):
                change_delta = current_delta - pre_delta
                stock_position = current_delta
                money_account = basemodel.getBankReturn(money_account,interest_days) - change_delta * St[k] - basemodel.transactionfee(change_delta, 0)
                pre_delta = current_delta
                upper_band = current_delta + semiband
                lower_band = current_delta - semiband
                interest_days = 0
                if upper_band > -0.01 and flag == 0:
                    upper_band = -0.01
                    flag = 1
                elif lower_band < -0.99 and flag == 0:
                    lower_band = -0.99
                    flag = 1
                if flag == 1 and (current_delta > upper_band or current_delta < lower_band):
                    flag = 0
            record.append(stock_position - current_delta)
    print(i)


    if St[-1] < K:
        money_account = basemodel.getBankReturn(money_account,1) + stock_position * St[-1] + (-K + St[-1]) - basemodel.transactionfee(stock_position, 0)
    else:
        money_account = basemodel.getBankReturn(money_account,1) + stock_position * St[-1] - basemodel.transactionfee(stock_position, 0)

    final_pnl.append(money_account*np.exp(-rf * 0.25))

plt.hist(final_pnl,bins=50)
plt.title('Delta Move-based Hedging')
print(basemodel.clientCharge(basemodel.cVar(final_pnl)))
'''

'''
#Q2 Delta-Gamma time based Hedging 
money_account = 0
final_pnl = []

temp = []

for i in range(10000):
    basemodel = DGHedging(T,S0,sigma,mu,rf,N)
    St = basemodel.StockPriceSim()

    pre_delta = 0
    money_account = 0
    pre_call_position = 0
    current_call_position = 0
    current_stock_position = 0
    current_delta = 0
    
    for k in range(len(St)-1):
        if k == 0:
            put_gamma,call_gamma,pre_call_position,call_price,put_delta,call_delta,pre_stock_position = basemodel.GammaSet(S0, 0)
            money_account = - pre_stock_position * S0 + basemodel.putPrice(S0, 0) - call_price * pre_call_position - basemodel.transactionfee(pre_stock_position, pre_call_position)

        else:
            put_gamma,call_gamma,current_call_position,call_price,current_delta,call_delta,current_stock_position = basemodel.GammaSet(St[k], k*T/(len(St)-1))
            change_call_position = current_call_position - pre_call_position
            change_stock_position = current_stock_position - pre_stock_position
            pre_call_position = current_call_position
            pre_stock_position = current_stock_position
            money_account = basemodel.getBankReturn(money_account,1) - change_stock_position * St[k] - basemodel.transactionfee(change_stock_position, change_call_position)\
                - call_price * change_call_position
    
    call_price = basemodel.callPrice(St[-1], 0.5, 0.25)
    if St[-1] < K:
        money_account = basemodel.getBankReturn(money_account,1) + current_stock_position * St[-1] + current_call_position * call_price + (-K + St[-1]) - basemodel.transactionfee(current_stock_position, current_call_position)
    else:
        money_account = basemodel.getBankReturn(money_account,1) + current_stock_position * St[-1] + current_call_position * call_price - basemodel.transactionfee(current_delta, current_call_position)

    final_pnl.append(money_account * np.exp(-rf * T))
    print(i)

plt.hist(final_pnl,bins=50)
plt.title('Delta-Gamma time based Hedging')

print(basemodel.clientCharge(basemodel.cVar(final_pnl)))
'''


#Q2 Delta-Gamma move based Hedging 
money_account = 0
final_pnl = []
money = []
for i in range(10000):
    basemodel = DGHedging(T,S0,sigma,mu,rf,N)
    St = basemodel.StockPriceSim()
    pre_delta = 0
    money_account = 0
    upper_band = 0
    lower_band = 0
    interest_days = 0
    pre_call_position = 0
    current_delta = 0
    current_call_position = 0
    current_stock_position = 0
    flag = 0
    for k in range(len(St)-1):
        interest_days += 1
        if k == 0:
            put_gamma,call_gamma,pre_call_position,call_price,put_delta,call_delta,pre_stock_position = basemodel.GammaSet(S0, 0)
            #put_gamma here should be negative, call_gamma should be positive, since we short the put, so we short the call. 
            money_account = - pre_stock_position * S0 + basemodel.putPrice(S0, 0) - call_price * pre_call_position - basemodel.transactionfee(pre_stock_position, pre_call_position)
            current_call_position = pre_call_position
            current_stock_position = pre_stock_position
        else:
            record.append([current_delta,money_account,current_call_position,current_stock_position])
            current_delta = pre_stock_position - basemodel.putDelta(St[k], k*T/N) + basemodel.callDelta(St[k], 0.5, k*0.25/91) * pre_call_position
            if (np.abs(current_delta) > 0.05):
                put_gamma,call_gamma,current_call_position,call_price,current_delta,call_delta,current_stock_position = basemodel.GammaSet(St[k], k*T/(len(St)-1))
                change_call_position = current_call_position - pre_call_position
                change_stock_position = current_stock_position - pre_stock_position
                money_account = basemodel.getBankReturn(money_account,interest_days) - change_stock_position * St[k] - basemodel.transactionfee(change_stock_position, change_call_position)\
                    - call_price * change_call_position
                pre_stock_position = current_stock_position
                pre_call_position = current_call_position
                interest_days = 0
        
        
            
    call_price = basemodel.callPrice(St[-1], 0.5,0.25)    
    if St[-1] < K:
        money_account = basemodel.getBankReturn(money_account, interest_days) + current_stock_position * St[-1] + (-K + St[-1]) - basemodel.transactionfee(current_delta, current_call_position) + current_call_position * call_price
    else:
        money_account = basemodel.getBankReturn(money_account, interest_days) + current_stock_position * St[-1] - basemodel.transactionfee(current_delta, current_call_position) + current_call_position * call_price
    final_pnl.append(money_account*np.exp(-rf * 0.25))
    
   
plt.hist(final_pnl,bins=50,density=True)
plt.title('Delta-Gamma move based Hedging ')
sns.kdeplot(final_pnl)
print(basemodel.clientCharge(basemodel.cVar(final_pnl)))


'''
#Q3 3 different bands for delta hedging

fig, axs = plt.subplots(4, 1, figsize=(10,40))

figIndex = -1

semibandlist = [0.1/2, 0.05/2, 0.02/2, 0.01/2]

res_array = []

for semiband in semibandlist:
    money_account = 0
    final_pnl = []
    figIndex += 1
    for i in range(10000):
        basemodel = DGHedging(T,S0,sigma,mu,rf,N)
        St = basemodel.StockPriceSim()
        port_delta = []
        
        pre_delta = 0
        money_account = 0
        upper_band = 0
        lower_band = 0
        interest_days = 0
        current_delta = 0
        stock_position = 0
        
        for k in range(len(St)-1):
            interest_days += 1
            if k == 0:
                pre_delta = basemodel.putDelta(S0, 0)
                stock_position = pre_delta
                money_account = - pre_delta * S0 + basemodel.putPrice(S0, 0) - basemodel.transactionfee(pre_delta, 0)
                upper_band = pre_delta + semiband
                lower_band = pre_delta - semiband
            
            else:
                current_delta = basemodel.putDelta(St[k], k*T/(len(St)-1))
    
                if current_delta > upper_band:
                    change_delta = current_delta - pre_delta
                    stock_position = current_delta
                    money_account = basemodel.getBankReturn(money_account,interest_days) - change_delta * St[k] - basemodel.transactionfee(change_delta, 0)
                    pre_delta = current_delta
                    upper_band = current_delta + semiband
                    lower_band = current_delta - semiband
                    if upper_band > 0:
                        upper_band = 0
                    elif lower_band < -1:
                        lower_band = -1
                    interest_days = 0
    
                        
                elif current_delta < lower_band:
                    change_delta = current_delta - pre_delta
                    stock_position = current_delta
                    money_account = basemodel.getBankReturn(money_account,interest_days) - change_delta * St[k] - basemodel.transactionfee(change_delta, 0)
                    pre_delta = current_delta
                    upper_band = current_delta + semiband
                    lower_band = current_delta - semiband
                    if upper_band > 0:
                        upper_band = 0
                    elif lower_band < -1:
                        lower_band = -1
                    interest_days = 0
    
    
    
        if St[-1] < K:
            money_account = basemodel.getBankReturn(money_account,1) + stock_position * St[-1] + (-K + St[-1]) - basemodel.transactionfee(stock_position, 0)
        else:
            money_account = basemodel.getBankReturn(money_account,1) + stock_position * St[-1] - basemodel.transactionfee(stock_position, 0)
    
        final_pnl.append(money_account*np.exp(-rf * 0.25))
        if np.abs(money_account) > 2:
            print(current_delta,St[-1],money_account,i,k)
        print(i)
    
    axs[figIndex].hist(final_pnl,bins=50)
    res_array.append(final_pnl)
    plt.subplot(4,1,figIndex+1).set_title(f'Band size: {semiband*2}')
    axs[figIndex].set_xticks(np.linspace(-3, 2,26)) 
    axs[figIndex].set_xticklabels([round(i,2) for i in np.linspace(-3, 2,26)],rotation=45)
    
    axs[figIndex].set_yticks(np.linspace(0, 1200,13)) 
    
    print(basemodel.clientCharge(basemodel.cVar(final_pnl)))
    



count = -1
plt.figure(figsize=(16,8))

for i in res_array:
    count += 1
    a = 0.3
    if count == 0:
        a = 1
    plt.hist(i,bins=100,alpha=a)

    axs[figIndex].set_xticks(np.linspace(-3, 2,26)) 
    axs[figIndex].set_xticklabels([i for i in np.linspace(-3, 2,26)],rotation=45)
    plt.legend([0.1,0.05,0.02,0.01,],loc="upper right",prop={'size': 10})


fig.show()
'''