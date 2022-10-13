import jsonlines
from datetime import datetime


def write_jsonlines_to_bucket(path: str, lines: list[dict]) -> None:
    """Write list of dictionaries to file.

    :param path: path to data folder
    :param lines: content to write to file
    """
    file_path = path + f"{datetime.now().isoformat()}_comment_backup.jsonl"
    with jsonlines.open(file_path, "w") as handle:
        for line in lines:
            handle.write(line)

