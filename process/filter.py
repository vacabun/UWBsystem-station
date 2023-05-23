import numpy as np
import matplotlib.pyplot as plt
from filterpy.kalman import KalmanFilter
from filterpy.common import Q_discrete_white_noise

def filter(measurements):
    #filter
    kf = KalmanFilter(dim_x=2, dim_z=1)  #dim_x:隐状态大小，dim_z:量测大小
    #定义参数
    kf.x = np.array([[measurements[0]],[0]]) #初始状态[位置,速度]
    kf.F =np.array([[1.,1.],[0.,1.]]) #状态转移矩阵
    kf.H = np.array([[1.,0.]])  #量测矩阵
    kf.P *= 1000. #初始状态协方差
    kf.R = 100  #量测噪声
    kf.Q = Q_discrete_white_noise(2, 0.1, 10) #过程（系统）噪声

    filter_result=[]
    for i in range(len(measurements)):
        kf.predict()
        kf.update(measurements[i])
        filter_result.append(kf.x)
    return filter_result,filter_result[len(measurements)-1]