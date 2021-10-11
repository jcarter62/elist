from os import listdir

from flask import current_app
import os


class EmployeePicture:
    _id: int
    _image_path: str
    _current_app = None
    _image_path = ''
    _root_path = ''
    _employee_path = ''
    _image_count = 0

    def __init__(self, employeeID: str = '0') -> None:
        self._id = employeeID
        self._image_path = ''
        # obtain image path from environment
        self._current_app = current_app
        self._root_path = self._current_app.config['IMAGE_PATH']
        self._employee_path = os.path.join(self._root_path, employeeID.zfill(5))
        self._init_folder()
        self._image_count = self._count_images()
        if self._image_count > 1:
            self._determine_default_image()

        return

    def _init_folder(self):
        if not os.path.exists(self._employee_path):
            os.makedirs(self._employee_path, exist_ok=True)
        return

    # count number of images
    def _count_images(self):
        image_count = 0
        for f in listdir(self._employee_path):
            if f.endswith('.jpg') or f.endswith('.png'):
                image_count += 1
                self._image_path = os.path.join(self._employee_path, f)
        return image_count

    def getimagepath(self) -> str:
        return self._image_path

    def get_image_folder(self) -> str:
        return self._employee_path

    def _determine_default_image(self):
        pass

