import numpy as np
import h5py
import json

f = h5py.File('./DataSet.mat', 'r')
data = f.get('data')
data = np.mat(data)
action = f.get('Car1_act')
action = np.array(action)
no_car_dis = 500
no_car_v = -30
tra = []

l_p_1 = []
v_1 = []
l_p_2 = []
d_2 = []
v_2 = []
l_p_3 = []
d_3 = []
v_3 = []

def lane_position(pos):
    if pos < -41.0:
        return 0
    else:
        return 1

for t in range(0, int(data.shape[1]/3)):
    car1 = data[:, 3*t].reshape((1, data.shape[0])).tolist()[0]
    car2 = data[:, 3*t+1].reshape((1, data.shape[0])).tolist()[0]
    car3 = data[:, 3*t+2].reshape((1, data.shape[0])).tolist()[0]
    
    tra.append(car1[2])
    
    l_p_1.append(car1[0])
    l_p_2.append(car2[0])
    l_p_3.append(car3[0])

    d_2.append(car2[2] - car1[2])
    d_3.append(car2[2] - car1[2])
    
    
    v_1.append(car1[3])
    v_2.append(car2[3] - car1[3])
    v_3.append(car3[3] - car1[3])

    
    if t == 1:
        print(tra[-1])
        print(l_p_1[-1])
        print(l_p_2[-1])
        print(l_p_3[-1])
        print(v_1[-1])
        print(v_2[-1])
        print(v_3[-1])
        print(d_2[-1])
        print(d_3[-1])

state_data ={
    "Car1_Position": tra,
    "Car1_Lane_Position": l_p_1,
    "Car1_Velocity": v_1,
    "Car2_Lane_Position": l_p_2,
    "Car2_Distance": d_2,
    "Car2_Velocity": v_2,
    "Car3_Lane_Position": l_p_3,
    "Car3_Distance": d_3,
    "Car3_Velocity": v_3,}
#"Action": action.tolist}

with open('data_v1.json', 'w') as fp:
    json.dump(state_data, fp)

 
