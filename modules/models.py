from dataclasses import dataclass

@dataclass
class ScraperConfig:
    token: str
    channel_id: str
    
@dataclass
class CaptchaConfig:
    capService: str
    capKey: str
    
@dataclass
class LoggerConfig:
    style: str
    style_types: list[str] # ignore

@dataclass
class Config:
    threads: int
    invite: str
    wait_time: int
    scraper: ScraperConfig
    captcha: CaptchaConfig
    logger: LoggerConfig