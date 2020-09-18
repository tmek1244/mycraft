import yaml


class Settings:
    settings = None

    def __init__(self):
        with open("config.yml", "r") as config_file:
            Settings.settings = yaml.safe_load(config_file)

    def __call__(self):
        return Settings.settings

    def __getitem__(self, item):
        return Settings.settings[item]

    @staticmethod
    def get_chunk_size():
        return Settings.settings['chunk_size']

    @staticmethod
    def get_max_height():
        return Settings.settings['max_height']
