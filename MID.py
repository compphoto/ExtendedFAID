import os, glob, random
from PIL import Image
from skimage import img_as_float, color, img_as_ubyte
import numpy as np
import scipy.io as sio
from matplotlib import pyplot as plt
from skimage.color import xyz2rgb, xyz2lab, rgb2lab
import pathlib
import skimage
import sys
import argparse

dirname = os.path.dirname(__file__)
sys.path.append(os.path.join(dirname, '../'))
from utils.util import getAverageBrightness, changeBrightness, lin, gama_corect

""" arguments are given here as input"""
parser = argparse.ArgumentParser(description='parameters')
parser.add_argument('--dir_name', type=str, default='multi_illum')
parser.add_argument('--number_of_ambients', type=int, default=19)
parser.add_argument('--result_dir', type=str, default="MID")
args = parser.parse_args()

""" arguments are loaded into variables"""
dirName = args.dir_name
numberOfAmbient = args.number_of_ambients
resultDir = args.result_dir
normalizeAmbient = args.normalize_ambient

folders = os.listdir(dirName)

""" create result directory"""
if not os.path.exists(resultDir):
    os.makedirs(resultDir)
for i in range(1, numberOfAmbient + 1):
    resultDir_sub = resultDir + "/" + str(i)
    if not os.path.exists(resultDir_sub):
        os.makedirs(resultDir_sub)

ambient_names = ["dir_0_mip2", "dir_7_mip2", "dir_18_mip2", "dir_10_mip2", "dir_4_mip2", "dir_1_mip2", "dir_13_mip2",
                 "dir_15_mip2", "dir_23_mip2", "dir_6_mip2", \
                 "dir_5_mip2", "dir_8_mip2", "dir_9_mip2", "dir_11_mip2", "dir_12_mip2", "dir_14_mip2", "dir_16_mip2",
                 "dir_17_mip2", "dir_19_mip2"]

for folder in folders:
    f = os.path.join(dirName, folder)
    images = os.listdir(f)
    if len(images) > 10:
        for i, ambient_name in enumerate(ambient_names):
            flash_name = 'dir_22_mip2.jpg'
            if ambient_name == flash_name:
                continue
            ambient_name = ambient_name + '.jpg'

            """ load images """
            ambient = os.path.join(f, ambient_name)
            ambient = Image.open(ambient)
            ambient = skimage.img_as_float(ambient)

            flash = os.path.join(f, flash_name)
            flash = Image.open(flash)
            flash = skimage.img_as_float(flash)

            flash = lin(flash)
            ambient = lin(ambient)

            # white balance
            ambient_wb, flashPhoto_wb = whiteBalance(flash, ambient)

            flashPhoto_wb = Image.fromarray((flashPhoto_wb * 255).astype('uint8'))
            ambient_wb = Image.fromarray((ambient_wb * 255).astype('uint8'))
            flash = Image.fromarray((flash * 255).astype('uint8'))

            """ save images """
            result_dir = resultDir + "/" + str(i + 1)
            name_ambient = os.path.join(resultDir, image.replace(".png", "_ambient.png"))
            name_flash = os.path.join(resultDir, image.replace(".png", "_flash.png"))
            name_flashPhoto = os.path.join(resultDir, image.replace(".png", "_flashPhoto.png"))

            ambient_wb.save(name_ambient)
            flash.save(name_flash)
            flashPhoto_wb.save(name_flashPhoto)
