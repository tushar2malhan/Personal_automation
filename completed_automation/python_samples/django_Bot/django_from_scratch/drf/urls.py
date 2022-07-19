

#The `urlpatterns` list routes URLs to views. For more information please see:
#    https://docs.djangoproject.com/en/3.2/topics/http/urls/
#Examples:
#Function views
#     1. Add an import:  from my_app import views
#     2. Add a URL to urlpatterns:  path('', views.home, name='home')
# Class-based views
#     1. Add an import:  from other_app.views import Home
#     2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
# Including another URLconf
#     1. Import the include() function: from django.urls import include, path
#     2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))


from django.contrib import admin
from django.urls import path,include
from rest_framework.routers import DefaultRouter
from app.views import *
# creating router object 
router = DefaultRouter()

# register the viewsets with the router
router.register('student',normal_viewset, basename='normal_viewset')
router.register('read_only_model_viewset',read_only_model_viewset, basename='read_only_model_viewset')
router.register('model_viewset',model_viewset, basename='model_viewset')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('app.urls')),            # uncomment it accordingly
    path('api/',include(router.urls)),

]
