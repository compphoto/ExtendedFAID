import os
from PIL import Image
import numpy as np
import cv2
import skimage
from PIL.PngImagePlugin import PngImageFile, PngInfo
from skimage import color
import argparse
from util import whiteBalance, changeTemp, xyztorgb, getAverage, alphaBlend

""" arguments loaded here"""
parser = argparse.ArgumentParser(description='parameters')
parser.add_argument('--room_dir', type=str, default='Rooms')
parser.add_argument('--portrait_flash_dir', type=str, default='train_inputs_origin')
parser.add_argument('--portrait_noflash_dir', type=str, default='train_target')
parser.add_argument('--alpha_dir', type=str, default='alpha_values')

parser.add_argument('--random_bg', type=int, default=5)
parser.add_argument('--result_dir', type=str, default="portraits")

args = parser.parse_args()

roomDir = args.room_dir
portrait_flash_dir = args.portrait_flash_dir
portrait_noflash_dir = args.portrait_noflash_dir
alpha_dir = args.alpha_dir
randomBG = args.random_bg

flash_color_adjustment_ratio = [0.2, 0.2, 0.25]

roomImages = os.listdir(roomDir)
peopleImages = os.listdir(portrait_flash_dir)

resultDir_portrait = args.result_dir

if not os.path.exists(resultDir_portrait):
    os.makedirs(resultDir_portrait)

for i in range(1, randomBG):
    resultDir_portrait_sub = resultDir_portrait + "/" + str(i)
    if not os.path.exists(resultDir_portrait_sub):
        os.makedirs(resultDir_portrait_sub)

for index, peopleImage in enumerate(peopleImages):

    ### choose random room images as the background for each portrait
    index_rooms = np.random.randint(len(roomImages) - 1, size=randomBG)

    for i, index_room in enumerate(index_rooms):
        room_image = roomImages[index_room]
        path_room = os.path.join(roomDir, room_image)
        room = Image.open(path_room)
        targetImage = PngImageFile(path_room)
        des = int(targetImage.text['des'])
        w, h = room.size
        w2 = int(w / 2)
        A = room.crop((0, 0, w2, h))
        B = room.crop((w2, 0, w, h))
        width, height = A.size  # Get dimensions

        new_width = newSize
        new_height = newSize
        left = (width - new_width) / 2
        top = (height - new_height) / 2
        right = (width + new_width) / 2
        bottom = (height + new_height) / 2

        # Crop the center of the image
        A = A.crop((left, top, right, bottom))
        B = B.crop((left, top, right, bottom))

        flash_room = skimage.img_as_float(A)
        ambient_room = skimage.img_as_float(B)

        flash_avg_room = getAverage(flash_room[:, :, 0]) + getAverage(flash_room[:, :, 1]) + getAverage(
            flash_room[:, :, 2])
        ambient_avg_room = getAverage(ambient_room[:, :, 0]) + getAverage(ambient_room[:, :, 1]) + getAverage(
            ambient_room[:, :, 2])
        flash_room = flash_room * 2 * ambient_avg_room / flash_avg_room

        # calculate average brightness of background
        ambient_avg_room = getAverage(ambient_room[:, :, 0]) + getAverage(ambient_room[:, :, 1]) + getAverage(
            ambient_room[:, :, 2])
        flash_avg_room = getAverage(flash_room[:, :, 0]) + getAverage(flash_room[:, :, 1]) + getAverage(
            flash_room[:, :, 2])

        if des == 21:
            flash_room = changeTemp(flash_room, 48)
            ambient_room = changeTemp(ambient_room, 48)

        flash_room = xyztorgb(flash_room, des)
        ambient_room = xyztorgb(ambient_room, des)

        path_people_flash = os.path.join(portrait_flash_dir, peopleImage)
        path_people_no_flash = os.path.join(portrait_noflash_dir, peopleImage.replace("flash", "no_flash"))
        alpha = os.path.join(alphaDir, path_people_flash.replace(".png", ".csv"))

        flash_por = Image.open(path_people_flash)
        ambient_por = Image.open(path_people_no_flash)
        alpha = list(csv.reader(open(path_alpha)))

        # adjust flash portrait with respect to the flash background (same for all of the flash images)
        flash_color_adjustment_ratio = flash_color_adjustment_ratio / np.max(flash_color_adjustment_ratio)
        flash_por = lin(skimage.img_as_float(flash_por))
        flash_por[:, :, 0] = flash_por[:, :, 0] * flash_color_adjustment_ratio[0]
        flash_por[:, :, 1] = flash_por[:, :, 1] * flash_color_adjustment_ratio[1]
        flash_por[:, :, 2] = flash_por[:, :, 2] * flash_color_adjustment_ratio[2]

        ambient_por_lin = ambient_por.copy()
        ambient_por_lin = lin(skimage.img_as_float(ambient_por_lin))

        flash_room_lin = lin(skimage.img_as_float(flash_room.copy()))
        ambient_room_lin = lin(skimage.img_as_float(ambient_room.copy()))

        # normalize flash and ambient with respect to brightness
        flash_por_gray = color.rgb2gray(flash_por)
        flash_por_normalize_gray = flash_por.copy()
        flash_por_normalize_gray[:, :, 1] = flash_por[:, :, 1].copy() / (flash_por_gray + 0.0001)
        flash_por_normalize_gray[:, :, 0] = flash_por[:, :, 0].copy() / (flash_por_gray + 0.0001)
        flash_por_normalize_gray[:, :, 2] = flash_por[:, :, 2].copy() / (flash_por_gray + 0.0001)

        ambient_por_lin_normalize_gray = ambient_por_lin.copy()
        ambient_por_gray = color.rgb2gray(ambient_por_lin_normalize_gray)
        ambient_por_lin_normalize_gray[:, :, 1] = ambient_por_lin[:, :, 1].copy() / (ambient_por_gray + 0.0001)
        ambient_por_lin_normalize_gray[:, :, 0] = ambient_por_lin[:, :, 0].copy() / (ambient_por_gray + 0.0001)
        ambient_por_lin_normalize_gray[:, :, 2] = ambient_por_lin[:, :, 2].copy() / (ambient_por_gray + 0.0001)

        # ratio of flash/ ambient portrait brightness
        ratio = flash_por_normalize_gray[:, :, 0:3] / (ambient_por_lin_normalize_gray[:, :, 0:3] + 0.0001)

        mask = np.where(flash_por[:, :, 3] == 1, 1, 0)

        ratio_masked = np.zeros((512, 512, 3))
        ratio_masked[:, :, 0] = ratio[:, :, 0] * mask
        ratio_masked[:, :, 1] = ratio[:, :, 1] * mask
        ratio_masked[:, :, 2] = ratio[:, :, 2] * mask

        ratio_masked[:, :, 2] = ratio_masked[:, :, 2] / (ratio_masked[:, :, 1] + 0.0001)
        ratio_masked[:, :, 0] = ratio_masked[:, :, 0] / (ratio_masked[:, :, 1] + 0.0001)
        ratio_masked[:, :, 1] = ratio_masked[:, :, 1] / (ratio_masked[:, :, 1] + 0.0001)

        ratio_red = np.reshape(ratio_masked[:, :, 0], (512 * 512))
        ratio_red = ratio_red[ratio_red != 0]
        median_red = np.median(ratio_red)

        ratio_blue = np.reshape(ratio_masked[:, :, 2], (512 * 512))
        ratio_blue = ratio_blue[ratio_blue != 0]
        median_blue = np.median(ratio_blue)

        avg_ambient_red_bg = getAverage(ambient_room_lin[:, :, 0])
        avg_ambient_green_bg = getAverage(ambient_room_lin[:, :, 1])
        avg_ambient_blue_bg = getAverage(ambient_room_lin[:, :, 2])

        avg_flash_red_bg = getAverage(flash_room_lin[:, :, 0])
        avg_flash_green_bg = getAverage(flash_room_lin[:, :, 1])
        avg_flash_blue_bg = getAverage(flash_room_lin[:, :, 2])

        bg_ratio_red = avg_ambient_red_bg / (avg_flash_red_bg + 0.0001)
        bg_ratio_green = avg_ambient_green_bg / (avg_flash_green_bg + 0.0001)
        bg_ratio_blue = avg_ambient_blue_bg / (avg_flash_blue_bg + 0.0001)

        ambient_por_lin[:, :, 0] = ambient_por_lin[:, :, 0] * bg_ratio_red * median_red
        ambient_por_lin[:, :, 1] = ambient_por_lin[:, :, 1] * bg_ratio_green
        ambient_por_lin[:, :, 2] = ambient_por_lin[:, :, 2] * bg_ratio_blue * median_blue

        ambient_por_adjust = gama_corect(ambient_por_lin)
        ambient_por_adjust = Image.fromarray((ambient_por_adjust * 255).astype('uint8'))

        flash_por = gama_corect(flash_por)
        flash_por = Image.fromarray((flash_por * 255).astype('uint8'))

        flash_out = alpha_blend(flash_por, flash_room, alpha)
        ambient_out_adjust = alpha_blend(ambient_por_adjust, ambient_room, alpha)

        #Gamma Correct
        ambient_wb, flashPhoto_wb = whiteBalance(flash_out, ambient_out_adjust)

        flashPhoto_wb = Image.fromarray((flashPhoto_wb * 255).astype('uint8'))
        ambient_wb = Image.fromarray((ambient_wb * 255).astype('uint8'))
        flash = Image.fromarray((flash_out * 255).astype('uint8'))

        resultDir = resultDir_portrait + "/" + str(i + 1)

        name_ambient = os.path.join(resultDir, image.replace(".png", "_ambient.png"))
        name_flash = os.path.join(resultDir, image.replace(".png", "_flash.png"))
        name_flashPhoto = os.path.join(resultDir, image.replace(".png", "_flashPhoto.png"))

        ambient_wb.save(name_ambient)
        flash.save(name_flash)
        flashPhoto_wb.save(name_flashPhoto)
