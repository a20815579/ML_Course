import time

class MLPlay:
    def __init__(self, player):
        self.player = player
        if self.player == "player1":
            self.player_no = 0
        elif self.player == "player2":
            self.player_no = 1
        elif self.player == "player3":
            self.player_no = 2
        elif self.player == "player4":
            self.player_no = 3
        self.car_vel = 0
        self.car_pos = ()
        self.returnArr = []
        self.left = True
        self.emeBrake = False
        self.emeDist = -999
        pass

    def update(self, scene_info):
        """
        Generate the command according to the received scene information
        """

        def getAns():

            self.returnArr = []
            carsX = []
            for car in scene_info["cars_info"]:
                if car['pos'][1] - 40 <= self.car_pos[1] + 40 and car['id'] != self.player_no:
                    carsX.append(car['pos'][0])
            carsX.sort()
            carGap = []
            maxGap = 0
            if len(carsX) > 0:
                for i, num in enumerate(carsX):
                    if i == 0:
                        carGap.append((-35, num + 35))
                        maxGap = num + 35
                        continue
                    carGap.append((carsX[i - 1], num - carsX[i - 1]))
                    if num - carsX[i - 1] > maxGap:
                        maxGap = num - carsX[i - 1]
                    if i == (len(carsX) - 1):
                        carGap.append((num, 595 + 70 - num))
                        if 595 + 70 - num > maxGap:
                            maxGap = 595 + 70 - num
                dist = []
                for element in carGap:
                    if element[1] == maxGap and maxGap >= 90:
                        dist.append(element[0] + element[1] / 2)
                dist[:] = [x - self.car_pos[0] for x in dist]
                minDist = 999
                for num in dist:
                    if abs(minDist) > abs(num):
                        minDist = num
                if abs(minDist) > 1:
                    if minDist > 0:
                        if minDist != 999:
                            self.returnArr.append("MOVE_RIGHT")
                    else:
                        self.returnArr.append("MOVE_LEFT")
            if not("MOVE_RIGHT" in self.returnArr or "MOVE_LEFT" in self.returnArr):
                changeLane = False
                block = ()
                for car in scene_info["cars_info"]:
                    if abs(car["pos"][0] - self.car_pos[0]) < 43 and self.car_vel > car["velocity"] and self.car_pos[1] - car["pos"][1] - 80 > 0:
                        if self.car_pos[1] - car["pos"][1] - 80 < 240:#((self.car_pos[1] - car["pos"][1] - 80) / (self.car_vel - car["velocity"])) * 2 <= abs(car["pos"][0] - self.car_pos[0]) + 25:
                            changeLane = True
                            block = ((car["pos"][0], car["pos"][1]))
                            print(self.player, end = " : ")
                            break
                carsX = []
                if changeLane:
                    for car in scene_info["cars_info"]:
                        if (car['pos'][1] <= self.car_pos[1] and car["id"] > 100) or (car['pos'][1] -40 <= self.car_pos[1] + 40 and car["id"] < 100 and car["id"] != self.player_no):
                            if abs(car["pos"][0] - block[0]) >= 43 and abs(car["pos"][0] - block[0]) < 88 and car["id"] != self.player_no:
                                carsX.append((car['pos'][0], car['pos'][1]))
                    for carX in carsX:
                        for carX2 in carsX:
                            if not(carX[0] == carX2[0] and carX[1] == carX2[1]) and abs(carX[0] - carX2[0]) <= 45:
                                if carX[1] > carX2[1]:
                                    carsX.remove(carX2)
                                    break
                                else:
                                    carsX.remove(carX)
                                    break
                    minX = 9999
                    if len(carsX) > 0:
                        for car in carsX:
                            if car[1] < minX:
                                minX = car[1]
                        for car in carsX:
                            if car[1] == minX and minX < 9999 and car[1] < block[1]:
                                #print(self.player, "destination", sep = " -> ", end = " : ")
                                #print(car)
                                if abs(self.car_pos[0] - car[0]) > 1:
                                    if self.car_pos[0] - car[0] > 0:
                                        self.returnArr.append("MOVE_LEFT")
                                        #print("MOVE_LEFT")
                                    else:
                                        self.returnArr.append("MOVE_RIGHT")
                                        #print("MOVE_RIGHT")
            """
            if "MOVE_RIGHT" in self.returnArr:
                for car in scene_info["cars_info"]:
                    if car["pos"][0] - self.car_pos[0] < 45 and car["pos"][0] - self.car_pos[0] > 0 and abs(car["pos"][1] - self.car_pos[1]) < 90:
                        self.returnArr.remove("MOVE_RIGHT")
                        break
            
            
            
            if self.left and len(self.car_pos) > 0 and self.car_pos[0] <= 35:
                self.left = False
            elif not self.left and len(self.car_pos) > 0 and self.car_pos[0] >= 595:
                self.left = True
                
            if self.left:
                if "MOVE_RIGHT" in self.returnArr:
                    self.returnArr.remove("MOVE_RIGHT")
                if "MOVE_LEFT" not in self.returnArr:
                    self.returnArr.append("MOVE_LEFT")
            else:
                if "MOVE_RIGHT" not in self.returnArr:
                    self.returnArr.append("MOVE_RIGHT")
                if "MOVE_LEFT" in self.returnArr:
                    self.returnArr.remove("MOVE_LEFT")
            
            if "MOVE_LEFT" in self.returnArr:
                for car in scene_info["cars_info"]:
                    if self.car_pos[0] - car["pos"][0] <= 45 and self.car_pos[0] - car["pos"][0] > 0 and abs(car["pos"][1] - self.car_pos[1]) < 90:
                        self.returnArr.remove("MOVE_LEFT")
                        break
            """

            if "MOVE_RIGHT" in self.returnArr and self.car_pos[0] >= 595:
                self.returnArr.remove("MOVE_RIGHT")
            elif "MOVE_LEFT" in self.returnArr and self.car_pos[0] <= 35:
                self.returnArr.remove("MOVE_LEFT")

            self.returnArr.append("SPEED")
            
            controlSpeed()
            """
            if self.player_no == 0:
                print(self.returnArr)
                #print()
            """
            return None#self.returnArr

        def controlSpeed():
            """
                    pos_2     pos_4

            pos_1        mycar        pos_3

            """
            pos_1 = {}
            pos_2 = {}
            pos_3 = {}
            pos_4 = {}
            temp = []
            for car in scene_info["cars_info"]:
                if abs(car["pos"][0] - self.car_pos[0]) < 43 and car["pos"][1] - 40 < self.car_pos[1] + 40 and car["id"] != self.player_no:
                    temp.append(car)
            if len(temp) != 0:
                maxY2 = -999
                maxY4 = -999
                for car in temp:
                    if car["pos"][1] > maxY2 and car["pos"][0] <= self.car_pos[0]:
                        maxY2 = car["pos"][1]
                    elif car["pos"][1] > maxY4 and car["pos"][0] > self.car_pos[0]:
                        maxY4 = car["pos"][1]
                for car in temp:
                    if car["pos"][1] == maxY2:
                        pos_2.update(car)
                    elif car["pos"][1] == maxY4:
                        pos_4.update(car)
            temp = []
            for car in scene_info["cars_info"]:
                if car["pos"][0] - self.car_pos[0] >= 43 and car["pos"][0] - self.car_pos[0] <= 83 and car["id"] != self.player_no:
                    if self.car_pos[1] + 40 >= (car["pos"][1] - 45):
                        temp.append(car)
                        if 15 > car["velocity"] and (self.car_pos[1] - car["pos"][1] - 90) > 0 and ((self.car_pos[1] - car["pos"][1] - 90) / (15 - car["velocity"])) * 2 > car["pos"][0] - self.car_pos[0] + 45:
                            temp.remove(car)
            if len(temp) != 0:
                maxY = -999
                for car in temp:
                    if car["pos"][1] > maxY:
                        maxY = car["pos"][1]
                for car in temp:
                    if car["pos"][1] == maxY:
                        pos_3.update(car)
                        break
            temp = []
            for car in scene_info["cars_info"]:
                if self.car_pos[0] - car["pos"][0] >= 43 and self.car_pos[0] - car["pos"][0] <= 83 and car["id"] != self.player_no:
                    if self.car_pos[1] >= (car["pos"][1] - 85):
                        temp.append(car)
                        if 15 > car["velocity"] and (self.car_pos[1] - car["pos"][1] - 90) > 0 and ((self.car_pos[1] - car["pos"][1] - 90) / (15 - car["velocity"])) * 2 > self.car_pos[0] - car["pos"][0] + 45:
                            temp.remove(car)
            if len(temp) != 0:
                maxY = -999
                for car in temp:
                    if car["pos"][1] > maxY:
                        maxY = car["pos"][1]
                for car in temp:
                    if car["pos"][1] == maxY:
                        pos_1.update(car)
                        break
            if len(pos_2) != 0:
                if self.car_pos[1] - pos_2["pos"][1] - 80 <=  5 + 8 * (self.car_vel + 1.7 - pos_2["velocity"]):
                    follow(pos_2)
            if len(pos_4) != 0:
                if self.car_pos[1] - pos_4["pos"][1] - 80 <=  5 + 8 * (self.car_vel + 1.7 - pos_4["velocity"]):
                    follow(pos_4)
            if "MOVE_RIGHT" in self.returnArr and len(pos_3) > 0:
                if len(pos_4) != 0:#both of pos4 and pos3 are occupied
                    if pos_3["pos"][1] - pos_4["pos"][1] - 80 > 90:# 從pos3上面過
                        if pos_3["pos"][0] - self.car_pos[0] <= 45 and pos_3["pos"][0] - self.car_pos[0] > 0:# and car["pos"][1] - self.car_pos[1] < 85
                            self.returnArr.remove("MOVE_RIGHT")
                    else:#從pos3下面過
                        if pos_3["pos"][0] - self.car_pos[0] <= 45 and pos_3["pos"][0] - self.car_pos[0] > 0:# and (self.car_pos[1] - 40) - (car["pos"][1] + 40) < 5 + (self.car_vel - car["velocity"] + 1.7)
                            self.returnArr.remove("MOVE_RIGHT")
                        follow(car = pos_3)
                        if self.car_pos[1] - pos_3["pos"][1] > 85:
                            self.returnArr.append("MOVE_RIGHT")
                elif len(pos_2) != 0:#both of pos2 and pos3 are occupied，四不在
                    if pos_3["pos"][1] - pos_2["pos"][1] - 80 > 90:# 從pos3上面過
                        if pos_3["pos"][0] - self.car_pos[0] <= 45 and pos_3["pos"][0] - self.car_pos[0] > 0:# and car["pos"][1] - self.car_pos[1] < 85
                            self.returnArr.remove("MOVE_RIGHT")
                    else:#從pos3下面過
                        if pos_3["pos"][0] - self.car_pos[0] <= 45 and pos_3["pos"][0] - self.car_pos[0] > 0:# and (self.car_pos[1] - 40) - (car["pos"][1] + 40) < 5 + (self.car_vel - car["velocity"] + 1.7)
                            self.returnArr.remove("MOVE_RIGHT")
                        follow(car = pos_3)
                        if self.car_pos[1] - pos_3["pos"][1] > 85:
                            self.returnArr.append("MOVE_RIGHT")
                else:# 從pos3上面過
                    if pos_3["pos"][0] - self.car_pos[0] <= 45 and pos_3["pos"][0] - self.car_pos[0] > 0:# and car["pos"][1] - self.car_pos[1] < 85
                        self.returnArr.remove("MOVE_RIGHT")
            if "MOVE_LEFT" in self.returnArr and len(pos_1) > 0:
                if len(pos_4) != 0:#both of pos4 and pos1 are occupied
                    if pos_1["pos"][1] - pos_4["pos"][1] - 80 > 90:# 從pos1上面過
                        if self.car_pos[0] - pos_1["pos"][0] <= 45 and self.car_pos[0] - pos_1["pos"][0] > 0:# and car["pos"][1] - self.car_pos[1] < 85
                            self.returnArr.remove("MOVE_LEFT")
                    else:#從pos1下面過
                        if self.car_pos[0] - pos_1["pos"][0] <= 45 and self.car_pos[0] - pos_1["pos"][0] > 0:# and (self.car_pos[1] - 40) - (car["pos"][1] + 40) < 5 + (self.car_vel - car["velocity"] + 1.7)
                            self.returnArr.remove("MOVE_LEFT")
                        follow(car = pos_1)
                        if self.car_pos[1] - pos_1["pos"][1] > 85:
                            self.returnArr.append("MOVE_LEFT")
                elif len(pos_2) != 0:#both of pos2 and pos1 are occupied
                    if pos_1["pos"][1] - pos_2["pos"][1] - 80 > 90:# 從pos1上面過
                        if self.car_pos[0] - pos_1["pos"][0] <= 45 and self.car_pos[0] - pos_1["pos"][0] > 0:# and car["pos"][1] - self.car_pos[1] < 85
                            self.returnArr.remove("MOVE_LEFT")
                    else:#從pos1下面過
                        if self.car_pos[0] - pos_1["pos"][0] <= 45 and self.car_pos[0] - pos_1["pos"][0] > 0:# and (self.car_pos[1] - 40) - (car["pos"][1] + 40) < 5 + (self.car_vel - car["velocity"] + 1.7)
                            self.returnArr.remove("MOVE_LEFT")
                        follow(car = pos_1)
                        if self.car_pos[1] - pos_1["pos"][1] > 85:
                            self.returnArr.append("MOVE_LEFT")
                else:# 從pos1上面過
                    if self.car_pos[0] - pos_1["pos"][0] <= 45 and self.car_pos[0] - pos_1["pos"][0] > 0:# and car["pos"][1] - self.car_pos[1] < 85
                        self.returnArr.remove("MOVE_LEFT")
            """
            if len(self.car_pos) > 0:
                if abs(self.car_pos[0] - self.emeDist) <= 1:
                    self.emeBrake = False
                    self.emeDist = -999
                if len(pos_2) > 0 and self.car_vel - pos_2["velocity"] > 7:
                    self.emeBrake = True
                    if abs((pos_2["pos"][0] - 45) - self.car_pos[0]) >= abs((pos_2["pos"][0] + 45) - self.car_pos[0]):
                        self.emeDist = (pos_2["pos"][0] + 45)
                    else:
                        self.emeDist = (pos_2["pos"][0] - 45)
                elif len(pos_4) > 0 and self.car_vel - pos_4["velocity"] > 7:
                    self.emeBrake = True
                    if abs((pos_4["pos"][0] - 45) - self.car_pos[0]) >= abs((pos_4["pos"][0] + 45) - self.car_pos[0]):
                        self.emeDist = (pos_4["pos"][0] + 45)
                    else:
                        self.emeDist = (pos_4["pos"][0] - 45)
                if self.emeBrake:
                    print("emergency brake!!")
                    print("emergency brake!!")
                    print("emergency brake!!")
                    print("emergency brake!!")
                    print("emergency brake!!")
                    print("emergency brake!!")
                    print("emergency brake!!")
                    print("emergency brake!!")
                    print("emergency brake!!")
                    print("emergency brake!!")
                    print("emergency brake!!")
                    print("emergency brake!!")
                    print("emergency brake!!")
                    print("emergency brake!!")
                    if len(pos_4) == 0 and len(pos_2) == 0:
                        pass
                    elif len(pos_2) > 0 and len(pos_4) == 0:
                        follow(pos_2)
                    elif len(pos_2) == 0 and len(pos_4) > 0:
                        follow(pos_4)
                    elif pos_2["velocity"] <= pos_4["velocity"]:
                        follow(pos_2)
                    else:
                        follow(pos_4)
                    if self.emeDist - self.car_pos[0] > 0:
                        if "MOVE_RIGHT" not in self.returnArr:
                            self.returnArr.append("MOVE_RIGHT")
                        if "MOVE_LEFT" in self.returnArr:
                            self.returnArr.remove("MOVE_LEFT")
                        if len(pos_3) == 0:
                            self.returnArr.remove("MOVE_RIGHT")
                        elif pos_3["pos"][0] - self.car_pos[0] <= 45 and pos_3["pos"][0] - self.car_pos[0] > 0:
                            self.returnArr.remove("MOVE_RIGHT")
                    else:
                        if "MOVE_RIGHT" in self.returnArr:
                            self.returnArr.remove("MOVE_RIGHT")
                        if "MOVE_LEFT" not in self.returnArr:
                            self.returnArr.append("MOVE_LEFT")
                        if len(pos_1) == 0:
                            self.returnArr.remove("MOVE_LEFT")
                        elif self.car_pos[0] - pos_1["pos"][0] <= 45 and self.car_pos[0] - pos_1["pos"][0] > 0:
                            self.returnArr.remove("MOVE_LEFT")
            


            if self.player_no == 0:
                print(pos_1, end = ", ")
                print(pos_2, end = ", ")
                print(pos_4, end = ", ")
                print(pos_3)
                print(self.car_pos)
            """
            return None
        def follow(car):
            if (self.car_pos[1] - 40) - (car["pos"][1] + 40) <= 5 + 8 * (self.car_vel - car["velocity"] + 1.7):
                if self.car_vel > car["velocity"] - 5:
                    if "SPEED" in self.returnArr:
                        self.returnArr.remove("SPEED")
                    if "BRAKE" not in self.returnArr:
                        self.returnArr.append("BRAKE")
                else:
                    keepSpeed(car["velocity"] - 4.7)
            else:
                keepSpeed(car["velocity"] + 1)
            return None

        def keepSpeed(speed):
            if self.car_vel >= speed:
                if "SPEED" in self.returnArr:
                    self.returnArr.remove("SPEED")
                if "BRAKE" in self.returnArr:
                    self.returnArr.remove("BRAKE")
            else:
                if "SPEED" not in self.returnArr:
                    self.returnArr.append("SPEED")
                if "BRAKE" in self.returnArr:
                    self.returnArr.remove("BRAKE")
            return None


        #tstart = time.time()
        if len(scene_info[self.player]) != 0:
            self.car_pos = scene_info[self.player]
            for car in scene_info["cars_info"]:
                if car["id"]==self.player_no:
                    self.car_vel = car["velocity"]
                    break
        getAns()
        """
        tend = time.time()
        if tend - tstart > 0.0005:
            print(self.player, end = " : ")
            print(tend - tstart)
        """
        if scene_info["status"] != "ALIVE":
            return "RESET"
        
        return self.returnArr


    def reset(self):
        """
        Reset the status
        """
        pass
