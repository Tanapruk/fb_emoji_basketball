#!/usr/bin/env python

from uiautomator import device as d
import os
import random


# from shapely.geometry import polygon


def get_ui_object(string_id_name):
    return d(resourceId="com.facebook.orca:id/" + string_id_name)


# nexus 4
# rim size 184
# width 768
# height 1184
# max possible rim right x 676 (768 -1/2 184)
# min possible rim left x 92 (1/2 184) ** there is a white space before rim, so it will be like 50 px more

ui_ball = get_ui_object("ball")
ui_bottom = get_ui_object("bottom")
# ui_backboard_target = get_ui_object("backboard_target")
ui_rim = get_ui_object("rim")
ui_score = get_ui_object("score")
ui_best_score = get_ui_object("best_score")


def get_score():
    # manual delay. otherwise this method is repeatedly called and freeze.
    sleep(0.3)
    if ui_score.wait.exists(timeout=1000):
        score = ui_score.info.get("text")
        print "score ", score
        return int(score)
    else:
        print "score gone"
        return -1


def get_bound(view_object):
    return view_object.info.get("visibleBounds")


def get_middle(a, b):
    return int((a + b) / 2)


def get_ball_bound_side(string_side):
    return get_bound(ui_ball).get(string_side)


def get_rim_bound_side(string_side):
    return int(get_bound(ui_rim).get(string_side))


def get_ball_left():
    return get_ball_bound_side("left")


def get_ball_right():
    return get_ball_bound_side("right")


def get_ball_top():
    return get_ball_bound_side("top")


def get_ball_bottom():
    return get_ball_bound_side("bottom")


def get_ball_middle_x():
    return get_middle(get_ball_left(), get_ball_right())


def get_ball_middle_y():
    return get_middle(get_ball_top(), get_ball_bottom())


def get_rim_left():
    return get_rim_bound_side("left")


def get_rim_right():
    return get_rim_bound_side("right")


def get_rim_top():
    return get_rim_bound_side("top")


def get_rim_bottom():
    return get_rim_bound_side("bottom")


def get_rim_middle_x():
    return get_middle(get_rim_left(), get_rim_right())


def get_rim_middle_y():
    return get_middle(get_rim_top(), get_rim_bottom())


int_screen_width = int(get_bound(ui_bottom).get("right"))
int_screen_height = int(get_bound(ui_bottom).get("bottom"))
int_middle_screen_horizontal = int_screen_width / 2


def swipe_up():
    ui_ball.swipe.up(steps=10)


def shoot_to(x, y):
    print "target", x, y
    d.drag(get_ball_middle_x(), get_ball_middle_y(), x, y, steps=10)


def shoot_to_x(x):
    shoot_to(x, get_rim_middle_y())


def shoot_moving_rim(ref_start_x, ref_start_y, offset):
    x = ref_start_x + offset
    y = ref_start_y
    shoot_to(x, y)


def shoot_to_right(ref_start_x, ref_start_y, offset):
    print "shoot to the right ", offset
    shoot_moving_rim(ref_start_x, ref_start_y, offset)


def shoot_to_left(ref_start_x, ref_start_y, offset):
    print "shoot to the left", "-", offset
    shoot_moving_rim(ref_start_x, ref_start_y, -offset)


def get_avg(array):
    return int(sum(array) / len(array))


class BallStatus:
    NO_SHOT = "0"
    SHOT_ALREADY = "1"
    STOP = "2"


class RimMomentum:
    MOVING_LEFT_TO_RIGHT = "1"
    MOVING_RIGHT_TO_LEFT = "2"
    STILL = "3"


class Level:
    LEVEL_UNKNOWN = "0"
    LEVEL_0_10 = "1"
    LEVEL_11_20 = "2"
    LEVEL_21_30 = "3"
    LEVEL_31_40 = "4"
    LEVEL_41_50 = "5"


def get_rim_momentum(avg_x_diff):
    if avg_x_diff < 0:
        print "L>>>>>R"
        return RimMomentum.MOVING_LEFT_TO_RIGHT
    elif avg_x_diff > 0:
        print "L<<<<<R"
        return RimMomentum.MOVING_RIGHT_TO_LEFT
    else:
        return RimMomentum.STILL


def get_xy_array(size):
    x_array = []
    y_array = []
    while len(x_array) < size:
        x_array.append(int(get_rim_middle_x()))
        y_array.append(int(get_rim_middle_y()))
    else:
        return XYArray(x_array, y_array)


def get_x_array(size):
    x_array = []
    while len(x_array) < size:
        x_array.append(get_rim_middle_x())
    else:
        return x_array


class XYArray:
    def __init__(self, x_array, y_array):
        self.x_array = x_array
        self.y_array = y_array


def get_diff_array(loc_array):
    diff_array = []
    count = 0

    while count < len(loc_array) - 1:
        diff = loc_array[count] - loc_array[count + 1]
        count += 1
        diff_array.append(diff)
    else:
        return diff_array


def get_level():
    score = get_score()
    if 0 <= score < 10:
        return Level.LEVEL_0_10
    elif 10 <= score < 20:
        return Level.LEVEL_11_20
    elif 20 <= score < 30:
        return Level.LEVEL_21_30
    elif 30 <= score < 40:
        return Level.LEVEL_31_40
    elif 40 <= score < 50:
        return Level.LEVEL_41_50
    else:
        return Level.LEVEL_UNKNOWN


class Operator:
    EQUAL = "1"
    LESS_THAN = "2"
    MORE_THAN = "3"


def is_stationary(avg_diff, avg_loc):
    rim_status = get_rim_momentum(avg_diff)
    if rim_status == RimMomentum.STILL and avg_loc == int_middle_screen_horizontal:
        return True
    else:
        return False


def is_left_to_right(rim):
    return True if rim.get_momentum_x() == RimMomentum.MOVING_LEFT_TO_RIGHT else False


def is_right_to_left(rim):
    return True if rim.get_momentum_x() == RimMomentum.MOVING_RIGHT_TO_LEFT else False


class RimX:
    def __init__(self, input_count):
        self.x_array = get_x_array(input_count)
        self.diff_x_array = get_diff_array(self.x_array)
        self.avg_x_diff = get_avg(self.diff_x_array)
        self.avg_x = get_avg(self.x_array)
        print "x", self.x_array, "speed", self.diff_x_array

    def get_first_x(self):
        return self.x_array[0]

    def get_last_x(self):
        return self.x_array[len(self.x_array) - 1]

    def get_momentum_x(self):
        return get_rim_momentum(self.avg_x_diff)


class Rim:
    def __init__(self, input_count):
        self.xy_array = get_xy_array(input_count)
        self.x_array = self.xy_array.x_array
        self.y_array = self.xy_array.y_array
        self.diff_x_array = get_diff_array(self.x_array)
        self.diff_y_array = get_diff_array(self.y_array)
        self.avg_x_diff = get_avg(self.diff_x_array)
        self.avg_y_diff = get_avg(self.diff_y_array)
        self.avg_x = get_avg(self.x_array)
        self.avg_y = get_avg(self.y_array)
        print "x", self.x_array, "speed", self.diff_x_array, "avg speed ", self.avg_x_diff, "avg loc ", self.avg_x

    def get_first_x(self):
        return self.x_array[0]

    def get_last_x(self):
        return self.x_array[len(self.x_array) - 1]

    def get_momentum_x(self):
        return get_rim_momentum(self.avg_x_diff)


def shoot_0_10():
    if ui_ball.exists:
        shoot_to_x(get_rim_middle_x())
        # ui_ball.drag.to(resourceId="com.facebook.orca:id/rim", steps=10)
        return BallStatus.SHOT_ALREADY
    else:
        return BallStatus.NO_SHOT


def shoot_11_20(rim):
    int_offset = int_screen_width / 2.8
    if is_left_to_right(rim) and rim.get_last_x() < int_middle_screen_horizontal:
        shoot_to_right(get_rim_middle_x(), get_rim_middle_y(), int_offset)
        return BallStatus.SHOT_ALREADY
    elif is_right_to_left(rim) and rim.get_last_x() > int_middle_screen_horizontal:
        shoot_to_left(get_rim_middle_x(), get_rim_middle_y(), int_offset)
        return BallStatus.SHOT_ALREADY
    else:
        return BallStatus.NO_SHOT


def sleep(second):
    if second != 0:
        os.system("sleep " + str(second))


def get_delay(int_x, start_x, end_x, total_delay, is_left_to_right):
    if is_left_to_right:
        return total_delay * (end_x - int_x) / (end_x - start_x)
    else:
        return total_delay * abs(start_x - int_x) / (end_x - start_x)


def get_w_p(int_x):
    return round(float(int_x) / float(int_screen_width), 2) * 100


def shoot_with_delay(target_x, target_y, int_x, start_x, end_x, total_delay, l_to_r):
    if start_x <= int_x <= end_x:
        int_delay = get_delay(int_x, start_x, end_x, total_delay, l_to_r)
        print start_x, "(", get_w_p(start_x), ")>x<", int_x, "(", get_w_p(int_x), ")", end_x, "(", get_w_p(
            end_x), ") Delay by", int_delay
        sleep(int_delay)
        shoot_to(target_x, target_y)
        sleep(int_delay)
        return BallStatus.SHOT_ALREADY
    else:
        skip_beat()
        return BallStatus.NO_SHOT


def shoot_21_30(rim):
    target_x = int_middle_screen_horizontal
    target_y = get_rim_middle_y()
    int_x = rim.get_last_x()
    if is_left_to_right(rim):
        shoot_with_delay(target_x, target_y, int_x, cx(170), cx(391), 0.68, True)
    elif is_right_to_left(rim):
        shoot_with_delay(target_x, target_y, int_x, cx(384), cx(630), 0.68, False)
    else:
        return BallStatus.NO_SHOT


def shoot_31_40(rim):
    target_x = int_middle_screen_horizontal
    target_y = cy(456)
    int_x = rim.get_last_x()
    if is_left_to_right(rim):
        shoot_with_delay(target_x, target_y, int_x, cx(130), cx(429), 0.8, True)
    elif is_right_to_left(rim):
        shoot_with_delay(target_x, target_y, int_x, cx(350), cx(650), 0.8, False)
    else:
        return BallStatus.NO_SHOT


def cx(pixel):
    # width pixel
    return int(int_screen_width * pixel / 768)


def cy(pixel):
    # height pixel
    return int(int_screen_height * pixel / 1168)


def shoot_41_50(rim):
    target_x = int_middle_screen_horizontal
    target_y = cy(509)
    int_x = rim.get_last_x()
    if is_left_to_right(rim):
        shoot_with_delay(target_x, target_y, int_x, cx(170), cx(391), 0.67, True)
    elif is_right_to_left(rim):
        shoot_with_delay(target_x, target_y, int_x, cx(384), cx(630), 0.67, False)
    else:
        return BallStatus.NO_SHOT


def shoot_by_level():
    level = get_level()
    if level == Level.LEVEL_0_10:
        return shoot_0_10()
    elif level == Level.LEVEL_11_20:
        return shoot_11_20(RimX(2))
    elif level == Level.LEVEL_21_30:
        return shoot_21_30(RimX(2))
    elif level == Level.LEVEL_31_40:
        return shoot_31_40(RimX(2))
    elif level == Level.LEVEL_41_50:
        return shoot_41_50(RimX(2))
    elif level == Level.LEVEL_UNKNOWN:
        return BallStatus.STOP
    else:

        print "Don't shoot"
        return BallStatus.NO_SHOT


def shoot_when_ready():
    shooting_status = shoot_by_level()
    while shooting_status == BallStatus.NO_SHOT:
        shooting_status = shoot_by_level()
    else:
        if shooting_status == BallStatus.STOP:
            return
        sleep(0.5)


def skip_beat():
    int_random = random.random()
    print "pause ", int_random
    sleep(int_random)


def loop_shooting():
    print "start loop shooting"
    while 0 <= get_score() < 50:
        shoot_when_ready()

        print "finish a shot"
    else:
        print "end shooting"


def shoot_basketball():
    if ui_score.exists:
        loop_shooting()
    else:
        shoot_0_10()
        sleep(0.5)
        loop_shooting()
#test commit

def print_dumb():
    while True:
        print get_rim_middle_x(), get_rim_middle_y()


shoot_basketball()
# print d.dump()
# print_dumb()


# swipe_up()
# shoot_31_40()
