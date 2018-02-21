import numpy as np
import pandas as pa

def initialize(context):
    context.lev = 1.0
    context.time_frame = 10 + 1
    context.polynomial = 5
    context.avg1 = 33 + 1
    context.avg2 = 14 + 1
    context.avg3 = 6 + 1
    context.securities = [sid(24),
                          sid(5061),
                          sid(8347),
                          sid(4151),
                          sid(3149),
                          sid(11100),
                          sid(6653),
                          sid(16841),
                          sid(8151),
                          sid(5938),
                          sid(26578),
                          sid(21839),
                          sid(5923),
                          sid(23112),
                          sid(4283),
                          sid(3496),
                          sid(5029),
                          sid(700),
                          sid(2190),
                          sid(1637)]
    context.data = np.ndarray((len(context.securities), context.time_frame-1))
    context.regressions = np.ndarray((len(context.securities), context.polynomial+1))
    context.weights = np.ndarray((len(context.securities),))
    context.derivative = np.ndarray((len(context.regressions),context.polynomial+1))
    context.derivative2 = np.ndarray((len(context.regressions),context.polynomial+1))
    context.sums = np.ndarray((len(context.regressions),2))
    context.ma1 = np.ndarray((len(context.securities),))
    context.ma2 = np.ndarray((len(context.securities),))
    context.ma3 = np.ndarray((len(context.securities),))
    schedule_function(my_rebalance, date_rules.every_day(), time_rules.market_open(hours=1))

def my_rebalance(context,data):
    get_data(context,data)
    find_weights(context)
    purchase(context)

def purchase(context):
    for i, stock in enumerate(context.securities):
        order_target_percent(stock, context.weights[i]*context.lev)
    
def get_data(context,data):
    for i, stock in enumerate(context.securities):
        context.ma1 = data.history(stock, 'price', context.avg1, '1d')[:-1].mean()
        context.ma2 = data.history(stock, 'price', context.avg2, '1d')[:-1].mean()
        context.ma3 = data.history(stock, 'price', context.avg3, '1d')[:-1].mean()
        context.data[i] = data.history(stock, 'price', context.time_frame, '1d')[:-1]
        context.regressions[i] = np.polyfit(np.linspace(1,context.time_frame-1, num=context.time_frame-1), context.data[i], context.polynomial)

def find_weights(context):
    find_derivative(context)
    find_derivative2(context)
    find_sums(context)
    
    for i in range(0,len(context.securities)):
        d1=context.sums[i][0]
        d2=context.sums[i][1]
        if(context.ma3>=context.ma1 and context.ma3>=context.ma2):
            if(d1>=0 and d2>=0):
                context.weights[i] = 1.0/len(context.securities)
            elif(d1>=0 or d2>=0):
                context.weights[i] = 0.5/len(context.securities)
            elif(d1<0 and d2<0):
                context.weights[i] = -1.0/len(context.securities)
        elif(context.ma3>=context.ma2 and not(context.ma3>=context.ma1)):
            context.weights[i] = -0.0/len(context.securities)
        elif(context.ma2>=context.ma3):
             if(d1>=0 and d2>=0):
                 context.weights[i] = 1.0/len(context.securities)
             elif(d1>=0 or d2>=0):
                 context.weights[i] = 0.5/len(context.securities)
             elif(d1<0 and d2<0):
                 context.weights[i] = -1.0/len(context.securities)
        else:
             context.weights[i] = -0.1/len(context.securities)
    
def find_derivative(context):
    for n in range(0,len(context.regressions)):
        for i, coefficient in enumerate(context.regressions[n]):
            context.derivative[n][i] = coefficient*(context.polynomial-i)
            
def find_derivative2(context):
    for n in range(0,len(context.regressions)):
        for i, coefficient in enumerate(context.derivative[n]):
            context.derivative2[n][i] = coefficient*(context.polynomial-i-1)
            
def find_sums(context):
    for n in range(0, len(context.regressions)):
        _sum = 0
        for i, coefficient in enumerate(context.derivative[n]):
            _sum = _sum + coefficient * context.time_frame ** (context.polynomial - 1)
        context.sums[n][0]=_sum
        
        _sum = 0
        for i, coefficient in enumerate(context.derivative2[n]):
            _sum = _sum + coefficient * context.time_frame ** (context.polynomial - 2)  
        context.sums[n][1]=_sum