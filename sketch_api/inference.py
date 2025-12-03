from PIL import Image, ImageFilter, ImageOps
import numpy as np


def image_to_sketch(img):
    gray = img.convert('L')
    inverted = ImageOps.invert(gray)
    blur = inverted.filter(ImageFilter.GaussianBlur(10))
    gray_np = np.array(gray).astype('float')
    blur_np = np.array(blur).astype('float')
    denom = 255 - blur_np
    denom[denom == 0] = 1
    sketch = np.minimum(255, (gray_np * 255) / denom)
    return Image.fromarray(sketch.astype('uint8'))