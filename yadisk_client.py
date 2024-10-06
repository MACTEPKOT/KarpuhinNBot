import yadisk

class YandexDiskClient:
    def __init__(self, token):
        self.yadisk = yadisk.YaDisk(token=token)

    def check_new_files(self, folder_path):
        files = self.yadisk.listdir(folder_path)
        return files
