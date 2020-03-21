import PIL.Image as Image
import numpy as np
from matplotlib import pyplot as plt
import torchvision.transforms.functional as F
from torchvision import datasets, transforms
from model import CSRNet
import torch


class PeopleCounter:
    def __init__(self,checkpoint_path='0model_best.pth.tar'):
        self.transform=transforms.Compose([
                               transforms.ToTensor(),transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                             std=[0.229, 0.224, 0.225]),
                           ])
        self.model = CSRNet()
        self.model = self.model.cuda()
        self.checkpoint = torch.load(checkpoint_path)
        self.model.load_state_dict(self.checkpoint['state_dict'])

    def countPeople(self, img):
        img = self.transform(img.convert('RGB')).cuda()
        output = self.model(img.unsqueeze(0))
        return int(output.detach().cpu().sum().numpy())
