"""
References:
    https://mp.weixin.qq.com/s/poQT_V46ZeucCfx0ctIPvQ
    https://github.com/ppoffice/ant-colony-tsp/blob/master/aco.py
    https://zhuanlan.zhihu.com/p/137408401
"""

import random
import threading                # Pause the thread
from tkinter import *
from ReadTSP import readTSP     # Read the file that storing data of tsp
import matplotlib.pyplot as plt

random.seed(0)

class Ant():

    def __init__(self, CITY_NUM):
        self.__cityNum = CITY_NUM
        self.path = []
        self.total_distance, self.move_cnt = 0, 0
        self.cur = random.randint(0, self.__cityNum - 1)
        self.visited = [False for city in range(self.__cityNum)]
        self.path.append(self.cur)
        self.visited[self.cur] = True
        self.move_cnt += 1

    def __clean(self):
        self.path = []
        self.total_distance, self.move_cnt = 0, 0
        self.cur = random.randint(0, self.__cityNum - 1)
        self.visited = [False for city in range(self.__cityNum)]
        self.path.append(self.cur)
        self.visited[self.cur] = True
        self.move_cnt += 1

    def __next(self, alpha, beta, dist, pher):
        next_loc = -1
        probabilities = [0 for city in range(self.__cityNum)]
        total_prob = 0
        for city in range(self.__cityNum):
            if not self.visited[city]:
                probabilities[city] = pow(pher[self.cur][city], alpha) * pow((1 / dist[self.cur][city]), beta)
        total_prob = sum(probabilities)
        temp_prob = random.random()
        for p in range(self.__cityNum):
            probabilities[p] /= total_prob
            if not self.visited[p]:
                temp_prob -= probabilities[p]
                if temp_prob < 0:
                    self.path.append(p)
                    self.visited[p] = True
                    self.total_distance += dist[self.cur][p]
                    self.cur = p
                    self.move_cnt += 1
                    break

    def search(self, alpha, beta, dist, pher):
        self.__clean()
        while self.move_cnt < self.__cityNum:
            self.__next(alpha, beta, dist, pher)
        self.total_distance += dist[self.path[-1]][self.path[0]]  # Distance between ending and starting


class ACO(Canvas):

    def __init__(self, master, coords=None, alpha=1.0, beta=5, tau=1, rho=0.9, q=1, iter=100,
                 scale=1, radius=5, animate=True, plot=True):
        """
        Canvas that visualize ACO
        :param master: The window or frame you want to pack on
        :param coords: The coordinates of cities
        :param alpha: Weight of pheromone on transition probability
        :param beta: Weight of heuristic on transition probability
        :param tau: Initial value of pheromone
        :param rho: Evaporation rate of pheromone
        :param q: Constant in calculation that update pheromone after an iteration
        :param iter: Number of iterations
        :param scale: Scaling of coordinates
        :param radius: Radius of nodes
        """
        super().__init__(master, width=480, height=500, bg="white", highlightbackground="black")

        self.__CITY_NUM = len(coords)
        self.__ANT_NUM = int(self.__CITY_NUM * 0.5)
        self.__ITER = iter
        self.__ALPHA = alpha
        self.__BETA = beta
        self.__TAU = tau
        self.__RHO = rho
        self.__Q = q
        self.__NODE_RADIUS = radius

        self.__PHEROMONE = [[self.__TAU for col in range(self.__CITY_NUM)] for row in range(self.__CITY_NUM)]
        self.__speed, self.__animate, self.__plot = 1, animate, plot

        self.__ants = [Ant(self.__CITY_NUM) for num in range(self.__ANT_NUM)]
        self.__best = {"dist" : float("inf"), "path" : []}
        self.__coords, self.__edges = coords if coords is not None else [], []
        self.__cnt, self.__lock, self.__running = 0, threading.RLock(), True

        for cnt, co in enumerate(self.__coords):
            node = self.create_oval(
                co[0] - self.__NODE_RADIUS, co[1] - self.__NODE_RADIUS,
                co[0] + self.__NODE_RADIUS, co[1] + self.__NODE_RADIUS,
                fill="red", outline="white", tags="nodes"
                    )
            self.create_text(co[0], co[1] - 10, fill="black", text=cnt)
            self.__edges.append(self.create_line(0, 0, 0, 0, width=1, fill="black"))

        self.__DISTANCE = self.__initDist(scale)

        self.bind("<MouseWheel>",  self.zoom)


    def stop(self, e):
        self.__lock.acquire()
        self.__running = False
        self.__lock.release()

    def zoom(self, event):
        x, y = self.canvasx(event.x), self.canvasy(event.y)
        self.scale(ALL, x, y, 1.001 ** event.delta, 1.001 ** event.delta)

    def __initDist(self, scale):
        distance = [[0 for col in range(self.__CITY_NUM)] for row in range(self.__CITY_NUM)]
        for r in range(self.__CITY_NUM):
            for c in range(self.__CITY_NUM):
                temp = pow((self.__coords[r][0] - self.__coords[c][0]), 2) + pow((self.__coords[r][1] - self.__coords[c][1]), 2)
                dist = pow(temp, 0.5) / scale
                distance[r][c] = dist
        return distance

    def __reset(self):
        self.delete("line")
        self.__ants = [Ant(self.__CITY_NUM) for num in range(self.__ANT_NUM)]
        self.__best = {"dist" : float("inf"), "path" : []}
        for r in range(self.__CITY_NUM):
            for c in range(self.__CITY_NUM):
                self.__PHEROMONE[r][c] = self.__TAU

    def __drawLine(self, path):
        nodes_coords = []
        for node in self.find_withtag("nodes"):
            nodes_coords.append(self.coords(node))

        for coords in range(len(path) - 1):
            line = self.__edges[coords]
            x0 = (nodes_coords[path[coords]][0] + nodes_coords[path[coords]][2]) / 2
            x1 = (nodes_coords[path[coords + 1]][0] + nodes_coords[path[coords + 1]][2]) / 2
            y0 = (nodes_coords[path[coords]][1] + nodes_coords[path[coords]][3]) / 2
            y1 = (nodes_coords[path[coords + 1]][1] + nodes_coords[path[coords + 1]][3]) / 2
            self.coords(line, x0, y0, x1, y1)

        line = self.__edges[-1]
        x0 = (nodes_coords[path[-1]][0] + nodes_coords[path[-1]][2]) / 2
        x1 = (nodes_coords[path[0]][0] + nodes_coords[path[0]][2]) / 2
        y0 = (nodes_coords[path[-1]][1] + nodes_coords[path[-1]][3]) / 2
        y1 = (nodes_coords[path[0]][1] + nodes_coords[path[0]][3]) / 2
        self.coords(line, x0, y0, x1, y1)

    def run(self, e, iterLabel:Label = None, bestLabel:Label = None, curLabel:Label = None):
        self.after(1)
        self.update()
        self.__lock.acquire()
        self.__running = True
        self.__lock.release()
        iteration = []
        while self.__ITER > self.__cnt and self.__running:
            cur = float("inf")
            curPath = []
            for ant in self.__ants:
                ant.search(self.__ALPHA, self.__BETA, self.__DISTANCE, self.__PHEROMONE)
                if ant.total_distance < self.__best["dist"]:
                    self.__best["dist"] = ant.total_distance
                    self.__best["path"] = ant.path.copy()
                    if bestLabel:
                        bestLabel.config(text=f"Best : {round(self.__best['dist'], 2)}")
                if ant.total_distance < cur:
                    cur = ant.total_distance
                    curPath = ant.path
            iteration.append(self.__best["dist"])
            if self.__animate:
                self.__updatePheromone()
                self.__drawLine(curPath)
                self.after(self.__speed)
                self.update()
                self.__cnt += 1
            if iterLabel:
                iterLabel.config(text=f"Iterations : {self.__cnt}")
            if curLabel:
                curLabel.config(text=f"Current : {round(cur, 2)}")

        print(f"ACO Path : {self.__best['path']}")
        print(f"ACO Best : {self.__best['dist']}")

        self.__drawLine(self.__best["path"])
        curLabel.config(text=f"Current : {round(self.__best['dist'], 2)}")
        self.after(1000)
        self.update()
        if self.__plot:
            plt.plot(iteration)
            plt.title(f"ACO")
            plt.ylabel("Dist.")
            plt.xlabel(f"Iter.")
            plt.show()


    def configSpeed(self, speed):
        self.__speed = int(1000 / speed.get())


    def __updatePheromone(self):
        temp_pher = [[0 for r in range(self.__CITY_NUM)] for c in range(self.__CITY_NUM)]
        for ant in self.__ants:
            for i in range(1, self.__CITY_NUM):
                start, end = ant.path[i - 1], ant.path[i]
                temp_pher[start][end] += self.__Q / ant.total_distance
                temp_pher[end][start] = temp_pher[start][end]
        for i in range(self.__CITY_NUM):
            for j in range(self.__CITY_NUM):
                self.__PHEROMONE[i][j] = self.__PHEROMONE[i][j] * self.__RHO + temp_pher[i][j]


if __name__ == '__main__':
    co = readTSP("../TSP Problem/tsp_folder/berlin52.txt", scale=2)
    coords = readTSP(r"../TSP Problem/tsp_folder/berlin52.txt", scale=2)
    w = Tk()
    a = ACO(w, scale=2, coords=coords)
    w.bind("<s>", a.stop)
    w.bind("<Button-3>", a.run)
    a.pack()
    w.mainloop()
