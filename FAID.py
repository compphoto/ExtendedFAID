import os
from PIL import Image
import numpy as np
from PIL.PngImagePlugin import PngImageFile, PngInfo
from util import whiteBalance, changeTemp, xyztorgb, divideImagePair

dir = 'Illuminations_XYZ'
images = os.listdir(dir)
resultDir = 'FAID'

for index, image in enumerate(images):
    image_path = os.path.join(dir, image)
    image_pair = Image.open(image_path)
    hyper_des = int(PngImageFile(image_path).text['des'])

    A, B = divideImagePair(image_pair)
    ambient = skimage.img_as_float(A)
    flash = skimage.img_as_float(B)

    if hyper_des == 21:
        flash = changeTemp(flash, 48)
        ambient = changeTemp(ambient, 48)

    ambient = xyztorgb(ambient, hyper_des)
    flash = xyztorgb(flash, hyper_des)

    # white balance
    ambient_wb, flashPhoto_wb = whiteBalance(flash, ambient)

    flashPhoto_wb = Image.fromarray((flashPhoto_wb * 255).astype('uint8'))
    ambient_wb = Image.fromarray((ambient_wb * 255).astype('uint8'))
    flash = Image.fromarray((flash * 255).astype('uint8'))

    name_ambient = os.path.join(resultDir, image.replace(".png", "_ambient.png"))
    name_flash = os.path.join(resultDir, image.replace(".png", "_flash.png"))
    name_flashPhoto = os.path.join(resultDir, image.replace(".png", "_flashPhoto.png"))

    ambient_wb.save(name_ambient)
    flash.save(name_flash)
    flashPhoto_wb.save(name_flashPhoto)

