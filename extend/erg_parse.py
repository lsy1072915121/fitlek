# -*- coding:utf-8 -*-
import re

from extend.param_enum import SportTypes, StepType, DurationType, TargetType
from fitlek.garmin import Workout, WorkoutStep, Target
from fitlek.utils import seconds_to_mmss


def switch_to_cycling_workout(file_path, name, ftp, offset=10):
    """
        erg课程数据转化成workout数据
        - file_path 课程本地文件路径
        - name 课程名字
        - ftp FTP
        - offset 目标功率偏移量,默认上下浮动10W
        return workout-佳明课表对象
    """
    course_data_list, watts_type = parse(file_path)
    # erg格式：第一个和最后一个是单的，其余的是成对存在，所以总数是双数
    if len(course_data_list) % 2 != 0:
        print("erg 格式错误")
        return
    # 去第一和最后一个数值
    tmp_list = []

    for index, data in enumerate(course_data_list):
        if index == 0 or index == len(course_data_list) - 1:
            tmp_list.append(data)
            continue
        if index % 2 == 0:
            # 基数保留
            tmp_list.append(data)

    # 后一个与前一个的时间差是前一个的time
    result_list = []
    for index, data in enumerate(tmp_list):
        if index == len(tmp_list) - 1:
            break
        cur_data = data
        next_data = tmp_list[index + 1]
        # 时间差
        diff_time = float(next_data['time']) - float(cur_data['time'])
        percent = int(cur_data['value'])
        result = dict()
        result['time'] = diff_time
        result['value'] = percent
        result_list.append(result)

    # 创建一个课表
    workout = Workout(SportTypes.CYCLING.value[0], name)
    for index, data in enumerate(result_list):
        seconds = int(data["time"] * 60)

        if watts_type == "PERCENT":
            target_value = ftp * data["value"] / 100.0
        else:
            target_value = data["value"]

        target = Target(TargetType.TARGET_POWER.value[0], target_value - offset, target_value + offset)
        workout.add_step(
            WorkoutStep(
                index,
                StepType.INTERVAL.value[0],
                # 默认都是按时间
                end_condition=DurationType.TIME.value[0],
                end_condition_value=seconds_to_mmss(seconds),
                target=target,
            )
        )
    return workout


def parse(file_path):
    """
        解析erg文件
        -file_path:课程本地文件路径

        return
            - course_data_list 课程数据
            - watts_type 功率类型，PERCENT:百分比；WATTS:功率值

    """
    # 读取文件
    file = open(file_path)
    erg_str = file.read()
    # 解析
    line_list = erg_str.splitlines()
    obj = {}
    # 按照固定行号表示参数
    for index, line in enumerate(line_list):
        # 过滤掉[xxx]
        match_obj = re.match(r'\[.+]', line, re.M | re.I)
        if match_obj:
            continue
        key_value_arr = line.split("=")
        if key_value_arr[0].__contains__("VERSION"):
            # 版本信息
            obj["VERSION"] = key_value_arr[1].strip()
        elif key_value_arr[0].__contains__("UNITS"):
            # 单位
            obj["UNITS"] = key_value_arr[1].strip()
        elif key_value_arr[0].__contains__("DESCRIPTION"):
            # 描述
            obj["DESCRIPTION"] = key_value_arr[1].strip()
        elif key_value_arr[0].__contains__("FILE NAME"):
            # 文件名
            obj["FILE_NAME"] = key_value_arr[1].strip()
        elif key_value_arr[0].__contains__("MINUTES"):
            # 格式
            obj["WATTS_TYPE"] = key_value_arr[0].split(" ")[1]

    # 课程数
    data_list = line_list[line_list.index("[COURSE DATA]") + 1:-1]
    course_data_list = []
    for data in data_list:
        temp = data.split("    ")
        d = dict()
        d["time"] = temp[0]
        d["value"] = temp[1]
        # 过滤LAP
        if "LAP" == temp[1]:
            continue
        course_data_list.append(d)
    return course_data_list, obj["WATTS_TYPE"]
