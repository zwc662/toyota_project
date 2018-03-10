import numpy as np
from scipy import sparse
import os
import ast
from discretizer import discretizer

class mdp:
    def __init__(self):
        self.S = list() ## extra states S[-1] is the unsafe terminal and S[-2] the initial terminal
        self.A = list()
        self.T = None
        self.P = None
        self.policy = None
        self.targets = list()
        self.starts = list()
        self.unsafes = list()
        self.discretizer = discretizer()

    def build_from_config(self, num_states, num_actions):
        self.S = range(num_states + 2)   ##Add one external source
        self.A = range(num_actions)
        self.T = []
	for a in range(len(self.A)):
		self.T.append(np.zeros([len(self.S), len(self.S)], dtype = np.int8))  ##Init transition probability to be all zero
    
    def build_from_discretizer(self, discretizer = None, num_actions = None):
        if discretizer != None:
            self.discretizer = discretizer
        print(self.discretizer.grids)
        self.S = range(np.array(self.discretizer.grids).prod() + 2)   ##Add two external source
        print(len(self.S))
        self.A = range(num_actions)
        print(len(self.A))
	self.T = []
	for a in range(len(self.A)):
		self.T.append(np.zeros([len(self.S), len(self.S)], dtype = np.int8))  ##Init transition probability to be all zero
        print("construction complete")
            
    def set_starts(self, starts):
        self.starts = starts
	for a in range(len(self.A)):
        	self.T[a][:, self.S[-2]] = self.T[a][:, self.S[-2]] * 0.0
        	self.T[a][self.S[-2]] = self.T[a][self.S[-2]] * 0.0
        
        	self.T[a][:, self.starts] = self.T[a][:, self.starts] * 0.0
        	self.T[a][self.S[-2], self.starts] = 1.0/len(self.starts)

    def set_targets(self, targets):
        self.targets = targets
	for a in range(len(self.A)):
        	self.T[a][self.targets] = self.T[a][self.targets] * 0.0
        	self.T[a][self.targets, self.targets] = 1.0

    def set_unsafes(self, unsafes):
        self.unsafes = unsafes
        
	for a in range(len(self.A)):
        	self.T[a][:, self.S[-1]] = self.T[a][:, self.S[-1]] * 0.0
        	self.T[a][self.S[-1]] = self.T[a][self.S[-1]] * 0.0
        	self.T[a][self.S[-1], self.S[-1]] = 1.0
        
        	self.T[a][self.unsafes] = self.T[a][self.unsafes] * 0.0
        	self.T[a][self.unsafes, self.S[-1]] = 1.0

    def observation_to_state(self, observation):
        coord = self.discretizer.observation_to_coord(observation)
        state = coord[0]
        for i in range(1, len(coord)):
        	state_temp = coord[i]
            	for j in range(0, i):
       			state_temp *= self.discretizer.grids[j]
            	state += state_temp
        return state
    
    def preprocess_list(self, data):
        tuples = []
        file_i = open(data, 'r')
        print("read list file")
        for line_str in file_i.readlines():
        	line = ast.literal_eval(line_str)
            	observation = line[1]
            	state = self.observation_to_state(observation)
            	action = line[2]
            	observation_ = line[3]
            	state_ = self.observation_to_state(observation_)
            	tuples.append((str(state) + ' ' + str(action) + ' ' + str(state_) + '\n'))
        file_i.close()
        
        file_o = open('./data/transitions', 'w')
        for line_str in tuples:
        	file_o.write(line_str)
        file_o.close()
    
    def set_transitions(self, transitions):
        file = open(str(transitions), 'r')
        for line_str in file.readlines():
            	line = line_str.split('\n')[0].split(' ')
            	a = int(float(line[1]))
            	s = int(float(line[0]))
            	s_ = int(float(line[2]))
		self.T[a][s,s_] += 1
        file.close()
        for a in range(len(self.A)):
            	for s in range(len(self.S)):
			norm = np.linalg.norm(self.T[a][s])
                	if norm == 0.0:
                    		continue
               		#for s_ in range(len(self.S)):
                    	self.T[a][s] = (self.T[a][s]/norm).astype(np.float32)
         
    def set_policy(self, policy):
        assert policy.shape == (len(self.S), len(self.A))
        if (policy.sum(axis = 1) <= np.ones([len(self.S)]).astype(np.float32)).all():
            	polcy = policy + ((np.ones([len(self.S)]).astype(np.float32) - policy.sum(axis = 1))/len(self.A)).reshape([len(self.S), 1])
        else:
            	#raise ValueError("policy action distribution sum larger than 1.0")
            	print("policy action distribution sum larger than 1.0")
    		policy_ = np.linalg.norm(policy, axis = 1).reshape([len(self.S), 1]).astype(np.float32)
    		policy = policy / policy_
        self.policy = policy

	self.P = np.zeros([len(self.S), len(self.S)], dtype = np.float32)
	for a in range(len(self.A)): 
        	self.P += self.T[a] * policy[:, a].reshape([len(self.S), 1])
		self.T[a] = sparse.csr_matrix(self.T[a])
        for s in range(len(self.S)):
		norm = np.linalg.norm(self.P[s])
               	if norm == 0.0:
                	continue
                self.P[s] = (self.P[s]/norm).astype(np.float32)
         
        assert self.P.shape == (len(self.S), len(self.S))
	self.P = sparse.csr_matrix(self.P)


    def output(self):
        os.system('rm ./state_space')
        os.system('touch ./state_space')
        file = open('./state_space', 'w')
        file.write('states\n' + str(len(self.S)) + '\n')
        file.write('actions\n' + str(len(self.A)) + '\n')
        file.close()

        os.system('rm ./unsafe')
        os.system('touch ./unsafe')
        file = open('unsafe', 'w')
        for i in range(len(self.unsafes)):
            	file.write(str(self.unsafes[i]) + ':\n')
        file.close()

        os.system('rm ./optimal_policy')
        os.system('touch ./optimal_policy')
        file = open('./optimal_policy', 'w')
        for i in range(len(self.S)):
            	for j in range(len(self.S)):
                	file.write(str(self.S[i]) + ' ' + str(self.S[j]) + ' ' + str(self.P[self.S[i], self.S[j]]) + '\n')
        file.close()




