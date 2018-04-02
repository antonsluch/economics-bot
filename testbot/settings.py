import json


class SettingsDict(dict):
    def __init__(self, file_path: str, *args, **kwargs):
        super(SettingsDict, self).__init__(*args, **kwargs)
        with open(file_path) as json_data:
            self.update(json.load(json_data))
        self.file_path = file_path

    def __getattr__(self, item):
        try:
            return self.__getitem__(item)
        except KeyError:
            return None

    def __setitem__(self, key, value):
        super(SettingsDict, self).__setitem__(key, value)
        self.save()

    def __setattr__(self, key, value):
        self.__setitem__(key, value)
        self.save()

    def save(self):
        with open(self.file_path, "w") as json_data:
            json.dump(self, json_data)


settings = SettingsDict("settings.json")
