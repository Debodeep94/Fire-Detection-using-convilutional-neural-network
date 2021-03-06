# -*- coding: utf-8 -*-
"""untuned_model.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1rX_cLf_AO7Gm1rcZ_dUMSxwt0xcvoUO2
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

def loader_image(train_parent_directory, test_parent_directory, input_shape):
    """
    The function takes train set directory and validation set directory as inputs
    Image data generator is used to label the images
    The function will return labeled train and validation data set
    """
    
    train_datagen = ImageDataGenerator(rescale=1./255,
                                        shear_range=0.2,
                                        zoom_range=0.2,
                                        horizontal_flip=True
                                       )
    validation_datagen = ImageDataGenerator(rescale=1./255)
    
    train_dataset = train_datagen.flow_from_directory(train_parent_directory,
                                  target_size = input_shape,
                                  batch_size = 50,
                                  class_mode = 'categorical')
 
    
    validation_dataset = validation_datagen.flow_from_directory(test_parent_directory,
                                 target_size=input_shape,
                                 batch_size = 30,
                                 class_mode = 'categorical')    
    
    return train_dataset, validation_dataset

# number of files belonging to the train set

def number_train_images(path):

  list_1 = os.listdir(path +'/fire_images') # dir is your directory path
  list_2 = os.listdir(path +"/non_fire_images") # dir is your directory path

  number_files = len(list_1)+len(list_2)
  return number_files

def nll(y_true, y_pred):
    """
    This function should return the negative log-likelihood of each sample
    in y_true given the predicted distribution y_pred. If y_true is of shape 
    [B, E] and y_pred has batch shape [B] and event_shape [E], the output 
    should be a Tensor of shape [B].
    """
    return -y_pred.log_prob(y_true)

def bayesian_convolutional_model(input_shape, loss, optimizer, metrics,path_to_train_folder):
    """
    The function helps to construct the bayesian CNN model
    The funcion takes input_shape, loss, optimizer, metrics and the train directory as input
    The train directory is needed to calculate the number of files inside the train folder
    which in turn is essential to compute the KL_divergence
    """
    
    # Define the KL divergence function:
    number_files=number_train_images(path_to_train_folder) 
    kl_divergence_fn = lambda q,p,_:tfd.kl_divergence(q,p)/number_files

    # Define the model:

    bcnn_model = Sequential([
                            # Convolutional reparameterization layers
                            tfpl.Convolution2DReparameterization(
                                      input_shape=input_shape, filters=8, 
                                      kernel_size=16, activation='relu', padding='SAME',
                                      #Kernel details
                                      kernel_prior_fn = tfpl.default_multivariate_normal_fn,
                                      kernel_posterior_fn=tfpl.default_mean_field_normal_fn(is_singular=False),
                                      kernel_divergence_fn = kl_divergence_fn,
                                      #Bias details
                                      bias_prior_fn = tfpl.default_multivariate_normal_fn,
                                      bias_posterior_fn=tfpl.default_mean_field_normal_fn(is_singular=False),
                                      bias_posterior_tensor_fn=(lambda d: d.sample()),
                                      bias_divergence_fn = kl_divergence_fn),
                              # Additional layers
                            MaxPooling2D(2,2),
                            Conv2D(32, 4, activation='relu'),
                            Dropout(0.2),
                            MaxPooling2D(2,2),
                            Conv2D(64, 4, activation='relu'),
                            Dropout(0.15),
                            MaxPooling2D(2,2),
                            Conv2D(64, 4, activation='relu'),
                            Dropout(0.35),
                            MaxPooling2D(2,2),
                            Flatten(),
                            Dense(416, activation='relu'),
                            # Dense reparameterizational layers
                            tfpl.DenseReparameterization(
                                      units=tfpl.OneHotCategorical.params_size(2), activation=None,
                                      #Kernel details
                                      kernel_prior_fn = tfpl.default_multivariate_normal_fn,
                                      kernel_posterior_fn=tfpl.default_mean_field_normal_fn(is_singular=False),
                                      kernel_posterior_tensor_fn=(lambda d: d.sample()),
                                      kernel_divergence_fn = kl_divergence_fn,
                                      #Bias details
                                      bias_prior_fn = tfpl.default_multivariate_normal_fn,
                                      bias_posterior_fn=tfpl.default_mean_field_normal_fn(is_singular=False),
                                      bias_posterior_tensor_fn=(lambda d: d.sample()),
                                      bias_divergence_fn = kl_divergence_fn
                                    ),
        tfpl.OneHotCategorical(2,convert_to_tensor_fn=tfd.Distribution.mode)
        
    ])
    bcnn_model.compile(loss=loss, optimizer=optimizer, metrics=metrics)
    return bcnn_model



