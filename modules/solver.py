from veilcord import Solver
from requests import Session
from random import choice
from modules.scraper import Scraper
from modules.models import Config

def solveCaptcha(Config: Config, url, sitekey, rqdata: str = None):
    session = Session()
    cproxy = choice(Scraper()._get_proxies())
    session.proxies = {
        "http": f"http://{cproxy}",
        "https": f"http://{cproxy}",
    }
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0"
    key = Solver(
        session, 
        Config.captcha.capService,
        Config.captcha.capKey,
        siteKey=sitekey,
        siteUrl=url,
        rqData=rqdata,
        user_agent=user_agent
    ).solveCaptcha()
    return key