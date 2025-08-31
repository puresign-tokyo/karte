import json5
import json
import time
import requests
from pathlib import Path
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import log
import setting
import sys
import task

log.init_logger()
logger = log.get_logger("karte")

settings = setting.get_setting()
init_memory = {"known_id": -1}


while True:
    logger.info("task start.")
    task.main_task(settings=settings)
    logger.info("task end.")
    # あんまし過度にリクエストしてほしくないのでユーザ側で決めさせずハードコード
    time.sleep(180)
