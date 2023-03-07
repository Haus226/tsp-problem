import sa
import aco
import tkinter as tk
import ReadTSP
import threading
import ga

class GUI:

    def __init__(self, coords, scale):
        window = tk.Tk()
        window.title("SA Vs ACO Vs GA")
        mainFrame = tk.Frame(window)
        mainFrame.pack()
        SAframe = tk.Frame(mainFrame)
        SAframe.grid(row=0, column=0)
        ACOframe = tk.Frame(mainFrame)
        ACOframe.grid(row=0, column=1)
        GAframe = tk.Frame(mainFrame)
        GAframe.grid(row=0, column=2)

        SA = sa.SA(SAframe, coords=coords, scale=scale, radius=3)
        SA.grid(row=0, column=0)
        self.__tempLabel = tk.Label(SAframe, text="Temp. : 1000", font=("Aerial", 20))
        self.__SAcurLabel = tk.Label(SAframe, text="Current : 0", font=("Aerial", 20))
        self.__bestLabel = tk.Label(SAframe, text=f"Best : {float('inf')}", font=("Aerial", 20))
        self.__tempLabel.grid(row=1, column=0)
        self.__SAcurLabel.grid(row=2, column=0)
        self.__bestLabel.grid(row=3, column=0)

        ACO = aco.ACO(ACOframe, coords=coords, scale=scale, iter=1000, radius=3)
        ACO.grid(row=0, column=0)
        self.__iterLabel = tk.Label(ACOframe, text=f"Iteration : 0", font=("Aerial", 20))
        self.__ACOcurLabel = tk.Label(ACOframe, text="Current : 0", font=("Aerial", 20))
        self.__bestAntLabel = tk.Label(ACOframe, text=f"Best : {float('inf')}", font=("Aerial", 20))
        self.__iterLabel.grid(row=1, column=0)
        self.__ACOcurLabel.grid(row=2, column=0)
        self.__bestAntLabel.grid(row=3, column=0)

        GA = ga.GA(GAframe, coords=coords, scale=scale, radius=3, genNum=1000)
        GA.grid(row=0, column=0)
        self.__genLabel = tk.Label(GAframe, text=f"Generation : 0", font=("Aerial", 20))
        self.__GAcurLabel = tk.Label(GAframe, text="Current : 0", font=("Aerial", 20))
        self.__bestGeneLabel = tk.Label(GAframe, text=f"Best : {float('inf')}", font=("Aerial", 20))
        self.__genLabel.grid(row=1, column=0)
        self.__GAcurLabel.grid(row=2, column=0)
        self.__bestGeneLabel.grid(row=3, column=0)

        window.bind("<Button-3>", lambda e : self.__run(e, SA, ACO, GA))
        # SA.bind("<s>", SA.stop)
        # ACO.bind("<s>", ACO.stop)
        window.bind("<s>", lambda e : self.__stop(e, SA, ACO))
        # window.bind("<MouseWheel>", lambda e : self.__zoom(e, SA, ACO, GA))
        window.mainloop()



    def __run(self, e, sa, aco, ga):
        threading.Thread(target=sa.run, args=[e, self.__tempLabel, self.__bestLabel, self.__SAcurLabel]).start()
        threading.Thread(target=aco.run, args=[e, self.__iterLabel, self.__bestAntLabel, self.__ACOcurLabel]).start()
        threading.Thread(target=ga.run, args=[e, self.__genLabel, self.__bestGeneLabel, self.__GAcurLabel]).start()

    def __zoom(self, e, sa, aco, ga):
        sa.zoom(e)
        ga.zoom(e)
        aco.zoom(e)

    def __stop(self, e, sa, aco):
        sa.stop(e)
        aco.stop(e)

if __name__ == '__main__':
    coords = ReadTSP.readTSP("../TSP Problem/tsp_folder/berlin52.txt", scale=0.25)
    GUI(coords, 0.25)