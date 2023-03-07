import tsplib95

def readTSP(filepath:str, scale):
    name = ""
    num = 0
    coords = []
    with open(filepath, "r") as tsp:
        line = tsp.readlines()

        for co in line:
            if co == "EOF\n":
                break
            co = co.strip()
            co = co.split(" ")
            while True:
                try:
                    co.remove("")
                except ValueError:
                    break
            x, y = float(co[1]) * scale, float(co[2]) * scale
            coords.append([x, y])
        # for c in coords:
        #     print(c)
        return coords
if __name__ == '__main__':
    # readTSP(r"C:\Users\User\Desktop\AI Algorithm\Console for Algorithm\berlin52.tsp", 2)
    p = tsplib95.load("tsp_folder/burma14.tsp")
    print(p.node_coords)