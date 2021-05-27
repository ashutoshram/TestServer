from abc import ABC, abstractmethod


class AbstractTestClass(ABC):
    @abstractmethod
    def get_args(self):
        return None

    @abstractmethod
    def run(self, args):
        return None
