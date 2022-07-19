
from django.urls import path
from .views import  *
from django.http.response import HttpResponse
# import csrf_exempt
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [

    path('home/',lambda request:HttpResponse('Message Created By Tushar Malhan'  ) ),
    path('check/', csrf_exempt(student_details), name ='details' ),
    path('check/<int:pk>', csrf_exempt(student_details), name ='details' ),

    path('', csrf_exempt(drf_func) ),
    path('<int:ok>/', csrf_exempt(drf_func) ),

    path('cls', csrf_exempt(cls_func.as_view()) ),
    path('cls/<int:pk>', csrf_exempt(cls_func.as_view()) ),

    path('cls_list_mixins', csrf_exempt(cls_list_mixins.as_view()) ),
    path('cls_create_mixins', csrf_exempt(cls_create_mixins.as_view()) ),
    path('cls_retreive_mixins/<int:pk>', csrf_exempt(cls_retreive_mixins.as_view()) ),
    path('cls_update_mixins/<int:pk>', csrf_exempt(cls_update_mixins.as_view()) ),
    path('cls_delete_mixins/<int:pk>', csrf_exempt(cls_delete_mixins.as_view()) ),

    path('grp_list_create_mixins', csrf_exempt(grp_list_create_mixins.as_view()) ),
    path('grp_list_create_mixins/<int:pk>', csrf_exempt(grp_retreive_update_delete_mixins.as_view()) ),
    # path('grp_retreive_update_delete_mixins/<int:pk>', csrf_exempt(grp_retreive_update_delete_mixins.as_view()) ), # not required because in same url only we can do CRUD

    path('generics_list_view', csrf_exempt(generics_list_view_.as_view()) ),
    path('generics_create_view_', csrf_exempt(generics_create_view_.as_view()) ),
    path('generics_retreive_view_/<int:pk>', csrf_exempt(generics_retreive_view_.as_view()) ),
    path('generics_update_view/<int:pk>/', csrf_exempt(generics_update_view_.as_view()) ),
    path('generics_delete_view/<int:pk>/', csrf_exempt(generics_delete_view_.as_view()) ),

    path('grp_generics_list_create_view', csrf_exempt(grp_generics_list_create_view.as_view()) ),
    path('grp_generics_list_create_view/<int:pk>', csrf_exempt(grp_generics_retreive_update_delete_view.as_view()) ),

    path('func_base_FormView/', csrf_exempt(func_base_FormView), name ='base' ),
    path('delete/<int:pk>', deletetask, name="delete"),
    path('cls_base_FormView/', csrf_exempt(cls_base_FormView.as_view()) ),
    path('success/', csrf_exempt(cls_base_FormView.as_view()) , name='home' ),
]
