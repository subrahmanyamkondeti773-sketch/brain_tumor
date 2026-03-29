from django.shortcuts import render, redirect
from . import forms
from django.contrib import messages
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from .models import User_SigUp

import os
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import cv2

# ---------------- USER AUTH ---------------- #

def SigUp(request):
    if request.method == 'POST':
        form = forms.User_SigupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account Created Successfully')
        else:
            messages.error(request, 'Invalid Credentials')
    else:
        form = forms.User_SigupForm()

    return render(request, 'Register.html', {'form': form})


def UserLogin(request):
    if request.method == 'POST':
        username = request.POST.get('name')
        password = request.POST.get('password')
        try:
            data = User_SigUp.objects.get(Username=username, Password=password)
            if data.Status == 'active':
                return redirect('UserHome')
            else:
                messages.error(request, 'You are not activated yet')
        except:
            messages.error(request, 'Invalid data')

    return render(request, 'UserLogin.html')


def UserHome(request):
    return render(request, 'Users/UserHome.html')


# ---------------- MODEL DEFINITION ---------------- #

class CNN(nn.Module):
    def __init__(self):
        super(CNN, self).__init__()
        self.cnn_model = nn.Sequential(
            nn.Conv2d(3, 6, 5),
            nn.Tanh(),
            nn.AvgPool2d(2, stride=5),

            nn.Conv2d(6, 16, 5),
            nn.Tanh(),
            nn.AvgPool2d(2, stride=5),
        )

        self.fc_model = nn.Sequential(
            nn.Linear(256, 120),
            nn.Tanh(),

            nn.Linear(120, 84),
            nn.Tanh(),

            nn.Linear(84, 1),
        )

    def forward(self, x):
        x = self.cnn_model(x)
        x = x.view(x.size(0), -1)
        x = self.fc_model(x)
        return torch.sigmoid(x)


# ---------------- LOAD MODEL ONCE (IMPORTANT) ---------------- #

MODEL_PATH = os.path.join(settings.MEDIA_ROOT, 'weights', 'model.pt')

model = CNN()

try:
    model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device('cpu')))
    model.eval()
    print("✅ Model loaded successfully")
except Exception as e:
    print("❌ Model loading failed:", e)


# ---------------- PREDICTION ---------------- #

def predict(request):
    if request.method == 'POST':
        img = request.FILES.get('img')

        if not img:
            messages.error(request, "No image uploaded")
            return render(request, 'Users/UserPredict.html')

        # Save image
        fs = FileSystemStorage(location=settings.MEDIA_ROOT)
        filename = fs.save(img.name, img)
        image_path = os.path.join(settings.MEDIA_ROOT, filename)

        # Read image
        image = cv2.imread(image_path)
        if image is None:
            messages.error(request, "Invalid image file")
            return render(request, 'Users/UserPredict.html')

        # Resize
        image = cv2.resize(image, (128, 128))

        # Convert BGR → RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Normalize + reshape
        image = image.reshape(1, 3, 128, 128)
        image = torch.from_numpy(image).float() / 255.0

        # Prediction
        with torch.no_grad():
            output = model(image)

        prediction = (output >= 0.5).int().item()

        if prediction == 1:
            result = "Tumor Detected"
        else:
            result = "No Tumor Detected"

        return render(request, 'Users/UserPredict.html', {
            'result': result,
            'image_url': fs.url(filename)
        })

    return render(request, 'Users/UserPredict.html')