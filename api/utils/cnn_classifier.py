import torch
import os
import torch.nn as nn
from PIL import Image
from torchvision import transforms

num_classes = 2

class SimpleCNN(nn.Module):
    def __init__(self):
        super(SimpleCNN, self).__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(3, 16, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(16, 32, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2)
        )
        self.fc = nn.Sequential(
            nn.Linear(32*7*7, 64),
            nn.ReLU(),
            nn.Linear(64, num_classes)
        )

    def forward(self, x):
        x = self.conv(x)
        x = x.view(x.size(0), -1)
        x = self.fc(x)
        return x

def load_model():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = SimpleCNN()
    model_path = os.path.join(os.path.dirname(__file__), "cnn_medical_images_classifier_final.pth")
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)
    return model, device



def cnn_inference(img, model, device):
    transform_infer = transforms.Compose([
    transforms.Resize((28, 28)),
    transforms.ToTensor(),
    ])
    img_tensor = transform_infer(img).unsqueeze(0).to(device)
    model.eval()
    with torch.no_grad():
        output = model(img_tensor)
        pred = torch.argmax(output, dim=1).item()
        return pred