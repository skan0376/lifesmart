import asyncio
import logging
import json
import time
import aiohttp
import hashlib


class Auth:
    def __init__(self, session, appkey, apptoken, password, email):
        self.session = session
        self.appkey = appkey
        self.apptoken = apptoken
        self.password = password
        self.email = email
        self.token = ""
        self.userid = ""
        self.rgn = ""
        self.svrurl = ""
        self.usertoken = ""

    async def asyncPOST(self, url, data, headers):
            async with self.session.post(url, data=data, headers=headers) as response:
                r = await response.text()
                return r

    async def login(self):
        url = "https://api.apz.ilifesmart.com/app/auth.login"

        payload = json.dumps(
            {
                # accuont user email
                "uid": self.email,
                # account password
                "pwd": self.password,
                # app-key from www.ilifesmar.com/open
                "appkey": self.appkey,
            }
        )

        headers = {"Content-Type": "application/json"}

        response = json.loads(await self.asyncPOST(url, payload, headers))

        if response["code"] == "success":
            return response
        return False

    async def do_auth(self):
        url = "https://api.apz.ilifesmart.com/app/auth.do_auth"

        payload = json.dumps(
            {
                "userid": self.userid,
                "token": self.token,
                "appkey": self.appkey,
                "rgn": self.rgn,
            }
        )

        headers = {"Content-Type": "application/json"}

        response = json.loads(await self.asyncPOST(url, payload, headers))
        if response["code"] == "success":
            print("Auth Success")
            return response
        return False

    async def launch_auth_flow(self):
        login_response = await self.login()
        self.token = login_response["token"]
        self.userid = login_response["userid"]
        self.rgn = login_response["rgn"]

        auth_response = await self.do_auth()
        self.svrurl = auth_response["svrurl"]
        self.usertoken = auth_response["usertoken"]

        param = {}
        param["appkey"] = self.appkey
        param["apptoken"] = self.apptoken
        param["usertoken"] = self.usertoken
        param["userid"] = self.userid
        param["rgn"] = self.rgn
        param["svrurl"] = self.svrurl
        return param
