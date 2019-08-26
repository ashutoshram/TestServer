from abc import ABC, abstractmethod


class AbstractTestClass(ABC):
    @abstractmethod
    def get_args(self):
        return None

    @abstractmethod
    def run(self, args, q, results):
        return None

    @abstractmethod
    def get_progress(self):
        return None

    @abstractmethod
    def set_default_storage_path(self, path):
        self.storage_path = path

    @abstractmethod
    def get_storage_path(self):
        return self.storage_path

    @abstractmethod
    def generate_report(self):
        return None

    @abstractmethod
    def is_done(self):
        return None

    @abstractmethod
    def get_name(self):
        return None
