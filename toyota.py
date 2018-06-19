import preprocess
import numpy as np
import time
import scipy as sci
from mdp import mdp
from grids import grids
from apirl import apirl
import os
import ast
import sys
from preprocess import preprocess_dict, preprocess_list
import scipy.sparse as sparse



class toyota(grids, object):
    def __init__(self):
        if sys.version_info[0] >= 3:  
            super().__init__()
        else:
            super(toyota, self).__init__()
        ##[front dist, rear dist, left, right, front speed, rear speed, left speed, right speed, lane pos]
	'''
        self.threshes = [
                         [5],#front dist
                         [5],#rear dist
                         [1],#left
                         [1],#right
                         [5],#front speed
                         [-30],#rear speed
                         [-30],#left speed
                         [-30],#right speed
                         [-42.0]#lane pos
                                        t = uuuuuu ] ##list of threshes for each dimension
        

        # Thresholds for each interval
        self.threshes = [
                         [5, 15, 25],  # front dist
                         [5, 15, 25],  # rear dist
                         [1],  # left
                         [1],  # right
                         [-5, 5],  # front speed
                         [-5, 5],  # rear speed
                         [-5, 5],  # left speed
                         [-5, 5],  # right speed
                         [-42.0, -40.5],  # lane pos
                         ]  # list of threshes for each dimension
        '''
        self.threshes = [
                     [-41],  # car1 lane position
                     [0, 20, 40],  # car1 velocity
                
                     [-41],  # car2 lane
                     [-30, -10, 10, 30],  # car2 distance
                     [-10, 0, 10],  # car2 speed
                         
                     [-41],  # car3 lane
                     [-30, -10, 10, 30],  # car3 distance
                     [-10, 0, 10],  # car3 speed
                     ]  # list of threshes for each dimension

        self.grids = []
        for i in range(len(self.threshes)):
            self.grids.append(1 + len(self.threshes[i]))


        num_S = 1
        for i in self.grids:
            num_S *= i
        num_S += 2
        print("State space: %d" % num_S)

        num_A = 6

        self.M = mdp(num_S, num_A)
        self.M.set_features(num_features = 50) 

        self.M.T = list()
        for a in self.M.A:
            self.M.T.append(np.zeros([num_S, num_S]))

        self.M.epsilon = 1e-5
        self.max_iter = 30000
        self.discount = 0.99
        
    def coord_to_action(self, observation):
        return observation[0] + observation[1] * 2

    def build_trans(self, path = './data/data', freq = 20):
        # Preprocess the data set file which contains trajectories
        # Each trajectory is a list in which each element in a list is a list of time step, dict of observations and ...
        # This method translates the observations to coords
        tuples = []
        
        last_tuple = list()
        file_i = open(path, 'r')
        print("read list file")
        lines = file_i.readlines()
    
        i = 0
        time = 0
        offset = 1

        
        while i < len(lines):
            line = ast.literal_eval(lines[i])
            observation = line[1]
            coord = self.observation_to_coord(observation)
            state = self.coord_to_index(coord)

            actions = np.zeros([3])

            line_ = list()
            offset = 1
            while offset < freq:
                line_ = ast.literal_eval(lines[i + offset])
                if line_[0] == 0:
                    break
                
                #If the true trajectory ends, or offset is reached
                action_ = int(line_[2] - 3)
                actions[action_] += 1

                offset += 1

            if line_[0] == 0:
                i += offset
                if offset < freq/2.0:
                    continue
                else:
                    line_ = ast.literal_eval(lines[i - 1])
            else:
                line_ = ast.literal_eval(lines[i + offset - 1])
                i += 1

            observation_ = line_[1] 
            coord_ = self.observation_to_coord(observation_)
            state_ = self.coord_to_index(coord_)

            action = [0, 0]
            if coord_[0] == coord[0]:
                action[0] = 0
            else:
                action[0] = 1

            action[1] = np.argmax(actions)
            action = self.coord_to_action(action)

            tuples.append(
                      ('[' +
                       str(time) +
                       ', ' +
                       str(state) +
                       ', ' +
                       str(action) +
                       ', ' +
                       str(state_) +
                       ']\n'))

        file_o = open('./data/trans', 'w')
        for line_str in tuples:
            file_o.write(line_str)
        file_o.close()


    def build_demo(self, path = './data/data', freq = 20):
        # Preprocess the data set file which contains trajectories
        # Each trajectory is a list in which each element in a list is a list of time step, dict of observations and ...
        # This method translates the observations to coords
        starts = np.zeros([len(self.M.S)]).astype(bool)
        tuples = []
        last_tuple = list()
        file_i = open(path, 'r')
        print("read list file")
        lines = file_i.readlines()
    
        i = 0
        time = 0
        offset = 1

        observation = ast.literal_eval(lines[i]) 
        state = self.observation_to_index(observation)
        i += 1

        while i < len(lines):
            line = ast.literal_eval(lines[i])
            if line[0] == 0 or offset == freq:
                #If the true trajectory ends, or offset is reached
                observation_ = ast.literal_eval(lines[i - 1])[1]
                state_ = self.observation_to_index(observation_)
                tuples.append(
                          ('[' +
                           str(time) +
                           ', ' +
                           str(state) +
                           ', ' +
                           str('0') +
                           ', ' +
                           str(state_) +
                           ']\n'))
                #If the true trajectory ends, then time is reset to 0
                if line[0] == 0:
                    time == 0
                #If the offset is reached, time index add  1
                elif offset == freq:
                    time += 1
                
                #Begin a new trajectory, reset offset
                observation = ast.literal_eval(lines[i])[1] 
                sate = self.observation_to_index(observation)
                offset = 1
                if time == 0:
                    starts[state] = True

            else:
                #Keep adding offset
                offset += 1
            i += 1


        file_o = open('./data/demo', 'w')
        for line_str in tuples:
            file_o.write(line_str)
        file_o.close()

        file_o = open('./data/start', 'w')
        for s in range(len(starts)):
            if starts[s]:
                file_o.write(str(s) + '\n')
        file_o.close()

    def set_transitions(self, path = './data/trans', freq = 1):   
        # Count the times of transitioning from one state to another
        # Calculate the probability
        # Give value to self.T
        starts = np.zeros([len(self.M.S)])
        file = open(str(path), 'r')

        if True:
            for line_str in file.readlines():
                #line = line_str.split('\n')[0].split(',')
                line = ast.literal_eval(line_str)
                a = int(float(line[2]))
                s = int(float(line[1]))
                s_ = int(float(line[-1]))
                self.M.T[a][s, s_] += 1
                if int(float(line[0])) == 0:
                    starts[s] += 1
            file.close()

            for a in range(len(self.M.A)):
                for s in range(len(self.M.S)):
                    if s == self.M.S[-2]:
                        self.M.T[a][s] = starts
                    tot = np.sum(self.M.T[a][s])
                if tot == 0.0:
                    self.M.T[a][s,s] = 1.0
            self.M.T[a] = sparse.bsr_matrix(self.M.T[a])
            self.M.T[a] = sparse.diags(1.0/self.M.T[a].sum(axis = 1).A.ravel()).dot(self.M.T[a])
            return
        
    def write_mdp_file(self):
        file = open('./data/mdp', 'w')
        for s in range(len(self.M.S)):
            for a in range(len(self.M.A)):
                for s_ in range(len(self.M.S)):
                    file.write(str(self.M.S[s]) + ' ' + str(self.M.A[a]) + ' ' + str(self.M.S[s_]) + ' ' + str(self.M.T[self.M.A[a]][self.M.S[s], self.M.S[s_]]) + '\n')
        file.close()

    def build_mdp_from_file(self):
        file = open('./data/mdp', 'r')
        for line_str in file.readlines():
            line = line_str.split('\n')[0].split(' ')
            a = int(float(line[1]))
            s = int(float(line[0]))
            s_ = int(float(line[2]))
            p = float(line[-1])
            self.M.T[a][s, s_] = p
        file.close()

        file = open('./data/start', 'r')
        for line_str in file.readlines():
            #line = ast.literal_eval(line_str)
            line = line_str.split('\n')[0].split('\0')
            self.M.starts.append(int(line[0]))
        file.close()
            
 
    def learn_from_demo_file(self, path = './data/trans'):
        learn = apirl(self.M, max_iter = 30, epsilon = 1E-3) 
        demo_mu = learn.read_demo_file(paths = path) 
        opt = learn.iteration(exp_mu = demo_mu)
        policy = opt['policy']
        self.write_to_policy(policy)
    

    def write_to_policy(self, policy):
        file = open('./data/policy_' + time.strftime("%m_%d_%H_%m_%s", time.localtime()), 'w')
        for s in self.M.S:
            for a in self.M.A:
                file.write(str(policy[s][a]) + ' ')
            file.write('\n')
        file.close()

    def raw_to_observation(self, data):
        assert data.shape[1] == 3
        car1 = data[:, 0]
        car2 = data[:, 1]
        car3 = data[:, 2]
        
        return [car1[2], car1[0], car1[3], 
                car2[0], car2[2] - car1[2], car2[3] - car1[3], 
                car3[0], car3[2] - car1[2], car3[3] - car1[3]]

    def raw_to_index(self, data):
        observation = self.raw_to_observation(data)
        index = self.observation_to_index(observation)
    
    def raw_to_policy(self, data, policy):
        return int(np.argmax(policy[index]))



if __name__ == "__main__":
    toyota = toyota()
    toyota.build_demo()
    toyota.build_trans()
    toyota.set_transitions()
    #toyota.write_mdp_file()
    #toyota.build_mdp_from_file()
    toyota.learn_from_demo_file()
    


