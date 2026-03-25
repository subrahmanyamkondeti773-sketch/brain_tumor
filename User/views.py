from django.shortcuts import render , redirect
from . import forms
from django.contrib import messages
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from .models import User_SigUp
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
import glob
import os
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix,  accuracy_score
import cv2
import random
import sys
import os

import torch.nn as nn
import torch.nn.functional as F
import seaborn as  sns

# Create your views here.
def SigUp(request):
    if  request.method=='POST':
        form = forms.User_SigupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request , 'Account Created Successfully')
            
        else:
            messages.error(request , 'Invalid Credentails')
    form = forms.User_SigupForm()

    return render(request , 'Register.html' , {'form':form})

def UserLogin(request):
    if request.method=='POST':
        username = request.POST.get('name')
        password = request.POST.get('password')
        try:
            data = User_SigUp.objects.get(Username=username , Password=password)
            if data.Status=='active':
                return redirect('UserHome')
            else:
             messages.error(request , 'You are not activated yet')
        except Exception as e:
            messages.error (request , 'Invalid data')
            return render(request , 'UserLogin.html')
    return render(request , 'UserLogin.html')


def UserHome(request):
    return render(request , 'Users/UserHome.html')




 
def Traning(request):
  
        tumor = []
        path = os.path.join(settings.MEDIA_ROOT , 'brain_tumor_dataset' , 'yes' , '*.jpg')
        for f in glob.glob(path):
            img = cv2.imread(f)
            img = cv2.resize(img,(128 , 128))
            b, g, r = cv2.split(img)
            cv2.merge([r, g, b])
            tumor.append(img)

        healthy = []
        path =os.path.join(settings.MEDIA_ROOT , 'brain_tumor_dataset' , 'no' , '*.jpg')
        for f in glob.glob(path):
            img = cv2.imread(f)
            img = cv2.resize(img,(128 , 128))
            b, g, r = cv2.split(img)
            cv2.merge([r, g, b])
            healthy.append(img)
        healthy = np.array(healthy)
        tumor = np.array(tumor)
        All= np.concatenate((tumor, healthy))
        plt.imshow(healthy[0])
        plt.axis('off')
        plt.show()
        plt.imshow(tumor[0])
        plt.axis('off')
        plt.show()
        def pot_random(healthy , tumor , num=5):
            healthy_images = healthy[np.random.choice(healthy.shape[0], num, replace=False)]
            tumor_images = tumor[np.random.choice(tumor.shape[0], num, replace=False)]
            plt.figure(figsize=(20, 8))
            for i in range(num):
                plt.subplot(1, num , i+1)
                plt.title('healthy')
                plt.imshow(healthy_images[i])
                plt.axis('off')
                
            plt.figure(figsize=(20, 8))
            for j in range(num):
                plt.subplot(1, num , j+1)
                plt.title('tumor')
                plt.imshow(tumor_images[j])
                plt.axis('off')
            plt.show()
        pot_random(healthy , tumor)
        class Dataset(object):
            def __getitem__(self, index):
                raise NotImplementedError

            def __len__(self): 
                raise NotImplementedError

            def __add__(self, other):
                raise NotImplementedError
        
        class MRI(Dataset):
            def __init__(self):
                
                tumor = []
                healthy = []
                path = os.path.join(settings.MEDIA_ROOT , 'brain_tumor_dataset' , 'yes' , '*.jpg')
                for f in glob.glob(path):
                    img = cv2.imread(f)
                    img = cv2.resize(img,(128 , 128))
                    b, g, r = cv2.split(img)
                    cv2.merge([r, g, b])
                    img = img.reshape(img.shape[2], img.shape[0], img.shape[1])
                    tumor.append(img)


                path = os.path.join(settings.MEDIA_ROOT , 'brain_tumor_dataset' , 'no' , '*.jpg')
                for f in glob.glob(path):
                    img = cv2.imread(f)
                    img = cv2.resize(img,(128 , 128))
                    b, g, r = cv2.split(img)
                    cv2.merge([r, g, b])
                    img = img.reshape(img.shape[2], img.shape[0], img.shape[1])
                    healthy.append(img)
        
                #out images


                tumor = np.array(tumor, dtype=np.float32)
                healthy = np.array(healthy, dtype=np.float32)

                #our labels
                tumor_labels = np.ones(tumor.shape[0], dtype=np.float32)
                healthy_labels = np.zeros(healthy.shape[0], dtype=np.float32)

            #concatenate
                self.images =np.concatenate((tumor, healthy) , axis=0)
                self.labels = np.concatenate((tumor_labels, healthy_labels) , axis=0)
                       
            def __len__(self):
                return self.images.shape[0]
            def __getitem__(self, index):
                sample = {'images': self.images[index], 'labels': self.labels[index]}
                return  sample
            def normalize(self):
                self.images = self.images / 255.0

        class CNN(nn.Module):
            def __init__(self):
                super(CNN, self).__init__()
                self.cnn_model = nn.Sequential (
                    nn.Conv2d(in_channels=3, out_channels=6, kernel_size=5),
                    nn.Tanh(),
                    nn.AvgPool2d(kernel_size=2, stride=5),
                    nn.Conv2d(in_channels=6, out_channels=16, kernel_size=5),
                    nn.Tanh(),
                    nn.AvgPool2d(kernel_size=2, stride=5),
                )
                self.fc_model = nn.Sequential (
                    nn.Linear(in_features=256, out_features=120),
                    nn.Tanh(),
                    nn.Linear(in_features=120, out_features=84),
                    nn.Tanh(),
                    nn.Linear(in_features=84, out_features=1),
                    
                )
            def forward(self, x):
                x = self.cnn_model(x)
                x = x.view(x.size(0), -1)
                x = self.fc_model(x)
                x = F.sigmoid(x)
                return x
        mri_dataset = MRI()
        mri_dataset.normalize()
        model = CNN()
        dataloader = DataLoader(mri_dataset , batch_size = 32 , shuffle = False)
        model.eval()
        outputs = []
        y_true = []
        with torch.no_grad():
            for D in dataloader:
                image = D['images']
                print(image[0].shape)
                label = D['labels']

                y_hat = model(image)
                outputs.append(y_hat.cpu().detach().numpy())
                y_true.append(label.cpu().detach().numpy())
        outputs = np.concatenate(outputs , axis=0).squeeze()
        y_true  = np.concatenate(y_true , axis=0).squeeze()
        def threshold(scores , threshold = 0.5 , minimum =0 , maximum = 1):
            x=np.array(list(scores))
            x[x>=threshold]= maximum    
            x[x<threshold]= minimum
            return x
        accuracy_score(y_true , threshold(outputs))
        plt.figure(figsize=(10,5))
        plt.plot(outputs)
        plt.axvline(x=len(tumor) , color='r' ,linestyle='dashed')
        plt.grid()
        plt.show()
        eta = 0.0001
        EPOCHS = 300
        optimizer = torch.optim.Adam(model.parameters() , lr = eta)
        dataloader = DataLoader(mri_dataset , batch_size = 32 , shuffle = True)
        model.train()
        for epoch in range(1 , EPOCHS):
            losses = []
            for D in dataloader:
                optimizer.zero_grad()
                data = D['images']
                label = D['labels']
                y_hat = model(data)
                #define losses function
                error = nn. BCELoss()
                loss= torch.sum(error(y_hat.squeeze() , label))   
                loss.backward()
                optimizer.step()
                losses.append(loss.item())
                print('Tain Epoch {} Loss {:.3f}'.format(epoch, np.mean(losses)))

        model.eval()
        dataloader = DataLoader(mri_dataset , batch_size = 32 , shuffle = False)
        outputs = []
        y_true = []
        with torch.no_grad():
            for D in dataloader:
                image = D['images']
                print(image[0].shape)
                label = D['labels']

                y_hat = model(image)
                outputs.append(y_hat.cpu().detach().numpy())
                y_true.append(label.cpu().detach().numpy())

        outputs = np.concatenate(outputs , axis=0).squeeze()
        y_true  = np.concatenate(y_true , axis=0).squeeze()
        acc= accuracy_score(y_true , threshold(outputs))
        
        plt.figure(figsize=(5,5))
        cm = confusion_matrix(y_true , threshold(outputs))
        ax=plt.subplot()
        sns.heatmap(cm , annot=True, fmt='g' , ax=ax , annot_kws={'size':20})

        ax.set_xlabel('Predicted labels', fontsize=20)
        ax.set_ylabel('True labels', fontsize=20)
        ax.set_title('Confusion Matrix' , fontsize=20)
        ax.xaxis.set_ticklabels(['healthy', 'tumor'], fontsize=15)
        ax.yaxis.set_ticklabels(['healthy', 'tumor'], fontsize=15)
        plt.show()
        plt.figure(figsize=(10,5))
        plt.plot(outputs)
        plt.axvline(x=len(tumor) , color='r' ,linestyle='dashed')
        plt.grid()
        plt.show()
        return render(request , 'Users/UserTraning.html' , {'acc':acc})






def predict(request):
    if request.method=='POST':
        img = request.FILES.get('img')
        fs = FileSystemStorage(location=settings.MEDIA_ROOT)
        filename = fs.save(img.name, img)  # Save the uploaded file with its original name
        uploaded_file_url = fs.url(filename)
        image_path = os.path.join(settings.MEDIA_ROOT , filename)
        class CNN(nn.Module):
            def __init__(self):
                super(CNN, self).__init__()
                self.cnn_model = nn.Sequential (
                    nn.Conv2d(in_channels=3, out_channels=6, kernel_size=5),
                    nn.Tanh(),
                    nn.AvgPool2d(kernel_size=2, stride=5),
                    nn.Conv2d(in_channels=6, out_channels=16, kernel_size=5),
                    nn.Tanh(),
                    nn.AvgPool2d(kernel_size=2, stride=5),
                )
                self.fc_model = nn.Sequential (
                    nn.Linear(in_features=256, out_features=120),
                    nn.Tanh(),
                    nn.Linear(in_features=120, out_features=84),
                    nn.Tanh(),
                    nn.Linear(in_features=84, out_features=1),
                    
                )
            def forward(self, x):
                x = self.cnn_model(x)
                x = x.view(x.size(0), -1)
                x = self.fc_model(x)
                x = F.sigmoid(x)
                return x

        model = CNN()
        model.load_state_dict(torch.load(os.path.join(settings.MEDIA_ROOT , 'weights' , 'model.pt')))
        model.eval()

        # Load and process the image
        # image_path = os.path.join(settings.MEDIA_ROOT , filename)
        image = cv2.imread(image_path)
        image_resized = cv2.resize(image, (128, 128))
        b, g, r = cv2.split(image_resized) 
        image_resized = cv2.merge([r, g, b])  # Convert BGR to RGB

        # Reshape to match input size and normalize
        image_input = image_resized.reshape(1, 3, 128, 128)
        image_input = torch.from_numpy(image_input).float() / 255.0

        # Define the thresholding function
        def threshold(scores, threshold=0.5, minimum=0, maximum=1):
            x = np.array(list(scores))
            x[x >= threshold] = maximum    
            x[x < threshold] = minimum
            return x

        # Make prediction
        with torch.no_grad():
            output = model(image_input)

        # Apply threshold
        prediction = threshold(output.cpu().numpy())

        # Show the image with the prediction result
        plt.imshow(image_resized)
        if prediction == 1:
            plt.title("Tumor detected")
        else:
            plt.title("No tumor detected")
        
        plt.axis('off')  # Hide axis
        plt.show()    
    return render(request , 'Users/UserPredict.html')
    



                    


    
            
