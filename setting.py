from zoneinfo import ZoneInfo
import json5
import log
from pathlib import Path

logger = log.get_logger("karte")


def check_settings(setting_data: dict) -> bool:
    def exists_settings_key(key: str, value_type: type) -> bool:
        if key not in setting_data:
            logger.critical(f"setting data does not include the key: {key}")
            return False
        if not isinstance(setting_data[key], value_type):
            logger.critical(f"{key} is not {value_type}: {type(setting_data[key])}")
            return False
        return False

    def exists_settings_game_key(game: str, key: str, value_type: type) -> bool:
        if key not in setting_data["games"][game]:
            logger.critical(f"setting data does not include the key in {game} :{key}")
            return False
        if not isinstance(setting_data[key], value_type):
            logger.critical(
                f"{key} of {game} is not {value_type}: {type(setting_data[key])}"
            )
            return False
        return False

    if not exists_settings_key("backend_url", str):
        return False
    if not exists_settings_key("search_days_back", int):
        return False
    if not exists_settings_key("optional_tag", str):
        return False
    if not exists_settings_key("karte_homedir", str):
        return False
    if not exists_settings_key("posts_per_page", int):
        return False
    if not exists_settings_key("max_page", int):
        return False
    if not exists_settings_key("games", dict):
        return False
    if not exists_settings_key("replay_summary", str):
        return False
    if not exists_settings_key("user_name_truncate_with", int):
        return False
    if not exists_settings_key("upload_comment_truncate_with", int):
        return False
    if not exists_settings_key("timezone", str):
        return False
    try:
        ZoneInfo(setting_data["timezone"])
    except ValueError:
        logger.critical(f"invalid timezone name {setting_data["timezone"]}")
        return False

    critical_error_in_game_setting = False
    for game in setting_data["games"].keys():
        if not exists_settings_game_key(game, "game_name", str):
            critical_error_in_game_setting = True
            break
        if not exists_settings_game_key(game, "path", str):
            critical_error_in_game_setting = True
            break
        if not exists_settings_game_key(game, "ud_replay_rename_limit", int):
            critical_error_in_game_setting = True
            break
    if critical_error_in_game_setting:
        return False
    logger.info("correct settings.")
    return True


def get_setting() -> dict:
    settings_json = Path("settings.json")
    if not settings_json.exists():
        logger.info("settings.json is not found.")
        raise
    with open("settings.json", "r", encoding="utf-8") as fp:
        settings = json5.load(fp)
    check_settings(settings)
    return settings
