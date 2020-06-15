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
        self.car_vel = 0                            # speed initial
        self.car_pos = (0,0)                        # pos initial
        self.car_lane = self.car_pos[0] // 70       # lanes 0 ~ 8
        self.lanes = [35, 105, 175, 245, 315, 385, 455, 525, 595]  # lanes center
        self.priority = 0
        self.start = 0
        self.now_x = 0
        self.last_x = 0
        pass

    def update(self, scene_info):
        def check_pos():
            pos_dict = {}
            if self.car_pos[0] < 140:
                pos_dict[2] = [-1,0]
            if self.car_pos[0] < 70:
                pos_dict[3] = [-1,0]
            if self.car_pos[0] > 560:
                pos_dict[5] = [-1,0]
            if self.car_pos[0] > 485:
                pos_dict[6] = [-1,0]

            for car in scene_info["cars_info"]:
                if car["id"] != self.player_no:
                    x = car["pos"][0] - self.car_pos[0]  # x relative position
                    y = self.car_pos[1] - car["pos"][1] # y relative position
                    v = round(car["velocity"],2)
                    if x <= 40 and x >= -40 :      
                        if y > -40 and y < 400:
                            if not(4 in pos_dict and pos_dict[4][1] < y):
                                pos_dict[4] = [v, y]
                    elif x >= -105 and x < -40 :
                        if y > -85 and y < 400:
                            if not(3 in pos_dict and pos_dict[3][1] < y):
                                pos_dict[3] = [v, y]
                    elif x <= 105 and x > 40 :
                        if y > -85 and y < 400:
                            if not(5 in pos_dict and pos_dict[5][1] < y):
                                pos_dict[5] = [v, y]
                    elif x >= -175 and x < -105 :
                        if y > -85 and y < 400:
                            if not(2 in pos_dict and pos_dict[2][1] < y):
                                pos_dict[2] = [v, y]
                    elif x <= 175 and x > 105 :
                        if y > -85 and y < 400:
                            if not(6 in pos_dict and pos_dict[6][1] < y):
                                pos_dict[6] = [v, y]
            return move(pos_dict)
            
        def move(pos_dict): 
            return_list = []
            speed = False
            brake = False
            if self.last_x % 70 != 0 and (self.last_x + self.now_x)/2 % 70 == 0:
                self.priority = 1
            # elif last_x % 70 == 0 and now_x % 70 != 0:
            #     priority = 0
            elif self.last_x not in self.lanes and self.now_x in self.lanes:
                self.priority = 0

            if 4 not in pos_dict or pos_dict[4][1] > 300:
                speed = True
            elif pos_dict[4][1] > 120 and self.car_vel < pos_dict[4][0]:
                speed = True
            elif pos_dict[4][1] > 250 and self.car_vel - pos_dict[4][0] < 4:
                speed = True
            elif pos_dict[4][1] > 200 and self.car_vel - pos_dict[4][0] < 3:
                speed = True
            elif pos_dict[4][1] < 100 and self.car_vel > pos_dict[4][0]:
                brake = True

            if self.priority: #move to center
                if self.car_pos[0] > self.lanes[self.car_lane]:
                    return_list.append("MOVE_LEFT")
                elif self.car_pos[0] < self.lanes[self.car_lane]:
                    return_list.append("MOVE_RIGHT")               
            else:
                if 4 in pos_dict:            
                    if(pos_dict[4][0] < 5): #front car brake suddenly
                        if(3 not in pos_dict):
                            return_list.append("MOVE_LEFT")
                        elif(5 not in pos_dict):
                            return_list.append("MOVE_RIGHT")
                        elif(pos_dict[3][1] > pos_dict[5][1] and pos_dict[3][1] > 100):
                            return_list.append("MOVE_LEFT")
                        elif(pos_dict[3][1] < pos_dict[5][1] and pos_dict[5][1] > 100):
                            return_list.append("MOVE_RIGHT")
                        else:
                            brake = True
                    else:
                        if (3 not in pos_dict and 5 not in pos_dict):    
                            if(2 not in pos_dict):
                                return_list.append("MOVE_LEFT")                        
                            else:
                                return_list.append("MOVE_RIGHT")
                        elif (3 not in pos_dict):
                            return_list.append("MOVE_LEFT")
                        elif (5 not in pos_dict):
                            return_list.append("MOVE_RIGHT")
                        else:
                            if (2 not in pos_dict and 6 not in pos_dict):    
                                if(pos_dict[3][1] > pos_dict[5][1] and pos_dict[3][1] > 180):        
                                    return_list.append("MOVE_LEFT")
                                elif(pos_dict[5][1] > pos_dict[3][1] and pos_dict[5][1] > 180):
                                    return_list.append("MOVE_RIGHT")
                            elif(2 not in pos_dict and pos_dict[3][1] > 180): #revise
                                return_list.append("MOVE_LEFT")
                            elif(6 not in pos_dict and pos_dict[5][1] > 180): #revise
                                return_list.append("MOVE_RIGHT")
                            elif(pos_dict[3][1] > pos_dict[4][1]):
                                return_list.append("MOVE_LEFT")
                            elif(pos_dict[5][1] > pos_dict[4][1]):
                                return_list.append("MOVE_RIGHT") 
            if speed:
                return_list.append("SPEED")
            if brake:
                return_list.append("BRAKE")
            if return_list == []:
                return_list = [None]
            # if(scene_info["frame"] % 5 == self.player_no):
            #     print(self.player_no," ",pos_dict, " ",return_list)
            return return_list                           
                    
        if len(scene_info[self.player]) != 0:
            self.car_pos = scene_info[self.player]

        for car in scene_info["cars_info"]:
            if car["id"]==self.player_no:
                self.car_vel = car["velocity"]

        if not self.start:
            self.start = 1
        else:
            self.last_x = self.now_x
        self.now_x = self.car_pos[0]

        if scene_info["status"] != "ALIVE":
            return "RESET"
        self.car_lane = self.car_pos[0] // 70
        return check_pos()

    def reset(self):
        """
        Reset the status
        """
        pass