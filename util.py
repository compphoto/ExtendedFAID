from PIL import Image
import numpy as np
from PIL.PngImagePlugin import PngImageFile, PngInfo


def getAverage(image):
    dropOut = int(np.floor(len(image) / 4))
    image = np.sort(image)
    image = np.delete(image, range(0, dropOut))
    image = np.delete(image, range((len(image) - dropOut), len(image)))
    avg_image = np.average(image)
    return avg_image


def alphaBlend(person, room, alpha):
    alpha = np.array(alpha)
    alpha = np.reshape(alpha, [512, 512, 1])
    alpha = np.tile(alpha, [1, 1, 3])
    alpha = alpha.astype(float) / 255

    person = np.array(person) / 255
    room = np.array(room) / 255

    foreground = person.astype(float)
    background = room.astype(float)
    foreground = cv2.multiply(alpha, foreground)
    background = cv2.multiply(1.0 - alpha, background)
    outImage = cv2.add(foreground, background)
    return outImage


def whiteBalance(flash_lin, ambient_lin):
    flash_gray = color.rgb2gray(flash_lin)
    flash_normalize_gray = flash_lin.copy()
    flash_normalize_gray[:, :, 1] = flash_lin[:, :, 1].copy() / (flash_gray + 0.0001)
    flash_normalize_gray[:, :, 0] = flash_lin[:, :, 0].copy() / (flash_gray + 0.0001)
    flash_normalize_gray[:, :, 2] = flash_lin[:, :, 2].copy() / (flash_gray + 0.0001)

    ambient_lin_normalize_gray = ambient_lin.copy()
    ambient_gray = color.rgb2gray(ambient_lin_normalize_gray)
    ambient_lin_normalize_gray[:, :, 1] = ambient_lin[:, :, 1].copy() / (ambient_gray + 0.0001)
    ambient_lin_normalize_gray[:, :, 0] = ambient_lin[:, :, 0].copy() / (ambient_gray + 0.0001)
    ambient_lin_normalize_gray[:, :, 2] = ambient_lin[:, :, 2].copy() / (ambient_gray + 0.0001)

    # ratio of flash/ ambient portrait brightness
    ratio = flash_normalize_gray[:, :, 0:3] / (ambient_lin_normalize_gray[:, :, 0:3] + 0.0001)
    # normalize ratio
    ratio[:, :, 2] = ratio[:, :, 2] / (ratio[:, :, 1] + 0.0001)
    ratio[:, :, 0] = ratio[:, :, 0] / (ratio[:, :, 1] + 0.0001)
    ratio[:, :, 1] = ratio[:, :, 1] / (ratio[:, :, 1] + 0.0001)

    ratio_red = np.reshape(ratio[:, :, 0], (ratio.shape[0] * ratio.shape[1]))
    ratio_red = ratio_red[ratio_red != 0]
    median_red = np.median(ratio_red)

    ratio_blue = np.reshape(ratio[:, :, 2], (ratio.shape[0] * ratio.shape[1]))
    ratio_blue = ratio_blue[ratio_blue != 0]
    median_blue = np.median(ratio_blue)

    # white balance ambient
    ambient_lin[:, :, 0] = ambient_lin[:, :, 0] * median_red
    ambient_lin[:, :, 1] = ambient_lin[:, :, 1]
    ambient_lin[:, :, 2] = ambient_lin[:, :, 2] * median_blue
    ambient_lin[ambient_lin < 0] = 0
    ambient_lin[ambient_lin > 1] = 1

    flashphoto_whitebalanced = flash_lin + ambient_lin
    flashphoto_whitebalanced[flashphoto_whitebalanced < 0] = 0
    flashphoto_whitebalanced[flashphoto_whitebalanced > 1] = 1

    return flashphoto_whitebalanced, ambient_lin


def xyztorgb(image, des):
    illum = chromaticityAdaptation(des)
    mat = [[3.2404542, -0.9692660, 0.0556434], [-1.5371385, 1.8760108, -0.2040259],
           [-0.4985314, 0.0415560, 1.0572252]]
    image = np.matmul(image, illum)
    image = np.matmul(image, mat)
    image = np.where(image < 0, 0, image)
    image = np.where(image > 1, 1, image)

    return image


def chromaticityAdaptation(calibrationIlluminant):
    if calibrationIlluminant == 17:
        illum = [[0.8652435, 0.0000000, 0.0000000],
                 [0.0000000, 1.0000000, 0.0000000],
                 [0.0000000, 0.0000000, 3.0598005]]
    elif calibrationIlluminant == 19:
        illum = [[0.9691356, 0.0000000, 0.0000000],
                 [0.0000000, 1.0000000, 0.0000000],
                 [0.0000000, 0.0000000, 0.9209267]]
    elif calibrationIlluminant == 20:
        illum = [[0.9933634, 0.0000000, 0.0000000],
                 [0.0000000, 1.0000000, 0.0000000],
                 [0.0000000, 0.0000000, 1.1815972]]
    elif calibrationIlluminant == 21:
        illum = [[1, 0, 0],
                 [0, 1, 0],
                 [0, 0, 1]]
    elif calibrationIlluminant == 23:
        illum = [[1.0077340, 0.0000000, 0.0000000],
                 [0.0000000, 1.0000000, 0.0000000],
                 [0.0000000, 0.0000000, 0.8955170]]
    return illum


def getRatio(t, low, high):
    dist = t - low
    range = (high - low) / 100
    return dist / range


def changeTemp(image, tempChange):

    t1 = 4500
    if tempChange == 48:
        tempChange = 700
    if tempChange == 44:
        tempChange = 400
    elif tempChange == 40:
        tempChange = 250
    elif tempChange == 52:
        tempChange = 800
    elif tempChange == 54:
        tempChange = 1000
    t = tempChange + t1

    if 4500 <= t <= 7500:
        r = getRatio(t, 4500, 7500)
        xD = 0.17
        yD = 0.17
        xS = 0.4231
        yS = 0.3304
        r_x = (xD - xS) / 100
        xD = xS + r * r_x
        r_y = (yD - yS) / 100
        yD = yS + r * r_y

    elif 4500 > t >= 4000:
        r = getRatio(t, 4500, 4000)
        xD = 0.4949
        yD = 0.3564
        xS = 0.4231
        yS = 0.3304
        r_x = (xD - xS) / 100
        xD = xS + r * r_x
        r_y = (yD - yS) / 100
        yD = yS + r * r_y

    elif 3500 <= t < 4000:
        r = getRatio(t, 4000, 3500)
        xD = 0.5141
        yD = 0.3434
        xS = 0.4949
        yS = 0.3564
        r_x = (xD - xS) / 100
        xD = xS + r * r_x
        r_y = (yD - yS) / 100
        yD = yS + r * r_y
    elif 0 < t < 3500:
        r = getRatio(t, 3500, 0)
        xD = 0.5189
        yD = 0.3063
        xS = 0.5141
        yS = 0.3434
        r_x = (xD - xS) / 100
        xD = xS + r * r_x
        r_y = (yD - yS) / 100
        yD = yS + r * r_y

    chromaticity_x = 0.4231
    chromaticity_y = 0.3304

    offset_x = xD / chromaticity_x
    offset_y = yD / chromaticity_y

    out = image
    h, w, c = image.shape
    img0 = image[:, :, 0]
    img1 = image[:, :, 1]
    img2 = image[:, :, 2]
    sumImage = img0 + img1 + img2
    x_pix = np.zeros((h, w))
    y_pix = np.zeros((h, w))

    nonZeroSum = np.where(sumImage != 0)
    x_pix[nonZeroSum] = img0[nonZeroSum] / sumImage[nonZeroSum]
    y_pix[nonZeroSum] = img1[nonZeroSum] / sumImage[nonZeroSum]

    x_pix = x_pix * offset_x
    y_pix = y_pix * offset_y

    out0 = np.zeros((h, w))
    out2 = np.zeros((h, w))

    nonZeroY = np.where(y_pix != 0)
    ones = np.ones((h, w))
    out0[nonZeroY] = x_pix[nonZeroY] * img1[nonZeroY] / y_pix[nonZeroY]
    out2[nonZeroY] = (ones[nonZeroY] - x_pix[nonZeroY] - y_pix[nonZeroY]) * img1[nonZeroY] / y_pix[nonZeroY]
    out[:, :, 0] = out0
    out[:, :, 2] = out2

    return out


def lin(srgb):
    srgb = srgb.astype(np.float)
    rgb = np.zeros_like(srgb).astype(np.float)
    srgb = srgb
    mask1 = srgb <= 0.04045
    mask2 = (1 - mask1).astype(bool)
    rgb[mask1] = srgb[mask1] / 12.92
    rgb[mask2] = ((srgb[mask2] + 0.055) / 1.055) ** 2.4
    rgb = rgb
    return rgb


def divideImagePair(image_pair):
    w, h = image_pair.size
    w2 = int(w / 2)
    A = image_pair.crop((0, 0, w2, h))
    B = image_pair.crop((w2, 0, w, h))
    return A, B


