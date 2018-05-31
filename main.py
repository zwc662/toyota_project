import numpy as np
import time
import scipy as sci
import mdp
import apirl
from discretizer import discretizer
import os
import ast
from preprocess import preprocess_dict, preprocess_list
import scipy.sparse as sparse



class run(object):
    def __init__(maxsize):
	pass

#    def limit_memory(self):
#	maxsize = self.maxsize
#        soft, hard = resource.getrlimit(resource.RLIMIT_AS)
#        resource.setrlimit(resource.RLIMIT_AS, (maxsize, hard))
    

    def main(self):
        #preprocess_dict('/home/zekunzhou/workspace/toyota_project/data/data.json')
        #preprocess_list('/home/zekunzhou/workspace/toyota_project/data/data.json')
        
        #M = mdp.mdp()
        
	M = apirl.apirl()
        
        M.build_from_discretizer(num_actions = 2 * 3)
        M.preprocess_list()
        M.set_transitions()
        
        M.run(max_iter = 50)

        #M.build_from_config(15000, 5)
        #M.set_transitions_random()
        #M.set_policy_random()

        M.reward = np.random.random([len(M.S), ]).astype(float)
        
        start = time.time()
        _, w, _ = M.QP(np.random.random((10)), np.random.random((10, 10)))
        end = time.time()
        print("QP time: %f" % (end - start))

        start = time.time()
        policy = M.value_iteration()
        end = time.time()
        print("Value iteration time: %f" % (end - start))

        M.set_policy(policy)

        start = time.time()
        v = M.expected_value()
        #mu = M.LP_features()
        end = time.time()
        print("Policy iteration time: %f" % (end - start))
        print(v[-2])

        '''
        start = time.time()
        v = M.expected_value_manual()
        #mu = M.LP_features()
            end = time.time()
        print("Policy iteration time: %f" % (end - start))
        print(v[-2])
        '''

        start = time.time()
        v = M.LP_value_()
        end = time.time()
        print("LP time: %f" % (end - start))
        print(v)
        print(v[-2])
        #mu = M.LP_features()

    
        exit()
        ##Use script to run PRISM, somehow doesn't work. Still working on it.
        os.system('/home/zekunzhou/workspace/toyota_project/prism-4.4.beta-src/src/demos/run /home/zekunzhou/workspace/toyota_project/')
        os.system('/home/zekunzhou/workspace/toyota_project/prism-4.4.beta-src/bin/prism ./grid_world.pm ./grid_world.pctl')


if __name__ == "__main__":
    run = run()
    run.main() 
    


