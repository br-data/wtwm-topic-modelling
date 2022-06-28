from src.tools import load_config, load_comments, store_comments

# NOT MEANT TO BE PART OF THIS REPO!
CONFIG_PATH = "config.json"


def run(config_path: str = CONFIG_PATH) -> None:
    """Run wrapper function.

    :param config_path: location of config path
    """
    config = load_config(config_path)
    comments = load_comments(config)
    store_comments(config, comments)


if __name__ == "__main__":
    run()
