#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author: github.com/imvast
@Date: 
"""

__summary__ = """
- mass dm tool src
- uses multiple user tokens
- captcha key support
- proxy support
- has built in joiner 
- blacklist roles
"""

from os import system, _exit
from time import time, sleep
from json import dumps
from random import choice
from base64 import b64encode
from veilcord import VeilCord
from terminut import log
from colorama import Fore as C
from tls_client import Session
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from modules.solver import solveCaptcha
from modules.models import Config
from modules.scraper import Scraper, MassDMScraper


class Stats:
    sent = 0
    failed = 0
    start = time()


class Joiner:
    def __init__(self, token, invite, proxy: str = None) -> None:
        self.client = Session(
            client_identifier="chrome_108", 
            random_tls_extension_order=True
        )
        self.client.proxies = ({
            "http": f"http://{proxy}",
            "https": f"http://{proxy}",
        } if proxy else None)
        self.invite = invite
        self.headers = {
            "authority": "discord.com",
            "accept": "*/*",
            "accept-language": "en-US",
            "authorization": token,
            "content-type": "application/json",
            "origin": "https://discord.com",
            "referer": "https://discord.com/channels/@me",
            "sec-ch-ua": '"Not?A_Brand";v="8", "Chromium";v="108"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9023 Chrome/108.0.5359.215 Electron/22.3.26 Safari/537.36",
            "x-debug-options": "bugReporterEnabled",
            "x-discord-locale": "en-GB",
            "x-discord-timezone": "America/Chicago",
            "x-super-properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRGlzY29yZCBDbGllbnQiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfdmVyc2lvbiI6IjEuMC45MDIzIiwib3NfdmVyc2lvbiI6IjEwLjAuMjI2MjEiLCJvc19hcmNoIjoieDY0IiwiYXBwX2FyY2giOiJpYTMyIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV09XNjQpIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIGRpc2NvcmQvMS4wLjkwMjMgQ2hyb21lLzEwOC4wLjUzNTkuMjE1IEVsZWN0cm9uLzIyLjMuMjYgU2FmYXJpLzUzNy4zNiIsImJyb3dzZXJfdmVyc2lvbiI6IjIyLjMuMjYiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjoyNDQ4NzQsIm5hdGl2ZV9idWlsZF9udW1iZXIiOjM5NTE1LCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsLCJkZXNpZ25faWQiOjB9",
        }
        self.veilcord = VeilCord(
            session=self.client,
            device_type="app",
            user_agent="Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9023 Chrome/108.0.5359.215 Electron/22.3.26 Safari/537.36",
            device_version="108",
            build_num=glbuildnum,
        )

    def acceptAgreement(self):
        try:
            return self.client.patch(
                "https://discord.com/api/v9/users/@me/agreements",
                headers=self.headers,
                json={"terms": True, "privacy": True},
            )
        except Exception as e:
            print("fail", e)

    def JoinServer(self, capkey: str = None, caprq: str = None):
        try:
            res = self.client.get(
                f"https://discord.com/api/v9/invites/{self.invite}"
            ).json()
            jsonContext = {
                "location": "Join Guild",
                "location_guild_id": str(res["guild"]["id"]),
                "location_channel_id": str(res["channel"]["id"]),
                "location_channel_type": int(res["channel"]["type"]),
            }
            # jsonContext = {
            #     "location": "Invite Button Embed",
            #     "location_guild_id": None,
            #     "location_channel_id": "1173378470307430481",
            #     "location_channel_type": 3,
            #     "location_message_id": "1173433979991498774",
            # }
            json_str = dumps(jsonContext)
            xContext = b64encode(json_str.encode()).decode()
            headers = {
                **self.headers,
                "x-context-properties": xContext,
            }
        except:
            headers = self.headers

        session_id = self.veilcord.getSession(self.headers.get("authorization"))
        payload = {"session_id": session_id}

        if capkey is not None:
            headers["x-captcha-key"] = capkey
            headers["x-captcha-rqtoken"] = caprq

        response = self.client.post(
            f"https://discord.com/api/v9/invites/{self.invite}",
            headers=headers,
            json=payload,
        )
        if "features" in response.text:
            if myconfig.logger.style == "vertical":
                log.vert(
                    "Joined.",
                    Token=self.headers.get("authorization").split(".")[0],
                    Name=response.json().get("guild").get("name"),
                    Code=response.json().get("code"),
                    Captcha=bool(capkey),
                )
            else:
                log.log(
                    "Joined.",
                    Token=self.headers.get("authorization").split(".")[0],
                    Name=response.json().get("guild").get("name"),
                    Code=response.json().get("code"),
                    Captcha=bool(capkey),
                )
            return response.json().get("guild")
        elif "captcha_key" in response.text:
            capSKEY = response.json()["captcha_sitekey"]
            rqtoken = response.json().get("captcha_rqtoken")
            rqdata = response.json().get("captcha_rqdata")
            key = solveCaptcha(
                myconfig, f"https://discord.com/invite/{invite}", capSKEY, rqdata
            )
            return self.JoinServer(key, rqtoken)
        elif response.status_code in [403, 401]:
            log.error("token is flagged/locked")
        else:
            log.debug(f"Join Res: {response.text}", "» ")

        return None


class MassDM(Joiner):
    def __init__(self, token, invite, members, proxy) -> None:
        super().__init__(token, invite, proxy)
        self.members = members

    def openDM(self, uid: str, headers):
        payload = {"recipients": [uid]}

        response = self.client.post(
            "https://discord.com/api/v9/users/@me/channels",
            headers=headers,
            json=payload,
        )
        return response

    def sendDM(
        self,
        user_id,
        message: str = "made by vast",
        captcha: str = None,
        caprq: str = None,
    ):
        headers = {
            **self.headers,
            "X-Context-Properties": "eyJsb2NhdGlvbiI6IlF1aWNrIE1lc3NhZ2UgSW5wdXQifQ==",
        }
        if captcha:
            headers["x-captcha-key"] = captcha
            headers["x-captcha-rqtoken"] = caprq
        response = self.openDM(user_id, headers)
        # {"op":14,"d":{"guild_id":"1171560354774515772","members":["1170915429389172846"]}}
        # {"op":13,"d":{"channel_id":"1178009815767851148"}}
        
        if response.status_code == 200:
            to_user = response.json().get("recipients")[0].get("username")
            chat_id = response.json().get("id")
            payload = {
                "mobile_network_type": "unknown",
                "content": message,
                "tts": False,
                "flags": 0,
            }
            response = self.client.post(
                f"https://discord.com/api/v9/channels/{chat_id}/messages",
                headers=headers,
                json=payload,
            )
            if "content" in response.text:
                Stats.sent += 1
                log.log(
                    f"[{Stats.sent}] DM Sent",
                    To=to_user,
                    From=response.json().get("author").get("username"),
                )
            elif "captcha" in response.text:
                log.debug("DM Res: Captcha Detected. Solving...", "» ")
                capSKEY = response.json().get("captcha_sitekey")
                rqtoken = response.json().get("captcha_rqtoken")
                rqdata = response.json().get("captcha_rqdata")
                key = solveCaptcha(myconfig, "https://discord.com/", capSKEY, rqdata)
                return self.sendDM(user_id, message, key, rqtoken)
            else:
                log.debug(f"DM Res: {response.text}", "» ")
        elif response.status_code == 401:
            log.error("token is flagged/locked")

    def main(self):
        has_to_verify = False # TODO: add a checker for this
        if has_to_verify:
            self.acceptAgreement()
        if self.JoinServer():
            for user in self.members:
                sleep(myconfig.wait_time)
                self.sendDM(user, choice(messages))


def start():
    log.debug("Scraping...", "» ")

    token = myconfig.scraper.token
    channel_id = myconfig.scraper.channel_id
    invite = myconfig.invite

    guild_id = Joiner(token, invite).JoinServer().get("id")

    scraper = MassDMScraper(token)
    roles = scraper._get_roles(guild_id)
    users = scraper._get_members(guild_id, channel_id)
    tokens = scraper._get_tokens()
    messages = scraper._get_messages()

    if myconfig.logger.style == "vertical":
        log.vert(
            "Successfully Scraped.", 
            Users=len(users), 
            Roles=len(roles), 
            Tokens=len(tokens),
            Messages=len(messages)
        )
    else:
        log.log(
            "Successfully Scraped.", 
            Users=len(users), 
            Roles=len(roles), 
            Tokens=len(tokens),
            Messages=len(messages)
        )

    return invite, users, tokens, messages


def main(tokens, invite, users):
    chunk_size, remainder = divmod(len(users), len(tokens))
    log.debug(
        f"Starting with {chunk_size} users per token. ({len(users)}/{len(tokens)})",
        "» ",
    )
    start_idx = 0

    with ThreadPoolExecutor(max_workers=myconfig.threads) as executor:
        for i, token in enumerate(tokens):
            end_idx = start_idx + chunk_size + (1 if i < remainder else 0)
            mdm_ctx = MassDM(
                token, invite, users[start_idx:end_idx], choice(Scraper()._get_proxies())
            )
            executor.submit(mdm_ctx.main)
            start_idx = end_idx


if __name__ == "__main__":
    glbuildnum = VeilCord.getBuildNum()
    system("cls")
    cl1 = C.MAGENTA
    cl2 = C.LIGHTMAGENTA_EX
    print(cl1 + f"""
      ┬  ┬┌─┐┌─┐┌┬┐{cl2}╔╦╗╔╦╗{cl1}
      └┐┌┘├─┤└─┐ │ {cl2} ║║║║║{cl1}
       └┘ ┴ ┴└─┘ ┴ {cl2}═╩╝╩ ╩{cl1}
         
    [INFO]
    {cl2}@{cl1} BuildNum: {cl2}{glbuildnum}{cl1}
    {cl2}@{cl1} Version:  {cl2}1.0.0{cl1}
    {cl2}@{cl1} Author:   {cl2}imvast{cl1}
    """)

    myconfig: Config = Scraper()._load_config()
    invite, users, tokens, messages = start()

    Stats()
        
    main(tokens, invite, users)