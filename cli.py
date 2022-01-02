#! /usr/bin/env python
# -*- coding:utf-8 -*-
import sys
import os

from extend import erg_parse
from fitlek.garmin import GarminClient


def parse_args(args):
    result = {
        a.split("=")[0]: int(a.split("=")[1])
        if "=" in a and a.split("=")[1].isnumeric()
        else a.split("=")[1]
        if "=" in a
        else True
        for a in args
        if "--" in a
    }
    result["[]"] = [a for a in args if not a.startswith("--")]
    return result


def get_or_throw(d, key, error):
    try:
        return d[key]
    except:
        raise Exception(error)


if __name__ == "__main__":
    args = parse_args(sys.argv)

    file_path = get_or_throw(
        args, "--file-path", "转换文件目录(支持erg)"
    )
    ftp = get_or_throw(
        args,
        "--ftp",
        "FTP",
    )
    username = get_or_throw(
        args, "--username", "Garmin Connect 用户名"
    )
    password = get_or_throw(
        args, "--password", "Garmin Connect 密码"
    )

    # 文件格式校验
    path, tmp_file_name = os.path.split(file_path)
    shot_name, extension = os.path.splitext(tmp_file_name)
    if ".erg" != extension:
        print("目前只支持erg文件")
        raise Exception("only support erg file now！")
    if ftp <= 0 or ftp >= 500:
        print("请输入正确的ftp")
        raise Exception("please input right FTP！")

    name = "{}w-{}".format(str(ftp), shot_name)
    workout = erg_parse.switch_to_cycling_workout(file_path, name, ftp)

    client = GarminClient(username, password)
    client.connect()
    client.add_workout(workout)

    print(
        "添加课表成功, 点击 https://connectus.garmin.com/modern/workouts 或者在手机Garmin Connect App查看"
    )
