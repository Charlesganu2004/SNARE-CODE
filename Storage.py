import json

class Storage:
    FILE_NAME = "data.json"

    @staticmethod
    def save(data):
        with open(Storage.FILE_NAME, "w") as f:
            json.dump(data, f)

    @staticmethod
    def load():
        try:
            with open(Storage.FILE_NAME, "r") as f:
                return json.load(f)
        except:
            return []

    @staticmethod
    def clear():
        with open(Storage.FILE_NAME, "w") as f:
            f.write("")
