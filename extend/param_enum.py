from enum import Enum


class SportTypes(Enum):
    RUNNING = "running", 1,
    CYCLING = "cycling", 2,

    def Mapping(key):
        tmp_map = {}
        for type in list(SportTypes):
            tmp_map[type.value[0]] = type.value[1]
        return tmp_map[key]


class DurationType(Enum):
    TIME = "time", 2
    DISTANCE = "distance", 3
    LAP_BUTTON = "lap.button", 1

    # CALORIES = "calories",
    # HEART_RATE = "heart.rate",
    # POWER = "power"
    def Mapping(key):
        tmp_map = {}
        for type in list(DurationType):
            tmp_map[type.value[0]] = type.value[1]
        return tmp_map[key]


class TargetType(Enum):
    # 无目标
    TARGET_PACE = "no.target", 1
    # 配速
    TARGET_SPEED = "speed.zone", 5
    TARGET_CADENCE = "cadence.zone", 3
    TARGET_HR = "heart.rate.zone", 4
    TARGET_POWER = "power.zone", 2
    # 自定义心率区间
    SELECT_HEART_RATE_ZONE_FIELD = "heart.rate.zone", 4
    # 自定义功率区间
    SELECT_POWER_ZONE_FIELD = "power.zone", 2

    def Mapping(key):
        tmp_map = {}
        for type in list(TargetType):
            tmp_map[type.value[0]] = type.value[1]
        return tmp_map[key]


class StepType(Enum):
    WARMUP = "warmup", 1
    INTERVAL = "interval", 3
    RECOVERY = "recovery", 4
    REST = "rest", 5
    COOL_DOWN = "cooldown", 2
    OTHER = "other", 7

    def Mapping(key):
        tmp_map = {}
        for type in list(StepType):
            tmp_map[type.value[0]] = type.value[1]
        return tmp_map[key]
