import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from PIL import Image
import glob
import json
from sklearn.model_selection import train_test_split
from keras.preprocessing import image
from keras.preprocessing.image import load_img
from keras.preprocessing.image import img_to_array
from keras.preprocessing.image import save_img
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten
from keras.layers import Conv2D, MaxPooling2D
import re

def createFeaturesAndTargets(maximumNumberOfFashionProducts = 30):
    misMatchDimensions = []
    fashionProducts = []
    X = []
    Y = []
    count = 1
    jsonPath = "fashion-dataset/styles/"
    imagesPath = 'fashion-dataset/images/*.jpg'
    for filename in glob.glob(imagesPath):
        fashionProductId = filename.strip('fashion-dataset/images/').strip('.jpg')
        fashionProductImage = load_img(filename)
        fashionProductImageArray = img_to_array(fashionProductImage)
        fashionProductImageArray = tf.image.resize(fashionProductImageArray, [50, 50], method='bilinear', preserve_aspect_ratio=True, antialias=True, name=None)
        fashionProductImageArray = fashionProductImageArray / 255
        # print ('lol', fashionProductImageArray.shape)
        if (fashionProductImageArray.shape != (50, 38, 3)):
            misMatchDimensions.append(fashionProductId)
            count += 1
            continue
        # save_img(str(count)+'.jpg', fashionProductImageArray)
        f = open(jsonPath + fashionProductId + '.json',)
        fashionProductDetails = json.load(f)
        item = {}
        item["id"] = fashionProductId
        item["baseColor"] = fashionProductDetails["data"]["baseColour"]
        item["gender"] = fashionProductDetails["data"]["gender"]
        item["usage"] = fashionProductDetails["data"]["usage"]
        item["fashionImage"] = fashionProductImageArray
        if item["id"] and item["baseColor"] and item["gender"] and item["usage"] :
            fashionProducts.append([int(item["id"]), item["baseColor"], item["gender"], item["usage"]])
            X.append(item["fashionImage"])
        count += 1
        if count > maximumNumberOfFashionProducts:
            break
    X = np.array(X)
    df = pd.DataFrame.from_records(fashionProducts, columns=['id', 'baseColor', 'gender', 'usage'])
    df = pd.get_dummies(df, prefix=['baseColor', 'gender', 'usage'])
    Y = np.array(df.drop(['id'], axis=1))
    classes = np.array(list(df.columns.values)[1:])
    print ("\nTarget Headings")
    print (classes)
    print ("\nFeatures Shape")
    print (X.shape)
    print ("\nTarget Shape")
    print (Y.shape)
    print ("\n Items Excluded")
    print (misMatchDimensions)
    return X, Y, classes

def createCnnModel(numberOfTargetColumns):
    model = Sequential()
    model.add(Conv2D(filters=16, kernel_size=(5, 5), activation="relu", input_shape=(50,38,3)))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))
    model.add(Conv2D(filters=32, kernel_size=(5, 5), activation='relu', padding='same'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))
    model.add(Conv2D(filters=64, kernel_size=(5, 5), activation="relu", padding='same'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))
    model.add(Conv2D(filters=64, kernel_size=(5, 5), activation='relu', padding='same'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))
    model.add(Flatten())
    model.add(Dense(128, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(64, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(numberOfTargetColumns, activation='sigmoid'))
    model.summary()
    return model

def runCNN(model, X_train, X_test, y_train, y_test):
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    model.fit(X_train, y_train, epochs=100, validation_data=(X_test, y_test), batch_size=32)
    return model

maximumNumberOfFashionProducts = 3000
model_file_h5 = "model-weights/Model.h5"
save_classes = "model-classes/classes.npy"
X, Y, classes = createFeaturesAndTargets(maximumNumberOfFashionProducts)
X_train, X_test, y_train, y_test = train_test_split(X, Y, random_state=42, test_size=0.1)
numberOfTargetColumns = len(classes)
model = createCnnModel(numberOfTargetColumns)
model = runCNN(model, X_train, X_test, y_train, y_test)
model.save(model_file_h5)
np.save(save_classes, classes)
print("Saved model to disk")
# 3000 Epoch : 100 Batch Size : 32