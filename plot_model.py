# -*- coding: utf-8 -*-
"""plot_the_model.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1rtQOi4ETFS72azNE91nyZQ2FCExKiZDm
"""

# Commented out IPython magic to ensure Python compatibility.

#Import necessary packages

from tensorflow.keras.layers import Dense, Flatten, Conv2D, MaxPooling2D,Dropout
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.losses import SparseCategoricalCrossentropy
from tensorflow.keras.preprocessing import image
from tensorflow.keras.optimizers import RMSprop
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam
import tensorflow_probability as tfp
from keras.utils import np_utils
import matplotlib.pyplot as plt
import tensorflow as tf
import numpy as np
#import splitfolders
import cv2
import os
tfd = tfp.distributions
tfpl = tfp.layers
# %matplotlib inline

# Pytorch packages

# Importing dataset
import os
import numpy as np

# Modifying dataset
from torchvision.transforms import transforms


# Modelling
from torchvision import datasets
import torchvision
import torch
import torchvision.models as models
import torch.nn as nn

#Visualization
from PIL import Image
import matplotlib.pyplot as plt

"""Function to plot the bayesian CNN model outcome:"""

def know_your_image(image, input_shape, model):

    #read image
    img = cv2.imread(image)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) 
    
    img_resize = (cv2.resize(img, dsize=input_shape, interpolation=cv2.INTER_AREA))/255.
    
    predict_proba = np.empty(shape=(500, 2))
    
    for i in range(500):
        
        predict_proba[i] = model(img_resize[np.newaxis,...]).mean().numpy()[0]

    fig,ax=plt.subplots(nrows=1, ncols=2,figsize=(8,4))

    #show the image
    ax[0].imshow(img)
    ax[0].axis('off')

    pred1 = [np.percentile(predict_proba[:, i], 2.5) for i in range(2)]
    pred2 = [np.percentile(predict_proba[:, i], 97.5) for i in range(2)]
    lower_percentile = np.array(pred1)
    upper_percentile = np.array(pred2)

    # As while labelling, the first category was 'fire' and the second category is 'no_fire'
    # Hence, the first probability value is of being fire and second is of being 'no_fire'

    # We will plot and check how much the model is 'confident' to predict accurately.

    data = {'Fire':(lower_percentile.item(0),upper_percentile.item(0)), 
            'No Fire': (lower_percentile.item(1),upper_percentile.item(1))}

    width = 0.5 # adjust to your liking

    my_color=['darkorange','navy']
    for i, values in enumerate(data.values()):

        ymin, ymax = values

        ax[1].axvspan(xmin=i-width/2, xmax=i+width/2, ymin=ymin,ymax=ymax, facecolor=my_color[i])
    


    # to illustrate that ranges are properly drawn
    ax[1].grid(True)

    #add ticks 
    ax[1].set_xticks(np.arange(0,len(data)))    
    ax[1].set_xticklabels(data.keys())
    _=plt.show()

"""Function to plot the Resnet50 model:"""

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

def predict_model(image, path):
  
  class_names = ['Fire', 'No_fire']
  model = torch.load(path)

  pred_trans = transforms.Compose([transforms.Resize(size=(224, 224)),
                                     transforms.ToTensor(), 
                                     transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])])

  image = pred_trans(image)[:3,:,:].unsqueeze(0)
  image = image.cuda()

  pred = model(image)
  idx = torch.argmax(pred)
  prob = round((pred[0][idx].item()*100), 5)
    
  return class_names[idx], prob

