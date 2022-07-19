from re import template
import re
from regex import E

from app import serializers
from .models import Queries 
# Imported almost everything , create your view accordingly , if anything missed kindly add it manually

import json
from django.shortcuts import redirect, render
from django.http import HttpResponse , JsonResponse
from requests import api

from django.views.generic import ListView
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User          # get all the users  in ur account 

from rest_framework.decorators import api_view , permission_classes
from rest_framework.response import Response
from rest_framework. parsers import JSONParser
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token             # just like User table we import the Token table 
from rest_framework.generics import ListAPIView
from app.serializers import StudentSerializer, MySerializer
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import (
      ListModelMixin,
      CreateModelMixin,
      UpdateModelMixin,
      DestroyModelMixin,
      RetrieveModelMixin  )

from rest_framework.generics import (
      ListAPIView,CreateAPIView,
      RetrieveAPIView,UpdateAPIView,
      DestroyAPIView,

      ListCreateAPIView,
      RetrieveUpdateDestroyAPIView,)

from rest_framework import viewsets

from app.forms import Myform

# normal func base views
def student_details(request,pk=None):
      if request.method == 'GET':
            stu = Queries.objects.all()
            # count total objects in ur table
            count = Queries.objects.all().count()
            print(count)
            my_serializer = MySerializer(stu,  many = True) 
            # print(my_serializer.data)
            if my_serializer.data:
                  return JsonResponse(my_serializer.data, safe=False)
            
            # json_data = json.dumps(my_serializer.data )
            # we need to convert to json format, so that we can send it to the HttpResponse
            # return HttpResponse(json_data, content_type='application/json')

      if request.method == 'POST':
            data = JSONParser().parse(request)
            print(data)
            # import pdb; pdb.set_trace()
            serializer = MySerializer(data=data) # here we are passing the data to the serializer
            if serializer.is_valid():
                  serializer.save()       # here we are saving the data to the database
                  return JsonResponse(serializer.data, status=201)
            return JsonResponse(serializer.errors, status=400)

      if request.method == 'PUT':
            print(request.body )
            # import pdb; pdb.set_trace()
            obj = Queries.objects.get(pk=pk)
            data =  json.loads(request.body ) 
            serializer = StudentSerializer(obj, data=data)
            if serializer.is_valid():
                  serializer.save()
                  return JsonResponse(serializer.data)
            # return JsonResponse(serializer.errors, status=400)

      if request.method == "DELETE":
            obj= Queries.objects.get(pk=pk).delete()
            return Response('delete_message delete called with class api ')


# DRF FUNC based views - here calling the request methods are same, we just use api_view to make it DRF 
@api_view(['GET', 'POST','PUT','DELETE'])
def drf_func(request,ok=None):
      all_objects = Queries.objects.all()
      serializer = StudentSerializer(all_objects, many=True)
      if request.method == 'POST':
            serializer = StudentSerializer(data=request.data)
            if serializer.is_valid():
                  serializer.save()
                  print('New Data Saved')
                  return Response(serializer.data)
      if request.method == "PUT":
            import pdb;pdb.set_trace()
            ok = request.data.get('id')
            one_obj = Queries.objects.get(id = ok )
            serializer = StudentSerializer(one_obj, data = request.data)
            if serializer.is_valid():
                  serializer.save()
                  print('data is updated')
                  return Response({'data updated':serializer.data})
            ...
      if request.method == "DELETE":
            one_obj = Queries.objects.get(id = ok ).delete()
            return Response({'data deleted':'deleted'})

      return  Response(serializer.data,202)


# class based views  -  we call the request methods in different functions named by HTTP methods
class  cls_func(APIView):
      def get(self, request, pk=None):
            if not pk:
                  obj = Queries.objects.all()
                  serializer = StudentSerializer(obj, many=True)
                  return Response(serializer.data)
            serializer = StudentSerializer(Queries.objects.get(id=pk))
            return Response(serializer.data)
      def post(self,request):
            serializer = StudentSerializer(data=request.data)
            if serializer.is_valid():
                  serializer.save()
                  return Response(serializer.data, status=201) 
      def put(self,request,pk=None):
            obj = Queries.objects.get(id = pk)  # url =  http://127.0.0.1:8000/cls/9/
            # else:
            #  pk = request.data.get('id')      # where in data we pass id 
            #                                   url =  http://127.0.0.1:8000/cls/ 
            # obj  = Querys.objects.get(id = pk)
            serializer = StudentSerializer(obj, request.data)
            if serializer.is_valid():
                  serializer.save()
                  return Response(serializer.data)
            return Response({'message':'put called'})
      def delete(self,request,pk=None):
            obj = Queries.objects.get(id = pk).delete()
            return Response({'message deleted':obj})


# SPECIFIC  MIXINS   - each class each http method but we dont return serializer.data or give Response instead we 
class cls_list_mixins(GenericAPIView, ListModelMixin):
      queryset = Queries.objects.all()
      serializer_class = StudentSerializer
      
      # inbuilt method   get()  and list() 
      def get(self, request,*args,**kwargs):
            return self.list(request,*args,**kwargs)

class cls_create_mixins(GenericAPIView, CreateModelMixin):
      queryset = Queries.objects.all()
      serializer_class = StudentSerializer
      
      # inbuilt method   post()  and create() 
      def post(self, request,*args,**kwargs):
            return self.create(request,*args,**kwargs)

class cls_retreive_mixins(GenericAPIView, RetrieveModelMixin):
      queryset = Queries.objects.all()
      serializer_class = StudentSerializer
      
      # inbuilt method   get()  and retrieve() 
      def get(self, request,*args,**kwargs):
            return self.retrieve(request,*args,**kwargs)

class cls_update_mixins(GenericAPIView, UpdateModelMixin):
      queryset = Queries.objects.all()
      serializer_class = StudentSerializer
      
      # inbuilt method   put()  and update() 
      def put(self, request,*args,**kwargs):
            return self.update(request,*args,**kwargs)

class cls_delete_mixins(GenericAPIView, DestroyModelMixin):

      queryset = Queries.objects.all()
      serializer_class = StudentSerializer
      
      # inbuilt method   delete()  and destroy() 
      def delete(self, request,*args,**kwargs):
            return self.destroy(request,*args,**kwargs)



# MIXINS   Making two groups these  5 classes
# LIST AND CREATE - No pk requried
class grp_list_create_mixins(GenericAPIView, ListModelMixin, CreateModelMixin):
      queryset = Queries.objects.all()
      serializer_class = StudentSerializer

      def get(self, request,*args,**kwargs):
            return self.list(request,*args,**kwargs)
      def post(self, request,*args,**kwargs):
            return self.create(request,*args,**kwargs)

# RETREIVE DESTROY UPDATE - pk is required
class grp_retreive_update_delete_mixins(GenericAPIView,
                              RetrieveModelMixin, 
                              UpdateModelMixin,
                              DestroyModelMixin):
      queryset = Queries.objects.all()
      serializer_class = StudentSerializer
      
      def get(self, request,*args,**kwargs):
            return self.retrieve(request,*args,**kwargs)
      def put(self, request,*args,**kwargs):
            return self.update(request,*args,**kwargs)
      def delete(self, request,*args,**kwargs):
            return self.destroy(request,*args,**kwargs)



# # generics views - for each http method created one class
class generics_list_view_(ListAPIView):
      queryset = Queries.objects.all()
      serializer_class = StudentSerializer

class generics_create_view_(CreateAPIView):
      queryset = Queries.objects.all()
      serializer_class = StudentSerializer

class generics_retreive_view_(RetrieveAPIView):
      queryset = Queries.objects.all()
      serializer_class = StudentSerializer

class generics_update_view_(UpdateAPIView):
      queryset = Queries.objects.all()
      serializer_class = StudentSerializer

class generics_delete_view_(DestroyAPIView):
      queryset = Queries.objects.all()
      serializer_class = StudentSerializer


# COMBINATION OF LIST CREATE  GENERICS VIEWS
class grp_generics_list_create_view(ListCreateAPIView):
      queryset = Queries.objects.all()
      serializer_class = StudentSerializer

class grp_generics_retreive_update_delete_view(RetrieveUpdateDestroyAPIView):
      queryset = Queries.objects.all()
      serializer_class = StudentSerializer



# VIEWSETS
class normal_viewset(viewsets.ViewSet):
      def list(self, request):
            queryset = Queries.objects.all()
            serializer = StudentSerializer(queryset, many=True)
            return Response(serializer.data)
      def create(self, request):
            serializer = StudentSerializer(data=request.data)
            if serializer.is_valid():
                  serializer.save()
                  return Response(serializer.data, status=201)
      def retrieve(self, request, pk=None):
            queryset = Queries.objects.get(id = pk)
            serializer = StudentSerializer(queryset)
            return Response(serializer.data)
      def update(self, request, pk=None):
            queryset = Queries.objects.get(id = pk)
            serializer = StudentSerializer(queryset, data=request.data)
            if serializer.is_valid():
                  serializer.save()
                  return Response(serializer.data)
      def destroy(self, request, pk=None):
            queryset = Queries.objects.get(id = pk).delete()
            return Response({'message deleted':queryset})
      def partial_update(self,request,pk):
            queryset = Queries.objects.get(id = pk)
            serializer = StudentSerializer(queryset, data=request.data, partial=True)
            if serializer.is_valid():
                  serializer.save()
                  return Response(serializer.data)



# Model ViewSet - retrieve,read operations only - no create,update,delete
class read_only_model_viewset(viewsets.ReadOnlyModelViewSet):
      queryset = Queries.objects.all()
      serializer_class = StudentSerializer

# Model ViewSet - CRUD complete
class model_viewset(viewsets.ModelViewSet):
      queryset = Queries.objects.all()
      serializer_class = StudentSerializer
      

# TEMPLATE VIEWS  func based 
def func_base_FormView(request,pk=None):
      form = Myform()
      all_objects = Queries.objects.all()
      if request.method == 'POST':
            form = Myform(request.POST)
            if form.is_valid():
                  form.save()
                  return render (request, 'success.html', {'form': form}) 
            return HttpResponse ('form is invalid ')


      return render (   request, 'form_template.html', {'form': form, 'all_objects': all_objects}  )

def deletetask(request,pk):
      item = Queries.objects.get(id = pk)
      if request.method == 'POST':
            item.delete()
            return redirect('base')

      return render (request, 'delete.html', {'item': item})



# TEMPLATE VIEWS  class based
from django.views import View

class cls_base_FormView(View):
    form_class = Myform
    initial = {'key': 'value'}
    template_name = 'form_template.html'
    all_objects = Queries.objects.all()

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
      #   import pdb; pdb.set_trace()
        return render(request, self.template_name, {'form': form,  'all_objects': self.all_objects})

    def post(self, request, *args, **kwargs):
      form = self.form_class(request.POST)
      if form.is_valid():
            form.save()
            # return redirect('/success/')     # both way we can render and send data 
            return render (request, 'success.html', {'form': form})  # this way too 

      return render(request, self.template_name, {'form': form, 'all_objects': self.all_objects})


