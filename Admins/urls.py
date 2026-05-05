from django.urls import path
from Admins.views import *

urlpatterns = [
    path('adminhome/', adminhome, name='adminhome'),
    path('admin_update_userstatus/<int:user_id>/', admin_update_userstatus, name='admin_update_userstatus'),
    path('adminuserratio/', adminuserratio, name='adminuserratio'),
    path('admin_accuracy/', admin_accuracy,name='admin_accuracy'),
]