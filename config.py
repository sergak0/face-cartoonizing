import os
import torch
from dataclasses import dataclass

device = torch.device('cpu')
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
