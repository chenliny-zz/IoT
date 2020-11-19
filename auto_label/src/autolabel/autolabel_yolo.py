import glob, shutil
import os
import pickle
import xml.etree.ElementTree as ET
from os import listdir, getcwd
from os.path import join
import numpy as np
import sys

"""
Reads images from raw data directory and prepares Yolo structure.
"""

input_path = '../../data/raw/'
output = '../../data/processed/'

# Read in latest class label from latest_label.txt
txt_label_file_path = input_path + 'latest_label.txt'
with open(txt_label_file_path, 'r') as file:
    obj = file.read()

# Read in a list of bbox dimensions from raw images
txt_dim_file_path = input_path + obj + '/bbox.txt'
with open(txt_dim_file_path, 'r') as file:
    bbox = file.read().splitlines()

# Master inventory list
inventory_path = output + 'label_inventory.txt'

# Create yolo folder structure - images folder
train_img_output_path = output + 'train/images/'
validate_img_output_path = output + 'validate/images/'

img_dir = [train_img_output_path, validate_img_output_path]
for dir in img_dir:
    if not os.path.exists(dir):
        os.makedirs(dir)

# Check if class label exists in inventory already
# If exits, inform and exit
# If not, proceed with appending the class label
try:
    with open(inventory_path, 'r+') as file:
        temp_set = set(file.read().splitlines())
        if obj in temp_set:
            print("We had annotated this object already:)")
        # If class label does not exit in inventory list, append to list
        else:
            file.write(obj + '\n')

# If inventory list does not exist, create one and append class label
except:
    with open(inventory_path, 'a') as file:
        file.write(obj + '\n')

# Read in inventory list to classes
with open(inventory_path, 'r') as file:
    classes = file.read().splitlines()

# raw image outputs from camera; input for auto-labeling
rawImage_dir = '../../data/raw/{}/'.format(obj)

dirs = ['train', 'validate']

# Function to obtain a list of .jpg images in directory
def getImagesInDir(dir_path):
    """
    Function to obtain a list of .jpg files in a directory.
    Parameters:
        - dir_path: directory for the training images (from camera output)
    """
    image_list = []

    for filename in glob.glob(dir_path + '/*.jpg'):
        image_list.append(filename)
    return image_list

def datasetSplit(img_lst):
    """
    Function to split the image_list to training/validation sets.
    Parameters:
        - img_list: list of images
    """
    num = len(img_lst)

    idx = np.random.permutation(num)
    train_lst = np.array(img_lst)[idx[:int(num * .8)]]   # 80/20 split
    validation_lst = np.array(img_lst)[idx[:int(num * .2)]]
    return train_lst, validation_lst

def convert(size, box):
    """
    Function to generate YOLO bbox parameters.
    Parameters:
        - size: tuple containing width and height of raw image
        - box: tuple containing bounding box x, y, w, h
    """
    dw = 1./(size[0])   # 1 / image width
    dh = 1./(size[1])   # 1 / image height

    x, y, w, h = box[0], box[1], box[2], box[3]
    x = (x + w/2.0) * dw
    w = w*dw
    y = (y + h/2.0) * dh
    h = h*dh
    return (x,y,w,h)


def annotate(output_path, image_path, size, bbox):
    """
    Main function to create the annotation .txt files.
    parameters:
        - output_path: destination for annotated .txt files
        - image_path: directory to individual image
        - size: tuple containing width and height of raw image
        - bbox: a tuple (x, y, w, h) with bbox dimensions from raw image
    """
    basename = os.path.basename(image_path)  # extract file name only
    basename_no_ext = os.path.splitext(basename)[0]   # extract file name without extension

    out_file = open(output_path + basename_no_ext + '.txt', 'w')   # write .txt file with same file name
    bb = convert(size, bbox)   ############
    cls = obj
    cls_id = classes.index(cls)  # [TODO] This classes will be read in from .txt file at beginning
    out_file.write(str(cls_id) + " " + " ".join([str(a) for a in bb]) + '\n')

# Execution
image_paths = getImagesInDir(rawImage_dir)
train_paths, validation_paths = datasetSplit(image_paths)
image_sets = [train_paths, validation_paths]

for i, image_paths in enumerate(image_sets):

    # output path to be either {$PWD}/train or {$PWD}/validate
    full_dir_path = output + dirs[i]

    # output path in the labels folder
    output_path = full_dir_path + '/labels/'

    # create label directory if not exists
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # copy train/validation images to images folder
    for file in image_paths:
        shutil.copy(file, full_dir_path + '/images')

    # generate annotation files and save to labels folder
    for n, path in enumerate(image_paths):
        bbox_float = [float(dim) for dim in bbox[n].split()]
        annotate(output_path, path, (640, 480), bbox_float)


num_train = len(train_paths)
num_validate = len(validation_paths)
# print("Processed {} training and {} validation".format(num_train, num_validate))
print("Process completed")

"""
Orignal .xml specs for our camera frame for reference
<object>
	<name>iphone x</name>
	<pose>Unspecified</pose>
	<truncated>0</truncated>
	<difficult>0</difficult>
	<bndbox>
		<xmin>107</xmin>
		<ymin>106</ymin>
		<xmax>694</xmax>
		<ymax>493</ymax>
	</bndbox>
</object>
"""
