import subprocess
from unittest import case
import urllib.request
import json
import time
import datetime
import hashlib
import logging
import threading
import asyncio
import struct
import aiohttp
from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP,
    ATTR_HS_COLOR,
    ATTR_MAX_MIREDS,
    ATTR_MIN_MIREDS,
    ATTR_RGB_COLOR,
    ATTR_RGBW_COLOR,
)
import homeassistant.util.color as color_util
from homeassistant.helpers.aiohttp_client import async_get_clientsession

import voluptuous as vol
import sys


sys.setrecursionlimit(100000)

from homeassistant.const import (
    CONF_FRIENDLY_NAME,
)

from homeassistant.core import callback
from homeassistant.helpers import discovery
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_point_in_utc_time
from homeassistant.util.dt import utcnow
from .auth import Auth
from .cloud import Cloud
from .constants import *

_LOGGER = logging.getLogger(__name__)


ENTITYID = "entity_id"
DOMAIN = "lifesmart"


async def asyncPOST(url, data, headers):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data, headers=headers) as response:
            r = await response.text()
            return r


async def asycn_lifesmart_EpGetAll(appkey, apptoken, usertoken, userid, svrurl):
    url = svrurl + "/api.EpGetAll"
    tick = int(time.time())
    sdata = (
        "method:EpGetAll,time:"
        + str(tick)
        + ",userid:"
        + userid
        + ",usertoken:"
        + usertoken
        + ",appkey:"
        + appkey
        + ",apptoken:"
        + apptoken
    )
    sign = hashlib.md5(sdata.encode(encoding="UTF-8")).hexdigest()
    send_values = {
        "id": 1,
        "method": "EpGetAll",
        "system": {
            "ver": "1.0",
            "lang": "en",
            "userid": userid,
            "appkey": appkey,
            "time": tick,
            "sign": sign,
        },
    }
    header = {"Content-Type": "application/json"}
    send_data = json.dumps(send_values)
    response = json.loads(await asyncPOST(url, send_data, header))
    if response["code"] == 0:
        return response["message"]
    return False


async def asycn_lifesmart_SceneGet(appkey, apptoken, usertoken, userid, agt, svrurl):
    url = svrurl + "/api.SceneGet"
    tick = int(time.time())
    sdata = (
        "method:SceneGet,agt:"
        + agt
        + ",time:"
        + str(tick)
        + ",userid:"
        + userid
        + ",usertoken:"
        + usertoken
        + ",appkey:"
        + appkey
        + ",apptoken:"
        + apptoken
    )
    sign = hashlib.md5(sdata.encode(encoding="UTF-8")).hexdigest()
    send_values = {
        "id": 1,
        "method": "SceneGet",
        "params": {
            "agt": agt,
        },
        "system": {
            "ver": "1.0",
            "lang": "en",
            "userid": userid,
            "appkey": appkey,
            "time": tick,
            "sign": sign,
        },
    }
    header = {"Content-Type": "application/json"}
    send_data = json.dumps(send_values)
    response = json.loads(await asyncPOST(url, send_data, header))
    print(send_data)
    print(response)
    if response["code"] == 0:
        return response["message"]
    return False


def lifesmart_Sendkeys(
    appkey, apptoken, usertoken, userid, agt, ai, me, category, brand, keys, svrurl
):
    url = svrurl + "/irapi.SendKeys"
    tick = int(time.time())
    # keys = str(keys)
    sdata = (
        "method:SendKeys,agt:"
        + agt
        + ",ai:"
        + ai
        + ",brand:"
        + brand
        + ",category:"
        + category
        + ",keys:"
        + keys
        + ",me:"
        + me
        + ",time:"
        + str(tick)
        + ",userid:"
        + userid
        + ",usertoken:"
        + usertoken
        + ",appkey:"
        + appkey
        + ",apptoken:"
        + apptoken
    )
    sign = hashlib.md5(sdata.encode(encoding="UTF-8")).hexdigest()
    _LOGGER.debug("sendkey: %s", str(sdata))
    send_values = {
        "id": 1,
        "method": "SendKeys",
        "params": {
            "agt": agt,
            "me": me,
            "category": category,
            "brand": brand,
            "ai": ai,
            "keys": keys,
        },
        "system": {
            "ver": "1.0",
            "lang": "en",
            "userid": userid,
            "appkey": appkey,
            "time": tick,
            "sign": sign,
        },
    }
    header = {"Content-Type": "application/json"}
    send_data = json.dumps(send_values)
    req = urllib.request.Request(
        url=url, data=send_data.encode("utf-8"), headers=header, method="POST"
    )
    response = json.loads(urllib.request.urlopen(req).read().decode("utf-8"))
    _LOGGER.debug("sendkey_res: %s", str(response))
    return response


def lifesmart_Sendackeys(
    appkey,
    apptoken,
    usertoken,
    userid,
    svrurl,
    agt,
    ai,
    me,
    category,
    brand,
    keys,
    power,
    mode,
    temp,
    wind,
    swing,
):
    url = svrurl + "/irapi.SendACKeys"
    tick = int(time.time())
    # keys = str(keys)
    sdata = (
        "method:SendACKeys,agt:"
        + agt
        + ",ai:"
        + ai
        + ",brand:"
        + brand
        + ",category:"
        + category
        + ",keys:"
        + keys
        + ",me:"
        + me
        + ",mode:"
        + str(mode)
        + ",power:"
        + str(power)
        + ",swing:"
        + str(swing)
        + ",temp:"
        + str(temp)
        + ",wind:"
        + str(wind)
        + ",time:"
        + str(tick)
        + ",userid:"
        + userid
        + ",usertoken:"
        + usertoken
        + ",appkey:"
        + appkey
        + ",apptoken:"
        + apptoken
    )
    sign = hashlib.md5(sdata.encode(encoding="UTF-8")).hexdigest()
    _LOGGER.debug("sendackey: %s", str(sdata))
    send_values = {
        "id": 1,
        "method": "SendACKeys",
        "params": {
            "agt": agt,
            "me": me,
            "category": category,
            "brand": brand,
            "ai": ai,
            "keys": keys,
            "power": power,
            "mode": mode,
            "temp": temp,
            "wind": wind,
            "swing": swing,
        },
        "system": {
            "ver": "1.0",
            "lang": "en",
            "userid": userid,
            "appkey": appkey,
            "time": tick,
            "sign": sign,
        },
    }
    header = {"Content-Type": "application/json"}
    send_data = json.dumps(send_values)
    req = urllib.request.Request(
        url=url, data=send_data.encode("utf-8"), headers=header, method="POST"
    )
    response = json.loads(urllib.request.urlopen(req).read().decode("utf-8"))
    _LOGGER.debug("sendackey_res: %s", str(response))
    return response


async def async_setup(hass, config):
    """Set up the lifesmart component."""

    session = async_get_clientsession(hass)

    appkey = config[DOMAIN][CONF_LIFESMART_APPKEY]
    apptoken = config[DOMAIN][CONF_LIFESMART_APPTOKEN]
    password = config[DOMAIN][CONF_LIFESMART_PASSWORD]
    email = config[DOMAIN][CONF_LIFESMART_EMAIl]

    auth = Auth(session, appkey, apptoken, password, email)
    data = await auth.launch_auth_flow()
    param = {}
    param["appkey"] = appkey
    param["apptoken"] = apptoken
    param["usertoken"] = data["usertoken"]
    param["userid"] = data["userid"]
    param["svrurl"] = data["svrurl"]

    exclude_items = config[DOMAIN][CONF_EXCLUDE_ITEMS]
    exclude_agts = config[DOMAIN][CONF_EXCLUDE_AGTS]
    ai_include_agts = config[DOMAIN][CONF_AI_INCLUDE_AGTS]
    ai_include_items = config[DOMAIN][CONF_AI_INCLUDE_ITEMS]

    devices = await asycn_lifesmart_EpGetAll(
        param["appkey"],
        param["apptoken"],
        param["usertoken"],
        param["userid"],
        param["svrurl"],
    )
    for dev in devices:
        if dev["me"] in exclude_items or dev["agt"] in exclude_agts:
            continue
        devtype = dev["devtype"]
        # dev['agt'] = dev['agt'].replace("_","")
        # dev['agt'] = dev['agt'][:-3]
        if devtype in SWTICH_TYPES:
            discovery.load_platform(
                hass, "switch", DOMAIN, {"dev": dev, "param": param}, config
            )
        if devtype in BINARY_SENSOR_TYPES:
            discovery.load_platform(
                hass, "binary_sensor", DOMAIN, {"dev": dev, "param": param}, config
            )
        if devtype in COVER_TYPES:
            discovery.load_platform(
                hass, "cover", DOMAIN, {"dev": dev, "param": param}, config
            )
        if devtype in SPOT_TYPES:
            discovery.load_platform(
                hass, "light", DOMAIN, {"dev": dev, "param": param}, config
            )
        if devtype in CLIMATE_TYPES:
            discovery.load_platform(
                hass, "climate", DOMAIN, {"dev": dev, "param": param}, config
            )
        if devtype in GAS_SENSOR_TYPES or devtype in EV_SENSOR_TYPES:
            discovery.load_platform(
                hass, "sensor", DOMAIN, {"dev": dev, "param": param}, config
            )
        if devtype in OT_SENSOR_TYPES:
            discovery.load_platform(
                hass, "sensor", DOMAIN, {"dev": dev, "param": param}, config
            )
        if devtype in LIGHT_SWITCH_TYPES or devtype in LIGHT_DIMMER_TYPES:
            discovery.load_platform(
                hass, "light", DOMAIN, {"dev": dev, "param": param}, config
            )
    if ai_include_agts is not False:
        for agt in ai_include_agts:
            scenes = await asycn_lifesmart_SceneGet(
                param["appkey"],
                param["apptoken"],
                param["usertoken"],
                param["userid"],
                agt,
                param["svrurl"],
            )

            if scenes is not False:
                for scene in scenes:
                    # TODO added comment here for include all items
                    # if scene["id"] in ai_include_items:
                    devtype = "ai"
                    me = scene["id"]
                    dev = {"devtype": devtype, "me": me, "agt": agt}
                    print(me, dev)
                    discovery.load_platform(
                        hass,
                        "switch",
                        DOMAIN,
                        {"dev": {**dev, **scene}, "param": param},
                        config,
                    )

    # listen to ws
    cloud = Cloud(param, hass)
    cloud.start()

    def send_keys(call):
        """Handle the service call."""
        agt = call.data["agt"]
        me = call.data["me"]
        ai = call.data["ai"]
        category = call.data["category"]
        brand = call.data["brand"]
        keys = call.data["keys"]
        restkey = lifesmart_Sendkeys(
            param["appkey"],
            param["apptoken"],
            param["usertoken"],
            param["userid"],
            agt,
            ai,
            me,
            category,
            brand,
            keys,
            param["svrurl"],
        )
        _LOGGER.debug("sendkey: %s", str(restkey))

    def send_ackeys(call):
        """Handle the service call."""
        agt = call.data["agt"]
        me = call.data["me"]
        ai = call.data["ai"]
        category = call.data["category"]
        brand = call.data["brand"]
        keys = call.data["keys"]
        power = call.data["power"]
        mode = call.data["mode"]
        temp = call.data["temp"]
        wind = call.data["wind"]
        swing = call.data["swing"]
        restackey = lifesmart_Sendackeys(
            param["appkey"],
            param["apptoken"],
            param["usertoken"],
            param["userid"],
            param["svrurl"],
            agt,
            ai,
            me,
            category,
            brand,
            keys,
            power,
            mode,
            temp,
            wind,
            swing,
        )
        _LOGGER.debug("sendkey: %s", str(restackey))

    def scene_set(call):
        """Handle the service call."""
        agt = call.data["agt"]
        id = call.data["id"]
        restkey = lifesmart_SceneSet(
            param["appkey"],
            param["apptoken"],
            param["usertoken"],
            param["userid"],
            agt,
            id,
            param["svrurl"],
        )
        _LOGGER.debug("scene_set: %s", str(restkey))

    def get_fan_mode(_fanspeed):
        fanmode = None
        if _fanspeed < 30:
            fanmode = FAN_LOW
        elif _fanspeed < 65 and _fanspeed >= 30:
            fanmode = FAN_MEDIUM
        elif _fanspeed >= 65:
            fanmode = FAN_HIGH
        return fanmode

    hass.services.async_register(DOMAIN, "send_keys", send_keys)
    hass.services.async_register(DOMAIN, "send_ackeys", send_ackeys)
    hass.services.async_register(DOMAIN, "scene_set", scene_set)
    return True


class LifeSmartDevice(Entity):
    """LifeSmart base device."""

    def __init__(self, dev, idx, val, param):
        """Initialize the switch."""
        if dev["devtype"] in SWTICH_TYPES and dev["devtype"] not in [
            "SL_NATURE",
            "SL_SW_ND1",
            "SL_SW_ND2",
            "SL_SW_ND3",
        ]:
            self._name = dev["name"] + "_" + dev["data"][idx]["name"]
        elif (
            dev["devtype"] in AI_TYPES
            or dev["devtype"] in LIGHT_DIMMER_TYPES
            or dev["devtype"] in LIGHT_SWITCH_TYPES
        ):
            self._name = dev["name"]
        else:
            self._name = dev["name"] + "_" + idx
        self._appkey = param["appkey"]
        self._apptoken = param["apptoken"]
        self._usertoken = param["usertoken"]
        self._userid = param["userid"]
        self._svrurl = param["svrurl"]
        self._agt = dev["agt"]
        self._me = dev["me"]
        self._idx = idx
        self._devtype = dev["devtype"]
        attrs = {
            "agt": self._agt,
            "me": self._me,
            "idx": self._idx,
            "devtype": self._devtype,
        }
        self._attributes = attrs

    @property
    def object_id(self):
        """Return LifeSmart device id."""
        return self.entity_id

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    @property
    def name(self):
        """Return LifeSmart device name."""
        return self._name

    @property
    def assumed_state(self):
        """Return true if we do optimistic updates."""
        return False

    @property
    def should_poll(self):
        """check with the entity for an updated state."""
        return False

    @staticmethod
    async def async_lifesmart_epset(self, type, val, idx):
        # self._tick = int(time.time())
        url = self._svrurl + "/api.EpSet"
        tick = int(time.time())
        appkey = self._appkey
        apptoken = self._apptoken
        userid = self._userid
        usertoken = self._usertoken
        agt = self._agt
        me = self._me
        sdata = (
            "method:EpSet,agt:"
            + agt
            + ",idx:"
            + idx
            + ",me:"
            + me
            + ",type:"
            + type
            + ",val:"
            + str(val)
            + ",time:"
            + str(tick)
            + ",userid:"
            + userid
            + ",usertoken:"
            + usertoken
            + ",appkey:"
            + appkey
            + ",apptoken:"
            + apptoken
        )
        sign = hashlib.md5(sdata.encode(encoding="UTF-8")).hexdigest()
        send_values = {
            "id": 1,
            "method": "EpSet",
            "system": {
                "ver": "1.0",
                "lang": "en",
                "userid": userid,
                "appkey": appkey,
                "time": tick,
                "sign": sign,
            },
            "params": {"agt": agt, "me": me, "idx": idx, "type": type, "val": val},
        }
        header = {"Content-Type": "application/json"}
        send_data = json.dumps(send_values)
        # req = urllib.request.Request(
        #     url=url, data=send_data.encode("utf-8"), headers=header, method="POST"
        # )
        # response = json.loads(urllib.request.urlopen(req).read().decode("utf-8"))
        response = json.loads(await asyncPOST(url, send_data, header))
        # _LOGGER.info("epset_send: %s", str(send_data))
        # _LOGGER.info("epset_res: %s", str(response))
        return response["code"]

    @staticmethod
    async def async_lifesmart_epget(self):
        url = self._svrurl + "/api.EpGet"
        tick = int(time.time())
        appkey = self._appkey
        apptoken = self._apptoken
        userid = self._userid
        usertoken = self._usertoken
        agt = self._agt
        me = self._me
        sdata = (
            "method:EpGet,agt:"
            + agt
            + ",me:"
            + me
            + ",time:"
            + str(tick)
            + ",userid:"
            + userid
            + ",usertoken:"
            + usertoken
            + ",appkey:"
            + appkey
            + ",apptoken:"
            + apptoken
        )
        sign = hashlib.md5(sdata.encode(encoding="UTF-8")).hexdigest()
        send_values = {
            "id": 1,
            "method": "EpGet",
            "system": {
                "ver": "1.0",
                "lang": "en",
                "userid": userid,
                "appkey": appkey,
                "time": tick,
                "sign": sign,
            },
            "params": {"agt": agt, "me": me},
        }
        header = {"Content-Type": "application/json"}
        send_data = json.dumps(send_values)
        # req = urllib.request.Request(
        #   url=url, data=send_data.encode("utf-8"), headers=header, method="POST"
        # )
        # response = json.loads(urllib.request.urlopen(req).read().decode("utf-8"))
        response = json.loads(await asyncPOST(url, send_data, header))
        return response["message"]["data"]

    @staticmethod
    async def async_lifesmart_sceneset(self, type, rgbw):
        # self._tick = int(time.time())
        url = self._svrurl + "/api.SceneSet"
        tick = int(time.time())
        appkey = self._appkey
        apptoken = self._apptoken
        userid = self._userid
        usertoken = self._usertoken
        agt = self._agt
        id = self._me
        sdata = (
            "method:SceneSet,agt:"
            + agt
            + ",id:"
            + id
            + ",time:"
            + str(tick)
            + ",userid:"
            + userid
            + ",usertoken:"
            + usertoken
            + ",appkey:"
            + appkey
            + ",apptoken:"
            + apptoken
        )
        sign = hashlib.md5(sdata.encode(encoding="UTF-8")).hexdigest()
        send_values = {
            "id": 1,
            "method": "SceneSet",
            "system": {
                "ver": "1.0",
                "lang": "en",
                "userid": userid,
                "appkey": appkey,
                "time": tick,
                "sign": sign,
            },
            "params": {"agt": agt, "id": id},
        }
        header = {"Content-Type": "application/json"}
        send_data = json.dumps(send_values)
        # req = urllib.request.Request(
        #     url=url, data=send_data.encode("utf-8"), headers=header, method="POST"
        # )
        # response = json.loads(urllib.request.urlopen(req).read().decode("utf-8"))
        response = json.loads(await asyncPOST(url, send_data, header))
        # _LOGGER.info("sceneset_send: %s", str(send_data))
        # _LOGGER.info("sceneset_res: %s", str(response))
        return response["code"]
