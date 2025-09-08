import requests
import log
import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from pathlib import Path
import urllib.parse

logger = log.get_logger("karte")


def exists_key_in_responce(data: dict, key: str) -> bool:
    if key in data:
        return True
    logger.error(f"backend responce does not include the key: f{key}")
    return False


def one_replay_task(
    parsed_res_get_replay: dict,
    settings: dict,
    memory: dict,
    fetched_metadata_txt: Path,
) -> str:
    if not exists_key_in_responce(parsed_res_get_replay, "replay_id"):
        return "error"
    if parsed_res_get_replay["replay_id"] <= memory["known_id"]:
        has_fetched_all_files = True
        logger.info(
            f"Encounted an already retrieved replay. Stopping further exploration."
        )
        return "end"

    if not exists_key_in_responce(parsed_res_get_replay, "uploaded_at"):
        return "error"
    try:
        replay_uploaded_at = datetime.fromisoformat(
            parsed_res_get_replay["uploaded_at"]
        )
    except ValueError:
        logger.error(
            f"uploaded_at key is not iso format: {parsed_res_get_replay["uploaded_at"]}"
        )
        return "error"
    if datetime.now(ZoneInfo(settings["timezone"])) - replay_uploaded_at > timedelta(
        days=settings["search_days_back"]
    ):
        logger.info(
            f"Replay older than {settings["search_days_back"]} days detected. Terminating search. the replay uploaded at {parsed_res_get_replay["uploaded_at"]}"
        )
        has_fetched_all_files = True
        return "end"

    if not exists_key_in_responce(parsed_res_get_replay, "filename"):
        return "error"

    if not exists_key_in_responce(parsed_res_get_replay, "game_id"):
        return "error"
    if parsed_res_get_replay["game_id"] not in settings["games"].keys():
        logger.error(f"Encounted unknown game: {parsed_res_get_replay["game_id"]}")
        return "error"

    # ファイルがダウンロードできなかったらメタデータ情報を書かずに次のリプレイへ移行する
    # ユーザがメタデータ情報だけ見てリプレイファイルがダウンロードできていると勘違いする可能性があるため
    if not exists_key_in_responce(parsed_res_get_replay, "replay_id"):
        return "error"
    try:
        file_download_url = f"{settings["backend_url"]}/replays/{parsed_res_get_replay["replay_id"]}/file"
        res_replay_file = requests.get(url=file_download_url)
        res_replay_file.raise_for_status()
        logger.info(
            f"requested replay binary file to L-uploader, and it responced. url: {file_download_url}"
        )
        binary_res_replay_file = res_replay_file.content
        logger.info(f"binary parsed.")

    except Exception as e:
        logger.exception(e)
        return "error"

    game_path = Path(settings["games"][parsed_res_get_replay["game_id"]]["path"])
    # 0始まりにして0の場合はスキップさせる
    # リネーム制限しない場合の処理をリネーム処理と同等に扱うため
    for storage_file_id in range(
        settings["games"][parsed_res_get_replay["game_id"]]["ud_replay_rename_limit"]
        + 1
    ):

        if storage_file_id == 0:
            continue

        cur_replay_file = (
            game_path / f"{parsed_res_get_replay["game_id"]}_{storage_file_id:02}.rpy"
        )
        if not cur_replay_file.exists():
            replay_file = cur_replay_file
            break

    else:
        replay_file = game_path / f"{parsed_res_get_replay["filename"]}"

    replay_file.write_bytes(binary_res_replay_file)
    logger.info(f"storage in {str(replay_file)}")

    game_name = settings["games"][parsed_res_get_replay["game_id"]]["game_name"]
    user_name = parsed_res_get_replay["user_name"][
        : settings["user_name_truncate_with"]
    ]
    upload_comment = parsed_res_get_replay["upload_comment"][
        : settings["upload_comment_truncate_with"]
    ]

    write_replay_summary = settings["replay_summary"].format(
        game_name=game_name,
        user_name=user_name,
        upload_comment=upload_comment,
    )

    with fetched_metadata_txt.open(mode="a") as fp:
        fp.write(str(replay_file) + "\n" + write_replay_summary + "\n\n")
    logger.info(f"wrote replay summary: {write_replay_summary}")

    return "continue"


def main_task(settings: dict):

    page = 0
    init_memory = {"known_id": -1}

    karte_homedir = Path(settings["karte_homedir"])
    memory_json = karte_homedir / "memory.json"
    fetched_metadata_txt = karte_homedir / "fetched_metadata.txt"

    if memory_json.exists():
        memory = json.loads(memory_json.read_text())
        logger.info(f"{str(memory_json)} is loaded.")
    else:
        memory = init_memory
        memory_json.write_text(json.dumps(memory))
        logger.warning(f"{str(memory_json)} is not found. So I created new file.")

    if not fetched_metadata_txt.exists():
        fetched_metadata_txt.write_text("")

    has_fetched_all_files = False

    # page loop
    for page in range(settings["max_page"]):

        url = f"{settings["backend_url"]}/replays?order=desc&page={page}&optional_tag={urllib.parse.quote(settings["optional_tag"])}"
        try:
            res_get_replays = requests.get(url=url)
            res_get_replays.raise_for_status()
        except Exception as e:
            logger.exception(e)
            continue
        logger.info(
            f"requested replay meta infomations to L-uploader, and it responced. url: {url}"
        )
        parsed_res_get_replays = json.loads(res_get_replays.text)
        logger.info(f"parsed responce.")

        if page == 0:
            if memory["known_id"] < parsed_res_get_replays[0]["replay_id"]:
                memory_json.write_text(
                    json.dumps({"known_id": parsed_res_get_replays[0]["replay_id"]})
                )
                logger.info(
                    f"I memory what latest fetched replay. id: {parsed_res_get_replays[0]["replay_id"]}"
                )
            elif memory["known_id"] == parsed_res_get_replays[0]["replay_id"]:
                logger.info(f"already fetched latest replay. id: {memory["known_id"]}")
            else:
                logger.info(
                    f"invalid replay id. memory: {memory["known_id"]} ,fetched: {parsed_res_get_replays[0]["replay_id"]}"
                )

        if len(parsed_res_get_replays) == 0:
            logger.info(f"Reached oldest page. Stopping further exploration.")
            return

        for parsed_res_get_replay in parsed_res_get_replays:
            try:
                if (
                    one_replay_task(
                        parsed_res_get_replay, settings, memory, fetched_metadata_txt
                    )
                    == "end"
                ):
                    return
            except Exception as e:
                logger.exception(e)
                continue

            try:
                if len(parsed_res_get_replays) < settings["posts_per_page"]:
                    logger.info(
                        f"The number of this page's posts is {len(parsed_res_get_replays)}. this is fewer than {settings["posts_per_page"]}. I judged this page is oldest page. Stopping further exploration."
                    )
                    return
            except Exception as e:
                logger.exception(e)
