import os.path
import queue

import albumentations as A
import cv2
import numpy as np
import torch
from albumentations.pytorch.transforms import ToTensor

from config import PROJECT_DIR, device
from face_aligner import align_image
from face_aligner import get_detector


def get_image_path(image_name):
    return os.path.join(PROJECT_DIR, 'photos', image_name)


class Worker:
    def __init__(self):
        self.landmarks_detector = get_detector()
        self.model = {'merged': torch.jit.load(os.path.join(PROJECT_DIR, 'models', 'generator_merged_new_scripted.pt'), map_location=device),
                      'cartoon': torch.jit.load(os.path.join(PROJECT_DIR, 'models', 'generator_merged_strong_scripted.pt'), map_location=device)}
        self.transforms = A.Compose([
              A.Resize(512, 512),
              ToTensor()
          ])

        print('Init was succesfully completed')

    def crop_faces(self, image_name: str):
        image_path = get_image_path(image_name)
        faces = list(align_image(self.landmarks_detector, image_path))
        return faces

    def load_image(self, path: str):
        image = cv2.imread(path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return image

    def predict(self, image: np.array, mode: str):
        image = self.transforms(image=image)['image']
        gen = self.model[mode](image.reshape(1, 3, 512, 512))
        gen = torch.moveaxis(gen, 1, -1).detach().cpu().numpy().squeeze() * 255
        gen = gen.astype(np.uint8)
        return gen
