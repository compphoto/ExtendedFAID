
images ='Illuminations';

pngFiles=dir(fullfile(images,'/*.png*'));
destinationFolder = 'Illuminations_XYZ';
if ~exist(destinationFolder, 'dir')
  mkdir(destinationFolder);
end



for i=1:numel(pngFiles)/2
    
    flash_name=pngFiles(2*i).name;
    ambient_name = pngFiles(2*i-1).name;
    
    flash=imread(fullfile(images,flash_name));
    ambient=imread(fullfile(images,ambient_name));
    
    rawFile = imfinfo(fullfile(images,flash_name));

    matrix =str2num(rawFile.Comment); 
    des = str2num(rawFile.Description);
    
    flash = getXYZ(flash, matrix);
    ambient = getXYZ(ambient, matrix);
    
    fullDestinationFileName = fullfile(destinationFolder, flash_name);
    combImg = imfuse(flash, ambient, 'montage');
    imwrite (combImg,fullDestinationFileName,'Comment',rawFile.Comment,'Description', rawFile.Description)
end

