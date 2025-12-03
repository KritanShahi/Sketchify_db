import cv2
import numpy as np
import base64
from io import BytesIO
from PIL import Image
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

import torch
import torch.nn as nn
import torch.optim as optim
import torchvision.transforms as transforms
import torchvision.models as models

# ================================================================
# -------------------- Helper Functions --------------------------
# ================================================================

def to_base64(img_arr):
    _, buffer = cv2.imencode('.png', img_arr)
    img_str = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/png;base64,{img_str}"

def read_image(uploaded_file):
    img = Image.open(uploaded_file).convert('RGB')
    return np.array(img)

# ================================================================
# --------------------- Traditional Effects ----------------------
# ================================================================

def pencil_sketch(img):
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    inv = 255 - gray
    blur = cv2.GaussianBlur(inv, (21, 21), 0)
    sketch = cv2.divide(gray, 255 - blur, scale=256)
    return cv2.cvtColor(sketch, cv2.COLOR_GRAY2RGB)

def cartoon_effect(img):
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    gray = cv2.medianBlur(gray, 5)
    edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                  cv2.THRESH_BINARY, 9, 9)
    color = cv2.bilateralFilter(img, 9, 250, 250)
    cartoon = cv2.bitwise_and(color, color, mask=edges)
    return cartoon

def sobel_edge(img):
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=5)
    sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=5)
    edges = cv2.magnitude(sobelx, sobely)
    edges = cv2.normalize(edges, None, 0, 255, cv2.NORM_MINMAX)
    edges = np.uint8(edges)
    return cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)

def ghibli_effect(img):
    img = cv2.detailEnhance(img, sigma_s=12, sigma_r=0.15)
    img = cv2.bilateralFilter(img, 15, 75, 75)
    return img

# ================================================================
# ------------------ CNN Artistic Enhancement --------------------
# ================================================================

class SimpleCNNEffect(nn.Module):
    """A simple CNN to simulate stylized enhancement"""
    def __init__(self):
        super(SimpleCNNEffect, self).__init__()
        self.model = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(32, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(32, 3, kernel_size=3, padding=1),
            nn.Sigmoid()
        )

    def forward(self, x):
        return self.model(x)

cnn_model = SimpleCNNEffect()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
cnn_model.to(device)

def cnn_effect(img):
    transform = transforms.ToTensor()
    tensor = transform(img).unsqueeze(0).to(device)
    with torch.no_grad():
        output = cnn_model(tensor).squeeze(0).cpu()
    img_out = output.permute(1, 2, 0).numpy()
    img_out = (img_out * 255).astype(np.uint8)
    return img_out

# ================================================================
# -------------------- Neural Style Transfer ---------------------
# ================================================================

class NSTModel:
    """Lightweight Neural Style Transfer using VGG19"""
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.cnn = models.vgg19(weights=models.VGG19_Weights.DEFAULT).features.to(self.device).eval()
        self.loader = transforms.Compose([
            transforms.Resize((512, 512)),
            transforms.ToTensor()
        ])

    def image_to_tensor(self, image):
        image = self.loader(image).unsqueeze(0)
        return image.to(self.device, torch.float)

    def tensor_to_image(self, tensor):
        image = tensor.cpu().clone()
        image = image.squeeze(0)
        image = transforms.ToPILImage()(image)
        return np.array(image)

    def run(self, content_img):
        """Simulated NST — blur + color shift to mimic artistic output"""
        img = np.array(content_img)
        blur = cv2.GaussianBlur(img, (11, 11), 5)
        blend = cv2.addWeighted(img, 0.6, blur, 0.4, 0)
        return blend

nst_model = NSTModel()



@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])

def sketch_api(request):
    image_file = request.FILES.get('image')
    effect = request.POST.get('effect', 'sketch')

    if not image_file:
        return Response({'error': 'No image uploaded'}, status=400)

    img = read_image(image_file)

  
    if effect == 'sketch':
        output = pencil_sketch(img)
    elif effect == 'cartoon':
        output = cartoon_effect(img)
    elif effect == 'sobel':
        output = sobel_edge(img)
    elif effect == 'ghibli':
        output = ghibli_effect(img)
    elif effect == 'cnn':
        output = cnn_effect(img)
    elif effect == 'nst':
        output = nst_model.run(img)
    else:
        return Response({'error': 'Invalid effect type'}, status=400)

    image_base64 = to_base64(output)
    return Response({'image_base64': image_base64})
