from django.urls import path
from Users.views import *

urlpatterns = [
    path('userhome/', userhome, name='userhome'),
    path('userpredict/', userpredict, name='userpredict'),
]