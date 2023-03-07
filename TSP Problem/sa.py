import datetime
import numpy.random
import math
import random
from tkinter import *
from ReadTSP import readTSP
import threading
import matplotlib.pyplot as plt

random.seed(0)
class SA(Canvas):

    def __init__(self, master, coords=None, temp=1000, coolingRate=0.999, endTemp=1e-8, scale=1, radius=5):
        """
        Canvas that visualize Simulated Annealing
        :param master: The window or frame you want to pack on
        :param coords: The coordinates of cities
        :param temp: Initial temperature
        :param coolingRate: Cooling rate of temperature
        :param endTemp: Threshold of ending
        :param scale: Scaling of coordinates
        :param radius: Radius of nodes
        """
        super().__init__(master, bg="white", width=480, height=500, highlightbackground = 'black')
        self.__coords = coords if coords is not None else []
        self.__path = [i for i in range(len(self.__coords))]
        self.__scale = scale
        self.__edges, self.__nodes = [], []
        self.__running, self.__lock = True, threading.RLock()
        self.__temp = temp
        self.__coolingRate = coolingRate
        self.__endTemp = endTemp
        self.__bestD = math.inf
        self.__NODE_RADIUS = radius
        self.__speed = 1

        self.__dist = self.__initDist(scale)

        if coords is not None:
            self.__DrawCircle()

        self.bind("<Button-1>", lambda e: self.__DrawCircle(e))
        self.bind("<MouseWheel>",  self.zoom)

    def stop(self, e):
        self.__lock.acquire()
        self.__running = False
        self.__lock.release()

    def zoom(self, event):
        x, y = self.canvasx(event.x), self.canvasy(event.y)
        self.scale(ALL, x, y, 1.001 ** event.delta, 1.001 ** event.delta)

    def __initDist(self, scale):
        distance = [[0 for col in range(len(self.__coords))] for row in range(len(self.__coords))]
        for r in range(len(self.__coords)):
            for c in range(len(self.__coords)):
                temp = pow((self.__coords[r][0] - self.__coords[c][0]), 2) + pow((self.__coords[r][1] - self.__coords[c][1]), 2)
                dist = pow(temp, 0.5) / scale
                distance[r][c] = dist
        return distance


    def __DrawLine(self, order):
        nodes_coords = []
        for node in self.find_withtag("nodes"):
            nodes_coords.append(self.coords(node))

        for coords in range(len(order) - 1):
            line = self.__edges[coords]
            x0 = (nodes_coords[order[coords]][0] + nodes_coords[order[coords]][2]) / 2
            x1 = (nodes_coords[order[coords + 1]][0] + nodes_coords[order[coords + 1]][2]) / 2
            y0 = (nodes_coords[order[coords]][1] + nodes_coords[order[coords]][3]) / 2
            y1 = (nodes_coords[order[coords + 1]][1] + nodes_coords[order[coords + 1]][3]) / 2
            self.coords(line, x0, y0, x1, y1)

        line = self.__edges[-1]
        x0 = (nodes_coords[order[-1]][0] + nodes_coords[order[-1]][2]) / 2
        x1 = (nodes_coords[order[0]][0] + nodes_coords[order[0]][2]) / 2
        y0 = (nodes_coords[order[-1]][1] + nodes_coords[order[-1]][3]) / 2
        y1 = (nodes_coords[order[0]][1] + nodes_coords[order[0]][3]) / 2
        self.coords(line, x0, y0, x1, y1)

    def __DrawCircle(self, event=None):
        if event is None:
            for cnt, coord in enumerate(self.__coords):
                oval = self.create_oval(coord[0] - self.__NODE_RADIUS, (coord[1]) - self.__NODE_RADIUS,
                                        coord[0] + self.__NODE_RADIUS, (coord[1]) + self.__NODE_RADIUS, fill="red", outline="red", tags="nodes")
                self.__nodes.append(oval)
                self.__edges.append(self.create_line(0, 0, 0, 0, width=1, fill="black", tags="line"))
                self.create_text(coord[0], coord[1] - 10, fill="black", text=cnt)
        else:
            cnt = 1
            self.create_oval(event.x - self.__NODE_RADIUS, event.y - self.__NODE_RADIUS,
                                    event.x + self.__NODE_RADIUS, event.y + self.__NODE_RADIUS, fill="red", outline="red")
            self.__coords.append([event.x, event.y])
            self.__edges.append(self.create_line(0, 0, 0, 0, width=2, fill="black"))
            self.create_text(event.x, event.y - 10, fill="black", text=cnt)
            cnt += 1

    def __nextOrder(self):
        next = self.__path.copy()
        num = random.randint(0, 1)

        if num == 1:
            r1 = random.randint(0, len(self.__coords) - 1)
            r2 = random.randint(r1, len(self.__coords) - 1)
            while r2 > r1:
                next[r1], next[r2] = next[r2], next[r1]
                r1 += 1
                r2 -= 1
        else:
            r1 = random.randint(0, len(self.__coords) - 1)
            r2 = random.randint(0, len(self.__coords) - 1)
            next[r1], next[r2] = next[r2], next[r1]
        return next

    def __CalDist(self, order):
        dist = 0
        for city in range(len(order) - 1):
            dist += self.__dist[order[city]][order[city + 1]]
        dist += self.__dist[order[-1]][order[0]]
        return dist

    def run(self, event, tempLabel:Label = None, bestLabel:Label = None, curLabel:Label = None):

        self.unbind("<Button-1>")
        self.__lock.acquire()
        self.__running = True
        self.__lock.release()
        start = datetime.datetime.now()
        dist = self.__CalDist(self.__path)
        iteration = []
        temps = []

        while self.__temp > self.__endTemp and self.__running:

            nextOrder = self.__nextOrder()
            nextDist = self.__CalDist(nextOrder)
            deltaDist = nextDist - dist
            if deltaDist < 0:
                self.__path = nextOrder
                dist = nextDist
                if dist < self.__bestD:
                    self.__bestD = dist
                    if bestLabel:
                        bestLabel.config(text=f"Best : {round(self.__bestD, 2)}")

            else:
                if numpy.exp(-deltaDist / self.__temp) > numpy.random.uniform():
                    self.__path = nextOrder
                    dist = nextDist

            self.__DrawLine(self.__path)
            self.after(self.__speed)
            self.update()
            temps.append(self.__temp)
            iteration.append(dist)
            self.__temp *= self.__coolingRate
            if tempLabel:
                tempLabel.config(text=f"Temp. : {self.__temp}")
            if curLabel:
                curLabel.config(text=f"Current : {round(dist, 2)}")
            # print(dist)
        self.__DrawLine(self.__path)

        end = datetime.datetime.now()
        # print(end - start)
        # print(self.__bestD)
        print(f"SA Path : {self.__path}")
        print(f"SA Best : {self.__bestD}")
        self.bind("<Button-1>", self.__DrawCircle)
        # print(end - start)

        plt.plot(temps, iteration)
        plt.title(f"SA")
        plt.axis([max(temps), min(temps), min(iteration), max(iteration)])
        plt.show()

    def configSpeed(self, speed):
        self.__speed = int(1000 / speed.get())


if __name__ == '__main__':
    coords = readTSP(r"../TSP Problem/tsp_folder/berlin52.txt", scale=0.5)
    w = Tk()
    s = SA(w, scale=0.5, coords=coords, coolingRate=0.99)
    w.bind("<s>", s.stop)
    w.bind("<Button-3>", s.run)
    s.pack()
    w.mainloop()

