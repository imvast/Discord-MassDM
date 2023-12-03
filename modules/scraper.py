from httpx import Client
from json import load
from modules.ihatethiscode import scrape
from modules.formatter import Formatter
from modules.models import Config, ScraperConfig, CaptchaConfig, LoggerConfig


class Scraper:
    BASE_FOLDER = "./data"

    @classmethod
    def _get_blacklisted_roles(cls) -> list[str]:
        with open(f"{cls.BASE_FOLDER}/role_blacklist.txt", "r") as f:
            return [str(i.strip()) for i in f.readlines()]
        
    @classmethod
    def _get_tokens(cls) -> list[str]:
        with open(f"{cls.BASE_FOLDER}/tokens.txt", "r") as f:
            return Formatter._format_tokens([i.strip() for i in f.readlines()])

    @classmethod
    def _get_proxies(cls):
        with open(f"{cls.BASE_FOLDER}/proxies.txt", "r") as f:
            return Formatter._format_proxies([i.strip() for i in f.readlines()])

    @classmethod
    def _get_messages(cls):
        with open(f"{cls.BASE_FOLDER}/messages.txt", "r") as f:
            return [str(f.strip()) for f in f.readlines()]

    @classmethod
    def _load_config(cls) -> Config:
        with open(f"{cls.BASE_FOLDER}/config.json", "r") as file:
            config_data = load(file)

        scraper_config = ScraperConfig(**config_data.get("scraper", {}))
        captcha_config = CaptchaConfig(**config_data.get("captcha", {}))
        logger_config  = LoggerConfig(**config_data.get("logger", {}))

        return Config(
            config_data["threads"],
            config_data["invite"], 
            config_data["wait_time"],
            scraper_config, 
            captcha_config,
            logger_config
        )


class MassDMScraper(Scraper):
    def __init__(self, token) -> None:
        super().__init__()
        self.client = Client()
        self.token = token
        self.blacklisted_roles = self._get_blacklisted_roles()

    def _get_members(self, guild_id, channel_id):
        return scrape(
            self.token, 
            guild_id, 
            channel_id, 
            self.blacklisted_roles
        )

    def _get_roles(self, guild_id):
        return Formatter._format_roles(
            self.client.get(
                f"https://discord.com/api/v9/guilds/{guild_id}",
                headers={"Authorization": self.token},
            )
            .json()
            .get("roles"),
            self.blacklisted_roles,
        )

    def _check_user(self):
        ... # TODO: check if the user needs to accept terms & if its invalid/spammer/etc
        