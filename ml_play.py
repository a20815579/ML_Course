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
        self.coin_num = 0
        self.computer_cars = []
        self.coins_pos = []
        print("Initial ml script")
        pass

    def update(self, scene_info):
        """
        cars: 9 grid relative position
        |    |    |    |
        |  1 |  2 |  3 |
        |    |  5 |    |
        |  4 | acb|  6 |
        |    |    |    |
        |  7 |  8 |  9 |
        |    |    |    |

        coins: 3 grid relative position
        |    |    |    |
        |  1 |  2 |  3 |
        |    |  c |    |
        |    |    |    |
        """
        def check_grid():
            grid = set()
            coin_grid = set()
            speed_ahead = 100
            close_coin = 0
            coin_distance = 1000

            for coin in scene_info["coins"]:
                if self.car_pos[1] - coin[1] < -80: # coin is behind
                    continue
                coin_lanes = coin[0] // 70

                if self.car_lane - 1 == coin_lanes:
                    coin_grid.add(1)
                    if self.car_pos[1] - coin[1] < coin_distance:
                        coin_distance = self.car_pos[1] - coin[1]
                        close_coin = 1
                elif self.car_lane == coin_lanes:
                    coin_grid.add(2)
                    if self.car_pos[1] - coin[1] < coin_distance:
                        coin_distance = self.car_pos[1] - coin[1]
                        close_coin = 2
                elif self.car_lane + 1 == coin_lanes:
                    coin_grid.add(3)
                    if self.car_pos[1] - coin[1] < coin_distance:
                        coin_distance = self.car_pos[1] - coin[1]
                        close_coin = 3

            if self.car_lane == 0: # left bound
                grid.add(1)
                grid.add(4)
                # grid.add(7)
            elif self.car_lane == 8: # right bound
                grid.add(3)
                grid.add(6)
                # grid.add(9)

            for car in scene_info["cars_info"]:
                if car["id"] == self.player_no: # my car
                    continue
                x = self.car_pos[0] - car["pos"][0] # x relative position
                y = self.car_pos[1] - car["pos"][1] # y relative position
                lanes = car["pos"][0] // 70 # car lane

                if self.car_lane == lanes:
                    if y > 0 and y < 250:
                        grid.add(2)
                        if y < 150:
                            speed_ahead = car["velocity"]
                            grid.add(5)
                    if y >= -80 and y <= 80 and x > 0 and x < 50:
                        grid.add('a')
                    elif y >= -80 and y <= 80 and x < 0 and x > -50:
                        grid.add('b')
                    # elif y < 0 and y > -120:
                    #     grid.add(8)
                elif self.car_lane + 1 == lanes:
                    if y > 80 and y < 250:
                        grid.add(3)
                    elif y < -80 and y > -120 and car["velocity"] > self.car_vel:
                        grid.add(9)
                    elif y < 80 and y > -80:
                        grid.add(6)
                elif self.car_lane - 1 == lanes:
                    if y > 80 and y < 250:
                        grid.add(1)
                    elif y < -80 and y > -120 and car["velocity"] > self.car_vel:
                        grid.add(7)
                    elif y < 80 and y > -80:
                        grid.add(4)
            return move(grid = grid, speed_ahead = speed_ahead, coin_grid = coin_grid, close_coin = close_coin, coin_distance = coin_distance)

        def move(grid, speed_ahead, coin_grid, close_coin, coin_distance):
            # if self.player_no == 0:
            #     print(self.car_pos[0])
            # print("--")
            if len(grid) == 0:
                if close_coin == 1:
                    return ["SPEED", "MOVE_LEFT"]
                elif close_coin == 3:
                    return ["SPEED", "MOVE_RIGHT"]
                else:
                    # Back to lane center
                    if abs(self.car_pos[0] - self.lanes[self.car_lane]) < 3:
                        return ["SPEED"]
                    if self.car_pos[0] > self.lanes[self.car_lane] and ('a' not in grid):
                        return ["SPEED", "MOVE_LEFT"]
                    elif self.car_pos[0] < self.lanes[self.car_lane] and ('b' not in grid):
                        return ["SPEED", "MOVE_RIGHT"]
                    else: return ["SPEED"]
            else:
                if (2 not in grid): # forward has no car
                    if close_coin == 1 and (1 not in grid) and (4 not in grid) and (7 not in grid) and ('a' not in grid):
                        return ["SPEED", "MOVE_LEFT"]
                    elif close_coin == 3 and (3 not in grid) and (6 not in grid) and (9 not in grid) and ('b' not in grid):
                        return ["SPEED", "MOVE_RIGHT"]
                    else:
                        # Back to lane center
                        if abs(self.car_pos[0] - self.lanes[self.car_lane]) < 3:
                            return ["SPEED"]
                        if self.car_pos[0] > self.lanes[self.car_lane] and ('a' not in grid):
                            return ["SPEED", "MOVE_LEFT"]
                        elif self.car_pos[0] < self.lanes[self.car_lane] and ('b' not in grid):
                            return ["SPEED", "MOVE_RIGHT"]
                        else: return ["SPEED"]
                else: # 2 in grid
                    if (5 in grid): # NEED to BRAKE
                        if (4 not in grid) and (1 not in grid) and ('a' not in grid): # turn left
                            if self.car_vel < speed_ahead:
                                return ["SPEED", "MOVE_LEFT"]
                            else:
                                return ["BRAKE", "MOVE_LEFT"]
                        elif (6 not in grid) and (3 not in grid) and ('b' not in grid): # turn right
                            if self.car_vel < speed_ahead:
                                return ["SPEED", "MOVE_RIGHT"]
                            else:
                                return ["BRAKE", "MOVE_RIGHT"]
                        elif (4 not in grid) and ('a' not in grid): # turn right
                            if self.car_vel < speed_ahead:
                                return ["SPEED", "MOVE_LEFT"]
                            else:
                                return ["BRAKE", "MOVE_LEFT"]
                        elif (6 not in grid) and ('b' not in grid): # turn left
                            if self.car_vel < speed_ahead:
                                return ["SPEED", "MOVE_RIGHT"]
                            else:
                                return ["BRAKE", "MOVE_RIGHT"]
                        else :
                            if self.car_vel < speed_ahead:  # BRAKE
                                return ["SPEED"]
                            else:
                                return ["BRAKE"]
                    else: # 5 not in grid
                        if close_coin == 2:
                            # Back to lane center
                            if abs(self.car_pos[0] - self.lanes[self.car_lane]) < 3:
                                return ["SPEED"]
                            if self.car_pos[0] > self.lanes[self.car_lane] and ('a' not in grid):
                                return ["SPEED", "MOVE_LEFT"]
                            elif self.car_pos[0] < self.lanes[self.car_lane] and ('b' not in grid):
                                return ["SPEED", "MOVE_RIGHT"]
                            else: return ["SPEED"]
                        if close_coin == 1 and (1 not in grid) and (4 not in grid) and (7 not in grid) and ('a' not in grid):
                            return ["SPEED", "MOVE_LEFT"]
                        if close_coin == 3 and (3 not in grid) and (6 not in grid) and (9 not in grid) and ('b' not in grid):
                            return ["SPEED", "MOVE_RIGHT"]
                        if close_coin == 1 and (1 not in grid) and (4 not in grid) and ('a' not in grid):
                            return ["SPEED", "MOVE_LEFT"]
                        if close_coin == 3 and (3 not in grid) and (6 not in grid) and ('b' not in grid):
                            return ["SPEED", "MOVE_RIGHT"]
                        if close_coin == 1 and (4 not in grid) and (7 not in grid) and ('a' not in grid):
                            return ["SPEED", "MOVE_LEFT"]
                        if close_coin == 3 and (6 not in grid) and (9 not in grid) and ('b' not in grid):
                            return ["SPEED", "MOVE_RIGHT"]
                        if (1 not in grid) and (4 not in grid) and (7 not in grid) and ('a' not in grid): # turn left
                            return ["SPEED", "MOVE_LEFT"]
                        if (3 not in grid) and (6 not in grid) and (9 not in grid) and ('b' not in grid): # turn right
                            return ["SPEED", "MOVE_RIGHT"]
                        if (1 not in grid) and (4 not in grid) and ('a' not in grid): # turn left
                            return ["SPEED", "MOVE_LEFT"]
                        if (3 not in grid) and (6 not in grid) and ('b' not in grid): # turn right
                            return ["SPEED", "MOVE_RIGHT"]
                        if (4 not in grid) and (7 not in grid) and ('a' not in grid): # turn left
                            return ["MOVE_LEFT"]
                        if (6 not in grid) and (9 not in grid) and ('b' not in grid): # turn right
                            return ["MOVE_RIGHT"]
                        return ["SPEED"]

        if len(scene_info[self.player]) != 0:
            self.car_pos = scene_info[self.player]
        for car in scene_info["cars_info"]:
            if car["id"] == self.player_no:
                self.car_vel = car["velocity"]
                self.coin_num = car["coin_num"]
        self.computer_cars = scene_info["computer_cars"]
        if scene_info.__contains__("coins"):
            self.coins_pos = scene_info["coins"]

        if scene_info["status"] != "ALIVE":
            return "RESET"

        self.car_lane = self.car_pos[0] // 70
        return check_grid()

    def reset(self):
        """
        Reset the status
        """
        pass