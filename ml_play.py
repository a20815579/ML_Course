"""
The template of the script for the machine learning process in game pingpong
"""

# Import the necessary modules and classes
from mlgame.communication import ml as comm
from pygame.math import Vector2

ready_print = False
print_frame = -1
print_block = 0
print_speedx = 0
print_speedy = 0

def ml_loop(side: str):
    """
    The main loop for the machine learning process
    The `side` parameter can be used for switch the code for either of both sides,
    so you can write the code for both sides in the same script. Such as:
    ```python
    if side == "1P":
        ml_loop_for_1P()
    else:
        ml_loop_for_2P()
    ```
    @param side The side which this script is executed for. Either "1P" or "2P".

    """
    def revise_contact_point(contact_point):
        if contact_point > 195:
            return 195
        elif contact_point < 0:
            return 0
        return contact_point

    def revise_ball_pred(pred, start_point, speed):
        is_bounce = 1
        if pred > 195:
            is_bounce = -1
            temp = (195 - start_point) // speed
            bias = 195 - (start_point + speed*temp)
            if bias != 0:
                pred = 195 - (pred - 195) + (speed - bias)
            else:
                pred = 195 - (pred - 195)
        elif pred < 0:
            is_bounce = -1
            temp = start_point // speed
            bias = start_point - speed*temp
            if bias != 0:
                pred = -pred - (speed - bias)
            else:
                pred = -pred
        return pred,is_bounce

    def revise_ball_approximate(pred):
        bound = pred // 200 # Determine if it is beyond the boundary
        if (bound > 0): # pred > 200 # fix landing position
            if (bound%2 == 0) : 
                pred = pred - bound*200                    
            else :
                pred = 200 - (pred - 200)
        elif (bound < 0) : # pred < 0
            if (bound%2 ==1) :
                pred = abs(pred - (bound+1) *200)
            else :
                pred = pred + (abs(bound)*200)
        return pred

    def revise_blocker_pred(pred, start_point):
        if (pred > 170):
            temp = (170 - start_point) // 3
            bias = 170 - (start_point + 3*temp)
            if bias != 0:
                pred = 170 - (pred - 170) + (3 - bias)
            else:
                pred = 170 - (pred - 170)
        elif (pred < 0):
            temp = start_point // 3
            bias = start_point - 3*temp
            if bias != 0:
                pred = -pred - (3 - bias)
            else:
                pred = -pred
        return pred         

    def is_collide(ball_x,ball_y,ball_speed_x,ball_speed_y,blocker_x):
        routes = [(Vector2(ball_x, ball_y), Vector2(ball_x+ball_speed_x, ball_y+ball_speed_y)),
                (Vector2(ball_x+5, ball_y), Vector2(ball_x+ball_speed_x+5, ball_y+ball_speed_y)),
                (Vector2(ball_x, ball_y+5), Vector2(ball_x+ball_speed_x, ball_y+ball_speed_y+5)),
                (Vector2(ball_x+5, ball_y+5), Vector2(ball_x+ball_speed_x+5, ball_y+ball_speed_y+5))]

        blocker_bound = [(Vector2(blocker_x,240), Vector2(blocker_x+30,240)),
                        (Vector2(blocker_x,260), Vector2(blocker_x+30,260)),
                        (Vector2(blocker_x,240), Vector2(blocker_x,260)),
                        (Vector2(blocker_x+30,240), Vector2(blocker_x+30,260))]
        '''
        blocker_bound = [(Vector2(blocker_x-5,235), Vector2(blocker_x+35,235)),
                        (Vector2(blocker_x-5,265), Vector2(blocker_x+35,265)),
                        (Vector2(blocker_x-5,235), Vector2(blocker_x-5,265)),
                        (Vector2(blocker_x+35,235), Vector2(blocker_x+35,265))]
        '''
        for route in routes:
            for bound_line in blocker_bound:
                if is_intersect(route, bound_line):
                    return True
        return False
        
    def is_intersect(line_a, line_b) -> bool:
        if (line_a[0] == line_b[0] or line_a[1] == line_b[0] or
            line_a[0] == line_b[1] or line_a[1] == line_b[1]):
            return True
        v0 = line_a[1] - line_a[0]
        v1 = line_b[1] - line_b[0]
        det = v0.x * v1.y - v0.y * v1.x
        if det == 0:
            return False
        du = line_a[0] - line_b[0]
        s_det = v1.x * du.y - v1.y * du.x
        t_det = v0.x * du.y - v0.y * du.x
        if ((det > 0 and 0 <= s_det <= det and 0 <= t_det <= det) or
            (det < 0 and det <= s_det <= 0 and det <= t_det <= 0)):
            return True
        return False

    def predict_direction(blocker_dict, side):
        global ready_print, print_frame, print_speedy, print_speedx 
        ball_speed_x = scene_info["ball_speed"][0]
        ball_speed_y = scene_info["ball_speed"][1]
        blocker_x = scene_info["blocker"][0]                
        speed = abs(ball_speed_y)
        cnt = (415-260) // speed
        #pred_y_no_slice = 415 - speed*cnt if side == 1 else 80 + speed*cnt
        pred_blocker = revise_blocker_pred(blocker_x + blocker_dict*3*(cnt+3), blocker_x)
        #小於或小於等於?
        if ball_speed_x > 0: 
            if scene_info['ball'][0] + ball_speed_x*2 < 195 :
                contact_point = scene_info["ball"][0] + ball_speed_x*2
                if side == 1:            
                    pred_y_right = 415 - speed*cnt
                    pred_right,is_bounce = revise_ball_pred(contact_point + (speed+3)*cnt, contact_point, speed+3)
                    is_collide_this = is_collide(pred_right,pred_y_right,is_bounce*(speed+3),-speed,pred_blocker)
                    print_speedy = -speed
                else:
                    pred_y_right = 80 + speed*cnt
                    pred_right,is_bounce = revise_ball_pred(contact_point + (speed+3)*cnt, contact_point, speed+3)
                    is_collide_this = is_collide(pred_right,pred_y_right,is_bounce*(speed+3),speed,pred_blocker)
                    print_speedy = speed
                if not is_collide_this:
                    print_speedx = is_bounce*(speed+3)
                    print_frame = scene_info['frame']+cnt+2
                    return 2,1,0
                else:
                    return 1,2,1
            elif scene_info['ball'][0] + ball_speed_x >= 195: #下一個frame就反彈
                contact_point = 195 - ball_speed_x
                if side == 1:            
                    pred_y_left = 415 - speed*cnt
                    pred_left,is_bounce = revise_ball_pred(contact_point - (speed+3)*cnt, contact_point, speed+3)
                    is_collide_this = is_collide(pred_left,pred_y_left,-is_bounce*(speed+3),-speed,pred_blocker)
                    print_speedy = -speed
                else:
                    pred_y_left = 80 + speed*cnt
                    pred_left,is_bounce = revise_ball_pred(contact_point - (speed+3)*cnt, contact_point, speed+3)
                    is_collide_this = is_collide(pred_left,pred_y_left,-is_bounce*(speed+3),speed,pred_blocker)
                    print_speedy = speed
                if not is_collide_this:
                    print_speedx = -is_bounce*(speed+3)
                    print_frame = scene_info['frame']+cnt+2
                    return 1,2,0
                else:
                    return 2,1,1
            else:
                return 1,1,2
        else:
            if scene_info['ball'][0] + ball_speed_x*2 > 0 :
                contact_point = scene_info["ball"][0] + ball_speed_x*2
                if side == 1:            
                    pred_y_left = 415 - speed*cnt
                    pred_left,is_bounce = revise_ball_pred(contact_point - (speed+3)*cnt, contact_point, speed+3)
                    is_collide_this = is_collide(pred_left,pred_y_left,-is_bounce*(speed+3),-speed,pred_blocker)
                    print_speedy = -speed
                else:
                    pred_y_left = 80 + speed*cnt
                    pred_left,is_bounce = revise_ball_pred(contact_point - (speed+3)*cnt, contact_point, speed+3)
                    is_collide_this = is_collide(pred_left,pred_y_left,-is_bounce*(speed+3),speed,pred_blocker)
                    print_speedy = speed
                if not is_collide_this:
                    print_speedx = -is_bounce*(speed+3)
                    print_frame = scene_info['frame']+cnt+2
                    return 1,2,0
                else:
                    return 2,1,1
            elif scene_info['ball'][0] + ball_speed_x <= 0 :
                contact_point = abs(ball_speed_x)
                if side == 1:            
                    pred_y_right = 415 - speed*cnt
                    pred_right,is_bounce = revise_ball_pred(contact_point + (speed+3)*cnt, contact_point, speed+3)
                    is_collide_this = is_collide(pred_right,pred_y_right,is_bounce*(speed+3),-speed,pred_blocker)
                    print_speedy = -speed
                else:
                    pred_y_right = 80 + speed*cnt
                    pred_right,is_bounce = revise_ball_pred(contact_point + (speed+3)*cnt, contact_point, speed+3)
                    is_collide_this = is_collide(pred_right,pred_y_right,is_bounce*(speed+3),speed,pred_blocker)
                    print_speedy = speed
                if not is_collide_this:
                    print_speedx = is_bounce*(speed+3)
                    print_frame = scene_info['frame']+cnt+2
                    return 2,1,0
                else:
                    return 1,2,1
            else:
                return 2,2,2

    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here
    ball_served = False
    former_blocker = 85
    former_ball_y = 415
    prepare_cal = 0
    second_last_command = 0
    last_command = 0
    will_print1 = False
    will_print2 = False
    will_print = False
    case = -1
    global ready_print, print_frame, print_speedy, print_speedx

    def move_to(player, pred) : #move platform to predicted position to catch ball 
        if player == '1P':
            if scene_info["platform_1P"][0]+17.5  > (pred-3) and scene_info["platform_1P"][0]+17.5 < (pred+3): return 0 # NONE
            elif scene_info["platform_1P"][0]+17.5 <= (pred-3) : return 1 # goes right
            else : return 2 # goes left
        else :
            if scene_info["platform_2P"][0]+17.5  > (pred-3) and scene_info["platform_2P"][0]+17.5 < (pred+3): return 0 # NONE
            elif scene_info["platform_2P"][0]+17.5 <= (pred-3) : return 1 # goes right
            else : return 2 # goes left

    def pred_1P(): 
        if scene_info["ball_speed"][1] > 0 : 
            x = (scene_info["platform_1P"][1]-scene_info["ball"][1]-5) // scene_info["ball_speed"][1]
            if (scene_info["platform_1P"][1]-scene_info["ball"][1]-5) % scene_info["ball_speed"][1] != 0:
                x = x + 1
            x2 = (scene_info["platform_1P"][1]-scene_info["ball"][1]-5) / scene_info["ball_speed"][1]
            pred = scene_info["ball"][0]+(scene_info["ball_speed"][0]*x2)
            if scene_info["ball"][1] > 275:
                pred, is_bounce = revise_ball_pred(pred, scene_info["ball"][0], abs(scene_info["ball_speed"][0]))                
            else:
                pred = revise_ball_approximate(pred)
            return pred
        else :
            return 100

    def pred_2P():
        if scene_info["ball_speed"][1] > 0 : 
            return 100
        else : 
            x = (scene_info["platform_2P"][1]+30-scene_info["ball"][1]) // scene_info["ball_speed"][1] 
            if (scene_info["platform_2P"][1]+30-scene_info["ball"][1]) % scene_info["ball_speed"][1] != 0:
                x += 1
            x2 = (scene_info["platform_2P"][1]+30-scene_info["ball"][1]) / scene_info["ball_speed"][1]
            pred = scene_info["ball"][0]+(scene_info["ball_speed"][0]*x2) 
            if scene_info["ball"][1] < 220:
                pred, is_bounce = revise_ball_pred(pred, scene_info["ball"][0], abs(scene_info["ball_speed"][0]))
            else:                
                pred = revise_ball_approximate(pred)
            return pred

    # 2. Inform the game process that ml process is ready
    comm.ml_ready()

    # 3. Start an endless loop
    while True:
        # 3.1. Receive the scene information sent from the game process
        scene_info = comm.recv_from_game()

        # 3.2. If either of two sides wins the game, do the updating or
        #      resetting stuff and inform the game process when the ml process
        #      is ready.
        if scene_info["status"] != "GAME_ALIVE":
            # Do some updating or resetting stuff
            ball_served = False

            # 3.2.1 Inform the game process that
            #       the ml process is ready for the next round
            comm.ml_ready()
            continue

        # 3.3 Put the code here to handle the scene information
        if scene_info['frame'] == print_frame and ready_print and side == "1P":
            print("block",print_frame,scene_info['ball'],scene_info['ball_speed'],print_speedx,print_speedy)
            ready_print = False

        now_ball_y = scene_info['ball'][1]
        now_ball_speed_y = scene_info['ball_speed'][1]
        now_blocker = scene_info['blocker'][0]

        if (now_ball_y == 80 or now_ball_y == 415) and will_print and side == "1P":
            print(scene_info['frame'],scene_info['ball'])
            will_print = False

        if now_ball_y != former_ball_y:
            if prepare_cal:
                blocker_dict = (now_blocker - former_blocker)/abs(now_blocker - former_blocker)
                will_print1 = will_print2 = will_print = True
                if prepare_cal == 1:
                    second_last_command, last_command, case = predict_direction(blocker_dict, 1)
                elif prepare_cal == 2:
                    second_last_command, last_command, case = predict_direction(blocker_dict, 2)
                prepare_cal = 0
            elif now_ball_speed_y > 0 and 415-now_ball_y <= now_ball_speed_y*3 and 415-now_ball_y > now_ball_speed_y:
                prepare_cal = 1
                pred_contact = pred_1P()
            elif now_ball_speed_y < 0 and now_ball_y-80 <= (-now_ball_speed_y)*3 and now_ball_y-80 > -now_ball_speed_y:
                prepare_cal = 2
                pred_contact = pred_2P()
            former_ball_y = now_ball_y
            former_blocker = now_blocker
        # 3.4 Send the instruction for this frame to the game process
        if not ball_served:            
            if scene_info['frame'] == 149:
                comm.send_to_game({"frame": scene_info["frame"], "command": "SERVE_TO_RIGHT"})
                ball_served = True
        else:
            if side == "1P":
                pred_temp = pred_1P()
                command = move_to("1P", pred_temp)
                if now_ball_speed_y > 0 and 415-now_ball_y <= now_ball_speed_y*2 and 415-now_ball_y > now_ball_speed_y:
                    if abs(pred_temp - (scene_info['platform_1P'][0]+17.5)) < 18:
                        command = second_last_command
                    if will_print2:
                        if abs(pred_temp - (scene_info['platform_1P'][0]+17.5)) < 18:
                            print(scene_info['frame'],"do_second", second_last_command, case, side)
                        else:
                            print(scene_info['frame'],"not_second", second_last_command, case, command, side)
                        will_print2 = False
                elif now_ball_speed_y > 0 and 415-now_ball_y <= now_ball_speed_y and 415-now_ball_y != 0:
                    if abs(pred_temp - (scene_info['platform_1P'][0]+17.5)) < 18:
                        command = last_command
                        ready_print = True
                    if will_print1:
                        if abs(pred_temp - (scene_info['platform_1P'][0]+17.5)) < 18:
                            print(scene_info['frame'],"do_last", last_command, case, side)
                        else:
                            print(scene_info['frame'],"not_last", last_command, case, command, side)
                        will_print1 = False
            else:
                pred_temp = pred_2P()
                command = move_to("2P", pred_temp)
                if now_ball_speed_y < 0 and now_ball_y-80 <= -now_ball_speed_y*2 and now_ball_y-80 > -now_ball_speed_y:
                    if abs(pred_temp - (scene_info['platform_2P'][0]+17.5)) < 18:
                        command = second_last_command
                    if will_print2:
                        if abs(pred_temp - (scene_info['platform_2P'][0]+17.5)) < 18:
                            print(scene_info['frame'],"do_second", second_last_command, case, side)
                        else:
                            print(scene_info['frame'],"not_second", second_last_command, case, command, side)
                        will_print2 = False
                elif now_ball_speed_y < 0 and now_ball_y-80 <= -now_ball_speed_y and now_ball_y-80 != 0:
                    if abs(pred_temp - (scene_info['platform_2P'][0]+17.5)) < 18:
                        command = last_command
                        ready_print = True
                    if will_print1:
                        if abs(pred_temp - (scene_info['platform_2P'][0]+17.5)) < 18:
                            print(scene_info['frame'],"do_last", last_command, case, side)
                        else:
                            print(scene_info['frame'],"not_last", last_command, case, command, side)
                        will_print1 = False
            if command == 0:
                comm.send_to_game({"frame": scene_info["frame"], "command": "NONE"})
            elif command == 1:
                comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_RIGHT"})
            else :
                comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_LEFT"})