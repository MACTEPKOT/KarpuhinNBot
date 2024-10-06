import yadisk


class YandexDiskClient:
    def __init__(self, token):
        self.yadisk = yadisk.YaDisk(token=token)

    def check_new_files(self, folder_path):
        """
        Проверяет наличие новых файлов в указанной папке.

        :param folder_path: Путь к папке на Яндекс Диске.
        :return: Список файлов в папке.
        """
        try:
            files = self.yadisk.listdir(folder_path)
            return files
        except yadisk.exceptions.UnauthorizedError:
            print("Ошибка: Неверный токен.")
            return []
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            return []

    def upload_file(self, local_file_path, remote_folder_path):
        """
        Загружает файл из локального хранилища на Яндекс Диск.

        :param local_file_path: Путь к локальному файлу.
        :param remote_folder_path: Путь к папке на Яндекс Диске, куда будет загружен файл.
        :return: Статус операции.
        """
        try:
            self.yadisk.upload(local_file_path, remote_folder_path)
            print(f"Файл {local_file_path} успешно загружен в {remote_folder_path}.")
            return True
        except Exception as e:
            print(f"Ошибка при загрузке файла: {e}")
            return False

    def delete_file(self, remote_file_path):
        """
        Удаляет файл на Яндекс Диске.

        :param remote_file_path: Путь к файлу на Яндекс Диске.
        :return: Статус операции.
        """
        try:
            self.yadisk.remove(remote_file_path)
            print(f"Файл {remote_file_path} успешно удалён.")
            return True
        except Exception as e:
            print(f"Ошибка при удалении файла: {e}")
            return False
