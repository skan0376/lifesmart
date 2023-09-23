import asyncio
import logging
import json
import time
import aiohttp
import hashlib
from .constants import *

from aiohttp import ClientConnectorError, ClientWebSocketResponse, WSMessage
from homeassistant.helpers.aiohttp_client import async_get_clientsession

RETRY_DELAYS = [15, 60, 5 * 60, 15 * 60, 60 * 60]
_LOGGER = logging.getLogger(__name__)


class Cloud:
    def __init__(self, data, hass):
        self.apptoken = data["apptoken"]
        self.appkey = data["appkey"]
        self.usertoken = data["usertoken"]
        self.userid = data["userid"]
        self.wsurl = "wss://api.apz.ilifesmart.com:8443/wsapp/"
        self.hass = hass

    async def asyncPOST(self, url, data, headers):
        async with async_get_clientsession(self.hass) as session:
            async with session.post(url, data=data, headers=headers) as response:
                r = await response.text()
                return r

    def get_socket_request(self):
        tick = int(time.time())

        sdata = (
            "method:WbAuth,time:"
            + str(tick)
            + ",userid:"
            + self.userid
            + ",usertoken:"
            + self.usertoken
            + ",appkey:"
            + self.appkey
            + ",apptoken:"
            + self.apptoken
        )
        sign = hashlib.md5(sdata.encode(encoding="UTF-8")).hexdigest()
        payload = json.dumps(
            {
                "id": 957,
                "method": "WbAuth",
                "system": {
                    "ver": "1.0",
                    "lang": "en",
                    "userid": self.userid,
                    "appkey": self.appkey,
                    "time": tick,
                    "sign": sign,
                },
            }
        )
        return payload

    async def callback(self, msg):
        await self.on_message(msg)

    async def prompt_and_send(self, ws, msg):
        await ws.send_str(msg)

    async def set_Event(self, msg):
        if msg["msg"]["idx"] != "s":
            devtype = msg["msg"]["devtype"]
            # agt = msg['msg']['agt'].replace("_","")
            agt = msg["msg"]["agt"][:-3]
            if devtype in SWTICH_TYPES and msg["msg"]["idx"] in [
                "L1",
                "L2",
                "L3",
                "P1",
                "P2",
                "P3",
            ]:
                enid = (
                    "switch."
                    + (
                        devtype
                        + "_"
                        + agt
                        + "_"
                        + msg["msg"]["me"]
                        + "_"
                        + msg["msg"]["idx"]
                    ).lower()
                )
                attrs = self.hass.states.get(enid).attributes
                if msg["msg"]["type"] % 2 == 1:
                    self.hass.states.async_set(enid, "on", attrs)
                else:
                    self.hass.states.async_set(enid, "off", attrs)

        # AI event
        if (
            msg["msg"]["idx"]
            == "s"
            # and msg["msg"]["me"] in ai_include_items
            # and msg["msg"]["agt"] in ai_include_agts
        ):
            _LOGGER.info("AI Event: %s", str(msg))
            devtype = msg["msg"]["devtype"]
            agt = msg["msg"]["agt"][:-3]
            enid = (
                "switch."
                + (
                    devtype
                    + "_"
                    + agt
                    + "_"
                    + msg["msg"]["me"]
                    + "_"
                    + msg["msg"]["idx"]
                ).lower()
            )
            attrs = self.hass.states.get(enid).attributes

            if msg["msg"]["stat"] == 3:
                self.hass.states.async_set(enid, "on", attrs)
            elif msg["msg"]["stat"] == 4:
                self.hass.states.async_set(enid, "off", attrs)

    async def on_message(self, message):
        try:
            msg = json.loads(message)
            if "type" not in msg:
                _LOGGER.info("Websocket_msg: %s", str(msg["message"]))
                return
            if msg["type"] != "io":
                return
            await self.set_Event(msg)
        except Exception as e:
            _LOGGER.error("Cloud WS exception", exc_info=e)

    async def run_forever(self):
        fails = 0

        while True:
            if not await self.connect():
                # self.set_online(False)

                delay = RETRY_DELAYS[fails]
                _LOGGER.debug(f"Cloud connection retrying in {delay} seconds")
                if fails + 1 < len(RETRY_DELAYS):
                    fails += 1
                await asyncio.sleep(delay)
                continue

            fails = 0

    def start(self):
        task = asyncio.create_task(self.run_forever())

    async def connect(self) -> bool:
        try:
            async with async_get_clientsession(self.hass).ws_connect(self.wsurl) as ws:
                await self.prompt_and_send(ws, self.get_socket_request())
                async for msg in ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        await self.callback(msg.data)
                    elif msg.type == aiohttp.WSMsgType.CLOSED:
                        break
                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        break

            return True

        except ClientConnectorError as e:
            _LOGGER.warning(f"Cloud WS Connection error: {e}")

        except Exception as e:
            _LOGGER.error("Cloud WS exception", exc_info=e)

        return False
