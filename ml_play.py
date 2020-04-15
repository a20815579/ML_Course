"""
The template of the main script of the machine learning process
"""

import games.arkanoid.communication as comm
from games.arkanoid.communication import ( \
    SceneInfo, GameStatus, PlatformAction
)

def calculate_fall(former, now):
    if 7 <= former and former <= 188:
        v = now - former
        fall = now + v*19.5
        if fall > 195:
            fall = 195 - (fall-195)
        if fall < 0:
            fall = -fall
    elif former < 7:
        fall = now + 7*19
    else:
        fall = now - 7*19
    if fall <= 20:
        fall = 0
    else:
        fall -= 20
    return fall

def ml_loop():
    """
    The main loop of the machine learning process

    This loop is run in a separate process, and communicates with the game process.

    Note that the game process won't wait for the ml process to generate the
    GameInstruction. It is possible that the frame of the GameInstruction
    is behind of the current frame in the game process. Try to decrease the fps
    to avoid this situation.
    """

    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here.
    ball_served = False
    prepare_cal = False
    fall = 75
    former_ball_y = 395
    former_ball_x = 75
    #now_ball_y = 400
    # 2. Inform the game process that ml process is ready before start the loop.
    comm.ml_ready()

    # 3. Start an endless loop.
    while True:
        # 3.1. Receive the scene information sent from the game process.
        scene_info = comm.get_scene_info()

        # 3.2. If the game is over or passed, the game process will reset
        #      the scene and wait for ml process doing resetting job.
        if scene_info.status == GameStatus.GAME_OVER or \
            scene_info.status == GameStatus.GAME_PASS:
            # Do some stuff if needed
            ball_served = False

            # 3.2.1. Inform the game process that ml process is ready
            comm.ml_ready()
            continue

        # 3.3. Put the code here to handle the scene information
        now_ball_x = scene_info.ball[0]
        now_ball_y = scene_info.ball[1]

        if now_ball_y != former_ball_y:
            if 247 < now_ball_y and now_ball_y < 255 and now_ball_y > former_ball_y:
                prepare_cal = True
            if prepare_cal:
                fall = calculate_fall(former_ball_x, now_ball_x)
                prepare_cal = False
            former_ball_x = now_ball_x
            former_ball_y = now_ball_y
        # 3.4. Send the instruction for this frame to the game process
        if not ball_served:
            comm.send_instruction(scene_info.frame, PlatformAction.SERVE_TO_LEFT)
            ball_served = True
        else:
            platform_x = scene_info.platform[0]
            if now_ball_y < 255:
                if platform_x < 77:
                    comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
                elif platform_x > 83:
                    comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
                else:
                    comm.send_instruction(scene_info.frame, PlatformAction.NONE)
            else:
                if now_ball_y >= 388 or abs(platform_x - fall) < 5:
                    comm.send_instruction(scene_info.frame, PlatformAction.NONE)
                elif fall > platform_x:
                    comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
                elif fall < platform_x:
                    comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
                else:
                    comm.send_instruction(scene_info.frame, PlatformAction.NONE)
