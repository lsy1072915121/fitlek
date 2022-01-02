import re

from extend.param_enum import TargetType, StepType, SportTypes, DurationType
from .utils import request

SSO_LOGIN_URL = "https://sso.garmin.com/sso/signin"

class GarminClient:
    """
    This is a modified version of:
    https://raw.githubusercontent.com/petergardfjall/garminexport/master/garminexport/garminclient.py

    The Garmin Export project was originally released under the Apache License 2.0.

    Lots of details about the Workouts grokked from:
    https://github.com/mgif/quick-plan
    """

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.cookiejar = None

    def connect(self):
        self._authenticate()

    def _authenticate(self):
        form_data = {
            "username": self.username,
            "password": self.password,
            "embed": "false",
        }

        request_params = {"service": "https://connectus.garmin.cn/modern/workouts",
                          "webhost": "https://connectus.garmin.cn/modern/workouts",
                          "source": "https://connectus.garmin.cn/signin/",
                          "redirectAfterAccountLoginUrl": "https://connectus.garmin.cn/modern/workouts",
                          "redirectAfterAccountCreationUrl": "https://connectus.garmin.cn/modern/workouts",
                          "gauthHost": "https://sso.garmin.com/sso",
                          "locale": "zh_TW",
                          "id": "gauth-widget",
                          "cssUrl": "https://connectus.garmin.cn/gauth-custom-cn-v1.2-min.css",
                          "privacyStatementUrl": "https://www.garmin.com/zh-TW/privacy/connect/",
                          "clientId": "GarminConnect",
                          "rememberMeShown": "true",
                          "rememberMeChecked": "false",

                          }
        headers = {
            "origin": "https://sso.garmin.com",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
            "cookie": 'SESSION=73eb164c-b2dc-4638-852c-54b945620563; CASTGC=TGT-164352-hV4YJG4d7nJarmbsuAI22ztHfKGdkCgIzyPVFi6Zo3XT07cDfH-cas; CONSENTMGR=consent:false%7Cts:1637327464787; __VCAP_ID__=7093ee3d-cdd5-4538-5213-1665; __cflb=02DiuHkH2SZrbLnjiuY1KAY9ZUtRHBhBoT2rch5ztCeZA; __cfruid=2fdb23f3a916b0711752527f857f89ac5af1c079-1638515396; org.springframework.web.servlet.i18n.CookieLocaleResolver.LOCALE=en; GARMIN-SSO=1; utag_main=v_id:017cb7c69d4a0020e876c063a88c03079003c07100942$_sn:4$_ss:1$_st:1638522192741$ses_id:1638520392741%3Bexp-session$_pn:1%3Bexp-session; TEALCDN=cn:1638606792736; GarminNoCache=true; GARMIN-SSO-GUID=0D5BAED35676F129A0D0A183FDB5EB5F85E7AC85; GARMIN-SSO-CUST-GUID=7ce9e16d-dffd-4962-b8d8-7b9c21c4e687; ADRUM=s=1638520440811&r=https%3A%2F%2Fsso.garmin.com%2Fsso%2Fsignin%3Fhash%3D35'
        }

        auth_response = request(
            SSO_LOGIN_URL,
            headers=headers,
            params=request_params,
            data=form_data,
            method="POST",
        )

        self.cookiejar = auth_response.cookiejar

        if auth_response.status != 200:
            raise ValueError("authentication failure: did you enter valid credentials?")

        auth_ticket_url = self._extract_auth_ticket_url(auth_response.content.decode())
        response = request(auth_ticket_url, cookiejar=self.cookiejar)

        if response.status != 200:
            raise RuntimeError(
                "auth failure: failed to claim auth ticket: {}: {}\n{}".format(
                    auth_ticket_url, response.status, response.content
                )
            )

    @staticmethod
    def _extract_auth_ticket_url(auth_response):
        match = re.search(r'response_url\s*=\s*"(https:[^"]+)"', auth_response)
        if not match:
            raise RuntimeError(
                "auth failure: unable to extract auth ticket URL. did you provide a correct username/password?"
            )
        auth_ticket_url = match.group(1).replace("\\", "")
        auth_ticket_url = auth_ticket_url.replace("workouts", "")
        return auth_ticket_url

    def add_workout(self, workout):
        response = request(
            "https://connectus.garmin.cn/modern/proxy/workout-service/workout",
            method="POST",
            json=workout.json(),
            headers={
                "Referer": "https://connectus.garmin.cn/modern/workout/create/cycling",
                "nk": "NT",
                "X-app-ver": "4.49.0.23",
                "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:82.0) Gecko/20100101 Firefox/82.0",
                "origin": "https://connectus.garmin.cn",
                "Host": "connectus.garmin.cn",
                "Cookie": "SESSIONID=" + self.cookiejar.__getattribute__("_cookies")["connectus.garmin.cn"]['/'][
                    "SESSIONID"].value
            },
            cookiejar=self.cookiejar,
        )

        if response.status > 299:
            print(response)
        return response.json


class Workout:
    def __init__(self, sport_type, name):
        self.sport_type = sport_type
        self.workout_name = name
        self.workout_steps = []

    def add_step(self, step):
        self.workout_steps.append(step)

    def json(self):
        return {
            "sportType": {
                "sportTypeId": SportTypes.Mapping(self.sport_type),
                "sportTypeKey": self.sport_type,
            },
            "workoutName": self.workout_name,
            "workoutSegments": [
                {
                    "segmentOrder": 1,
                    "sportType": {
                        "sportTypeId": SportTypes.Mapping(self.sport_type),
                        "sportTypeKey": self.sport_type,
                    },
                    "workoutSteps": [step.json() for step in self.workout_steps],
                }
            ],
        }


class WorkoutStep:
    def __init__(
        self,
        order,
        step_type,
        end_condition="lap.button",
        end_condition_value=None,
        target=None,
    ):
        """Valid end condition values:
        - distance: '2.0km', '1.125km', '1.6km'
        - time: 0:40, 4:20
        - lap.button
        """
        self.order = order
        self.step_type = step_type
        self.end_condition = end_condition
        self.end_condition_value = end_condition_value
        self.target = target or Target()

    def end_condition_unit(self):
        if self.end_condition and self.end_condition.endswith("km"):
            return {"unitKey": "kilometer"}
        else:
            return None

    def parsed_end_condition_value(self):
        # distance
        if self.end_condition_value and self.end_condition_value.endswith("km"):
            return int(float(self.end_condition_value.replace("km", "")) * 1000)

        # time
        elif self.end_condition_value and ":" in self.end_condition_value:
            m, s = [int(x) for x in self.end_condition_value.split(":")]
            return m * 60 + s
        else:
            return None

    def json(self):
        return {
            "type": "ExecutableStepDTO",
            "stepId": None,
            "stepOrder": self.order,
            "childStepId": None,
            "description": None,
            "stepType": {
                "stepTypeId": StepType.Mapping(self.step_type),
                "stepTypeKey": self.step_type,
            },
            "endCondition": {
                "conditionTypeKey": self.end_condition,
                "conditionTypeId": DurationType.Mapping(self.end_condition),
            },
            "preferredEndConditionUnit": self.end_condition_unit(),
            "endConditionValue": self.parsed_end_condition_value(),
            "endConditionCompare": None,
            "endConditionZone": None,
            **self.target.json(),
        }


class Target:
    def __init__(self, target="no.target", to_value=None, from_value=None, zone=None):
        self.target = target
        self.to_value = to_value
        self.from_value = from_value
        self.zone = zone

    def json(self):
        return {
            "targetType": {
                "workoutTargetTypeId": TargetType.Mapping(self.target),
                "workoutTargetTypeKey": self.target,
            },
            "targetValueOne": self.to_value,
            "targetValueTwo": self.from_value,
            "zoneNumber": self.zone,
        }
