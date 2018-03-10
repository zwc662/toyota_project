import numpy as np
import scipy as sci

class discretizer:
    def __init__(self):
	'''      
        self.grids = [5, 5, 2, 2, 5, 5, 5, 5, 3]  ##list of unit numbers in each dimension
        ##[front dist, rear dist, left, right, front speed, rear speed, left speed, right speed, lane pos]
        self.threshes = [
                         [5, 10, 20, 25],#front dist
                         [5, 10, 20, 25],#rear dist
                         [1],#left
                         [1],#right
                         [5, 10, 20, 30],#front speed
                         [-30, -10, -20, -5],#rear speed
                         [-30, -10, 10, 30],#left speed
                         [-30, -10, 10, 30],#right speed
                         [-42.0, -40.5],#lane pos
                         ] ##list of threshes for each dimension
        '''
        self.grids = [4, 4, 2, 2, 3, 3, 3, 3, 3]  ##list of unit numbers in each dimension
        ##[front dist, rear dist, left, right, front speed, rear speed, left speed, right speed, lane pos]
        self.threshes = [
                         [5, 15, 25],#front dist
                         [5, 15, 25],#rear dist
                         [1],#left
                         [1],#right
                         [-5, 5],#front speed
                         [-5, 5],#rear speed
                         [-5, 5],#left speed
                         [-5, 5],#right speed
                         [-42.0, -40.5],#lane pos
                         ] ##list of threshes for each dimension

    def build_discretizer(self, grids, threshes):
        assert len(grids) == len(threshes)
        for i in range(len(grids)):
            if(grids[i] != len(threshes[i])):
               raise ValueError("threshes conflict grids")
        self.grids = grids
        self.threshes = threshes
    
    def observation_to_coord(self, observation):
        coord = np.zeros([len(self.grids)])
        for i in range(len(observation)):
            for j in range(len(self.threshes[i])):
               if observation[i] >= self.threshes[i][j]:
                continue
               else:
                coord[i] = j 
		break
            if observation[i] >= self.threshes[i][-1]:
                coord[i] = len(self.threshes[i])
        return coord
