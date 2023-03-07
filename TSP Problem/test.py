"""
SA Parameters:
    Initial Temp. = 1000
    Cooling Rate = 0.999
    End Temp. = 1e-9
References:
    https://blog.csdn.net/google19890102/article/details/45395257

GA Parameters:
    Population Size = 1000
    Elite Size = 200
    Generation = 1000
    Mutating Rate = 0.001
References:
    https://github.com/ezstoltz/genetic-algorithm/blob/master/genetic_algorithm_TSP.ipynb

ACO Parameters:
    Alpha = 1.0             Weight of pheromone on decision 信息素重要程度因子
    Beta = 5                Weight of heuristic on decision 启发函数重要程度因子
    Rho = 0.9               Evaporation rate 信息素的挥发程度
    Tau = 1                 Initial value of pheromone 信息素初始值
    Q = 1                   Constant 常数
    Iteration = 1000
References:
    https://mp.weixin.qq.com/s/poQT_V46ZeucCfx0ctIPvQ
    https://github.com/ppoffice/ant-colony-tsp/blob/master/aco.py
    https://zhuanlan.zhihu.com/p/137408401
"""