from abc import ABC, abstractmethod


class AbstractTestClass(ABC):
    @abstractmethod
    def get_args(self):
        return None

    @abstractmethod
    def run(self, args):
        return None

    @abstractmethod
    def get_progress(self):
        return None

    @abstractmethod
    def set_default_storage_path(self, path):
        self.storage_path = path

    @abstractmethod
    def generate_report(self):
        return None

    @abstractmethod
    def is_done(self):
        return None

    @abstractmethod
    def get_name(self):
        return None
