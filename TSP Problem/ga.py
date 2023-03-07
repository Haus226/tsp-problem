import datetime
import random
import threading
import time

from ReadTSP import readTSP
import matplotlib.pyplot as plt
from tkinter import *

class GA(Canvas):

    def __init__(self, master, coords=None, popSize=1000, eliteSize=200,
                 mutateRate=0.001, genNum=1000, radius=5, scale=1,
                 animate=True, plot=True):
        super().__init__(master, width=480, height=500, bg="white", highlightbackground="black")

        self.__popSize, self.__eliteSize = popSize, eliteSize
        self.__mutateRate, self.__genNum = mutateRate, genNum
        self.__coords, self.__edges = coords if coords is not None else [], []
        self.__path = [x for x in range(len(self.__coords))]
        self.__cnt, self.__lock, self.__running = 0, threading.RLock(), True
        self.__NODE_RADIUS = radius
        self.__best = {"dist" : float("inf"), "path" : []}
        self.__animate, self.__plot = animate, plot

        for cnt, co in enumerate(self.__coords):
            node = self.create_oval(
                co[0] - self.__NODE_RADIUS, co[1] - self.__NODE_RADIUS,
                co[0] + self.__NODE_RADIUS, co[1] + self.__NODE_RADIUS,
                fill="red", outline="white", tags="nodes"
                    )
            self.create_text(co[0], co[1] - 10, fill="black", text=cnt)
            self.__edges.append(self.create_line(0, 0, 0, 0, width=1, fill="black"))
            cnt += 1

        self.__dist = self.__initDist(scale)
        self.bind("<MouseWheel>",  self.zoom)
        t = [24, 11, 27, 26, 25, 46, 12, 13, 51, 10, 50, 32, 42, 9, 8, 7, 40, 18, 44, 31, 48, 0, 21, 30, 17, 2, 16, 20, 41, 6, 1, 29, 22, 19, 49, 28, 15, 43, 33, 34, 35, 38, 39, 36, 37, 4, 14, 3, 5, 23, 47, 45]
        self.__drawLine(t)
        # t = [
        #     48, 31, 44, 18, 40, 7, 8, 9, 42, 32, 50, 10, 51,
        #     13, 12, 46, 25, 26, 27, 11, 24, 3, 5, 14, 4, 23, 47, 37, 36, 39, 38,
        #     35, 0, 21, 30, 17, 2, 16, 20, 41, 6, 1, 29, 22, 19, 49, 28, 15, 45, 43, 33, 34
        # ]
        # print(len(t))
        # print(1 / self.__calFitness(t, self.__dist))
        # t = [24, 11, 27, 26, 25, 46, 12, 13, 51, 10, 50, 32, 42, 9, 8, 7, 40, 18, 44, 31, 48, 0, 21, 30, 17, 2, 16, 20, 41, 6, 1, 29, 22, 19, 49, 28, 15, 43, 33, 34, 35, 38, 39, 36, 37, 4, 14, 3, 5, 23, 47, 45]
        # print(1 / self.__calFitness(t, self.__dist))

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

    def __initialPopulation(self):
        population = []
        for cnt in range(self.__popSize):
            population.append(random.sample(self.__path, len(self.__path)))
        return population

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

    @staticmethod
    def __calFitness(path, dist_):
        dist = 0
        for city in range(len(path) - 1):
            dist += dist_[path[city]][path[city + 1]]
        dist += dist_[path[-1]][path[0]]
        return 1 / dist

    def __individualRanking(self, population, dist):
        fitness = []
        for cnt, path in enumerate(population):
            fitness.append([cnt, self.__calFitness(path, dist)])
        fitness.sort(reverse=True, key=lambda x: x[1])
        return fitness

    def __Selection(self, ranking):
        selection = []
        for cnt in range(self.__eliteSize):
            selection.append(ranking[cnt][0])
        while len(selection) < len(ranking):
            index = random.randint(0, len(ranking) - 1)
            if random.uniform(0, 1) > 0.5:
                selection.append(ranking[index][0])

        return selection

    @staticmethod
    def __matingPool(population, selectionResult):
        pool = []
        for cnt in range(0, len(selectionResult)):
            pool.append(population[selectionResult[cnt]])
        return pool

    @staticmethod
    def __breed(parent1, parent2):
        child = []
        childP1 = []
        childP2 = []

        geneA = int(random.random() * len(parent1))
        geneB = int(random.random() * len(parent1))

        startGene = min(geneA, geneB)
        endGene = max(geneA, geneB)

        for i in range(startGene, endGene):
            childP1.append(parent1[i])

        childP2 = [item for item in parent2 if item not in childP1]

        child = childP1 + childP2
        return child

    def __breedPopultation(self, matingPool):
        children = []
        length = len(matingPool) - self.__eliteSize
        pool = random.sample(matingPool, len(matingPool))

        for i in range(self.__eliteSize):
            children.append(matingPool[i])

        for i in range(length):
            child = self.__breed(pool[i], pool[len(matingPool) - i - 1])
            children.append(child)
        return children

    def __mutate(self, individual):
        for cnt in range(len(individual)):
            if (random.uniform(0, 1) < self.__mutateRate):
                r1 = random.randint(0, len(individual) - 1)
                r2 = random.randint(0, len(individual) - 1)
                individual[r1], individual[r2] = individual[r2], individual[r1]
        return individual

    def __mutatePopulation(self, population):
        mutated = []
        for individual in population:
            mutatedInd = self.__mutate(individual)
            mutated.append(mutatedInd)
        return mutated

    def __nextGeneration(self, currentGen):
        ranking = self.__individualRanking(currentGen, self.__dist)
        selection = self.__Selection(ranking)
        pool = self.__matingPool(currentGen, selection)
        children = self.__breedPopultation(pool)
        nextGen = self.__mutatePopulation(children)
        return nextGen

    def run(self, population, genLabel:Label = None, bestLabel:Label = None, curLabel:Label = None):
        pop = self.__initialPopulation()
        iteration = []

        for num in range(self.__genNum):
            pop = self.__nextGeneration(pop)
            curDist = 1 / self.__individualRanking(pop, self.__dist)[0][1]
            curPath = pop[self.__individualRanking(pop, self.__dist)[0][0]]
            if curDist < self.__best["dist"]:
                self.__best["dist"] = curDist
                self.__best["path"] = curPath.copy()

            if genLabel:
                genLabel.config(text=f"Generation : {num + 1}")
            if bestLabel:
                bestLabel.config(text=f"Best : {round(self.__best['dist'], 2)}")
            if curLabel:
                curLabel.config(text=f"Current : {round(curDist, 2)}")
            if self.__animate:
                self.__drawLine(curPath)
                self.after(1)
                self.update()
            iteration.append(curDist)

        print(f"GA Path : {self.__best['path']}")
        print(f"GA Best : {self.__best['dist']}")

        self.__drawLine(self.__best["path"])
        if curLabel:
            curLabel.config(text=f"Current : {round(self.__best['dist'], 2)}")
        self.after(1000)
        self.update()

        time.sleep(10)
        if self.__plot:
            plt.plot(iteration)
            plt.title(f"GA")
            plt.ylabel("Dist.")
            plt.xlabel(f"Gen.")
            plt.show()


if __name__ == '__main__':
    # random.seed(0)
    c = readTSP("tsp_folder/berlin52.txt", 1)
    w = Tk()
    g = GA(w, c, genNum=1000, popSize=1000, eliteSize=200, animate=False, plot=False)
    g.pack()
    w.bind("<Button-3>", g.run)
    w.mainloop()