# -*- coding: utf-8 -*-
"""
Created on Thu Oct 27 17:26:34 2022

@author: tomls
"""

import random
import numpy as np
from scipy.stats import norm

random.seed(1)
class DGHedging:
    def __init__(self,T,S0,sigma,mu,rf,N):
        self.T = T
        self.S0 = S0
        self.sigma = sigma
        self.mu = mu
        self.rf = rf
        self.K = S0
        self.stockPriceArray = []
        self.N = N
        self.dt = T/N
        
    def StockPriceSim(self):
        St = self.S0
        for i in np.linspace(0, self.T,self.N+1):
            dWt = random.normalvariate(0, np.sqrt(self.dt))
            self.stockPriceArray.append(St)
            St = St + St * self.mu*self.dt + St * self.sigma*dWt
        return self.stockPriceArray
    
    def dplus(self, St, t):
        return (np.log(St/self.K) + ((self.rf + 0.5 * self.sigma**2) * (self.T - t))) \
    /(self.sigma * np.sqrt(self.T - t))
    
    def dminus(self, St, t):
        return (np.log(St/self.K) + ((self.rf - 0.5 * self.sigma**2) * (self.T - t))) \
    /(self.sigma * np.sqrt(self.T - t))
    
    def putDelta(self, St, t):
        return norm.cdf(self.dplus(St, t)) - 1
    
    def putPrice(self, St, t):
        return self.K * np.exp(-self.rf*(self.T - t)) * norm.cdf(- self.dminus(St, t)) - St * norm.cdf(-self.dplus(St, t))
    
    def callPrice(self, St, t):
        return St * norm.cdf(self.dplus(St, t)) - self.K * np.exp(-self.rf*(self.T - t)) * norm.cdf(self.dminus(St, t))
    
    def Gamma(self, St, t):
        return (norm.pdf(self.dplus(St, t)))/(self.sigma*St*np.sqrt(self.T-t))
    
    def transactionfee(self, changeDelta, changeOption):
        return np.abs(changeDelta) * 0.005 + np.abs(changeOption) * 0.01
    
    def getBankReturn(self, money,days):
        return money * np.exp(self.rf*self.dt*days)
    
    def cVar(self, final_pnl):
        tenpercentile = np.quantile(final_pnl,0.1)
        leasttenpercentlist = [i for i in final_pnl if i <=tenpercentile]
        return np.array(leasttenpercentlist).mean() / np.exp(-self.rf * self.T)
    
    def clientCharge(self, cVar):
        return - cVar - 0.02 + self.putPrice(100, 0)