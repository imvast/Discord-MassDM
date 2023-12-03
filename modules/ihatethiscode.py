import websocket
import time
import threading
import json
from terminut import log


class DiscordSocket(websocket.WebSocketApp): # idek who the og of this is but im too lazy to remake 💀
    def __init__(self, token, guild_id, channel_id, blroles):
        self.BLACKLISTED_ROLES: list[str] = blroles
        self.MAX_ITER = 10
        self.token = token
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.endScraping = False
        self.guilds = {}
        self.members = set()
        self.ranges = [[0]]
        self.lastRange = 0
        self.packets_recv = 0
        self.msgs = []
        self.d = 1
        self.iter = 0
        self.finished = False
        super().__init__(
            "wss://gateway.discord.gg/?encoding=json&v=9",
            header={
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-US,en;q=0.9",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
                "Sec-WebSocket-Extensions": "permessage-deflate; client_max_window_bits",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
            },
            on_open=lambda ws: self.sock_open(ws),
            on_message=lambda ws, msg: self.sock_message(ws, msg),
            on_close=lambda ws, close_code, close_msg: self.sock_close(
                ws, close_code, close_msg
            ),
        )

    def getRanges(self, index, multiplier, memberCount):
        initialNum = int(index * multiplier)
        rangesList = [[initialNum, initialNum + 99]]

        if memberCount > initialNum + 99:
            rangesList.append([initialNum + 100, initialNum + 199])

        if [0, 99] not in rangesList:
            rangesList.insert(0, [0, 99])

        return rangesList

    def parseGuildMemberListUpdate(self, response):
        memberdata = {
            "online_count": response["d"]["online_count"],
            "member_count": response["d"]["member_count"],
            "id": response["d"]["id"],
            "guild_id": response["d"]["guild_id"],
            "hoisted_roles": response["d"]["groups"],
            "types": [],
            "locations": [],
            "updates": [],
        }
        for chunk in response["d"]["ops"]:
            memberdata["types"].append(chunk["op"])
            if chunk["op"] in ("SYNC", "INVALIDATE"):
                memberdata["locations"].append(chunk["range"])
                if chunk["op"] == "SYNC":
                    memberdata["updates"].append(chunk["items"])
                else:
                    memberdata["updates"].append([])
            elif chunk["op"] in ("INSERT", "UPDATE", "DELETE"):
                memberdata["locations"].append(chunk["index"])
                if chunk["op"] == "DELETE":
                    memberdata["updates"].append([])
                else:
                    memberdata["updates"].append(chunk["item"])
        return memberdata

    def find_most_reoccuring(self, data):
        return max(set(data), key=data.count)

    def run(self) -> list[str]:
        try:
            self.run_forever()
            self.finished = True
            return list(set(self.members))
        except Exception as e:
            log.error(e)
            pass

    def scrapeUsers(self):
        if not self.endScraping:
            payload = {
                "op": 14,
                "d": {
                    "guild_id": self.guild_id,
                    "typing": True,
                    "activities": True,
                    "threads": True,
                    "channels": {self.channel_id: self.ranges},
                },
            }
            self.send(json.dumps(payload))

    def sock_open(self, ws):
        payload = {
            "op": 2,
            "d": {
                "token": self.token,
                "capabilities": 125,
                "properties": {
                    "os": "Windows",
                    "browser": "Firefox",
                    "device": "",
                    "system_locale": "en-US",
                    "browser_user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/119.0",
                    "browser_version": "119.0",
                    "os_version": "10",
                    "referrer": "",
                    "referring_domain": "",
                    "referrer_current": "",
                    "referring_domain_current": "",
                    "release_channel": "stable",
                    "client_build_number": 103981,
                    "client_event_source": None,
                },
                "presence": {
                    "status": "online",
                    "since": 0,
                    "activities": [],
                    "afk": False,
                },
                "compress": False,
                "client_state": {
                    "guild_hashes": {},
                    "highest_last_message_id": "0",
                    "read_state_version": 0,
                    "user_guild_settings_version": -1,
                    "user_settings_version": -1,
                },
            },
        }
        self.send(json.dumps(payload))

    def heartbeatThread(self, interval):
        try:
            while True:
                self.send('{"op":1,"d":' + str(self.packets_recv) + "}")
                time.sleep(interval)
        except Exception as e:
            return False

    def sock_message(self, ws, message):
        try:
            decoded = json.loads(message)
            if decoded is None:
                return

            op = decoded.get("op")
            t = decoded.get("t")
            d = decoded.get("d")

            if op != 11:
                self.packets_recv += 1

            if op == 10:
                threading.Thread(
                    target=self.heartbeatThread,
                    args=(d.get("heartbeat_interval", 0) / 1000,),
                    daemon=True,
                ).start()

            if t == "READY":
                for guild in d.get("guilds", []):
                    self.guilds[guild["id"]] = {"member_count": guild["member_count"]}

            if t == "READY_SUPPLEMENTAL":
                self.ranges = self.getRanges(0, 100, self.guilds[self.guild_id]["member_count"])
                self.scrapeUsers()

            elif t == "GUILD_MEMBER_LIST_UPDATE":
                parsed = self.parseGuildMemberListUpdate(decoded)
                self.msgs.append(len(self.members))

                print(f"Scraping... [{len(self.members)}/{self.guilds[self.guild_id]['member_count']}]", end="\r")

                if self.guilds[self.guild_id]["member_count"] == len(self.members):
                    self.endScraping = True
                    self.close()
                    return

                if self.d == len(self.members) or self.guilds[self.guild_id]["member_count"] == len(self.members):
                    self.iter += 1
                    if self.iter == self.MAX_ITER:
                        self.endScraping = True
                        self.close()
                        return

                self.d = self.find_most_reoccuring(self.msgs)

                if parsed["guild_id"] == self.guild_id and ("SYNC" in parsed["types"] or "UPDATE" in parsed["types"]):
                    for elem, index in enumerate(parsed["types"]):
                        if index == "SYNC":
                            for item in parsed["updates"]:
                                if len(item) > 0:
                                    for member in item:
                                        if "member" in member:
                                            mem = member["member"]
                                            if not mem["user"].get("bot") and any(role in mem["roles"] for role in self.BLACKLISTED_ROLES):
                                                self.members.add(str(mem["user"]["id"]))
                        elif index == "UPDATE":
                            for item in parsed["updates"][elem]:
                                if isinstance(item, dict) and "member" in item and isinstance(item["member"], dict):
                                    mem = item["member"]
                                    if not mem["user"].get("bot") and any(role in mem["roles"] for role in self.BLACKLISTED_ROLES):
                                        self.members.add(str(mem["user"]["id"]))

                        self.lastRange += 1
                        self.ranges = self.getRanges(self.lastRange, 100, self.guilds[self.guild_id]["member_count"])
                        time.sleep(0.45)
                        self.scrapeUsers()

                if self.endScraping:
                    self.close()

        except Exception as e:
            log.error(e)
            return False



def scrape(token, guild_id, chanid, role_blacklist: list[str] = []):
    members = DiscordSocket(token, guild_id, chanid, role_blacklist).run()

    return members
