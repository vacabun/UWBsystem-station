import numpy as np
import matplotlib.pyplot as plt

from filter import filter

def plot_result(measurements,real_state,filter_result):
    plt.figure(figsize=(8,4))
    plt.plot(range(1,len(measurements)), measurements[1:], label = 'Measurements')
    plt.plot(range(1,len(real_state)), real_state[1:], label = 'Real statement' )
    plt.plot(range(1,len(filter_result)), np.array(filter_result)[1:,0], label = 'Kalman Filter')
    plt.legend()
    plt.xlabel('Time',fontsize=14)
    plt.ylabel('velocity [m]',fontsize=14)
    plt.show()
    
    plt.figure(figsize=(8,4))
    plt.axhline(5, label='Real statement') #, label='$GT_x(real)$'
    plt.plot(range(1,len(filter_result)), np.array(filter_result)[1:,1], label = 'Kalman Filter')
    plt.legend()
    plt.xlabel('Time',fontsize=14)
    plt.ylabel('velocity [m]',fontsize=14)
    plt.show()

if __name__ == '__main__':
    np.random.seed(2)
    R = 2.
    real_state = []
    measurements = []
    for i in range(100):
        real_state.append(i)
        measurements.append(real_state[i]+ np.random.normal(0,R))
    
    filter_result_all_list, filter_result_lastest=filter(measurements)

    plot_result(measurements,real_state,filter_result_all_list)

