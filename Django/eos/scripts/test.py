import os
import cv2

import eos.scripts.AbstractTestClass as ATC

class Test(ATC.AbstractTestClass):
    def get_args():
        return ['all','27','25','20', '30']
    def run():
        return None
    def progress():
        return None
    def set_default_storage_path(path):
        self.storage_path = path
    def get_return_codes():
        return None
