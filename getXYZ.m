function image = getXYZ(image, matrix)
    image = im2double(image);

    XYZtoCamera = reshape(matrix, [3 3])';
    imf = reshape(image, [size(image, 1) * size(image, 2), 3])';
    CameraToXYZ = inv(XYZtoCamera);
    imf = CameraToXYZ * imf;
    image = reshape(imf', [size(image, 1), size(image, 2), 3]);



end