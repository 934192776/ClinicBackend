from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from clinic.views import RegisterView, CreateDoctorView, CreatePatientView


from clinic.views import (
    DoctorViewSet, TimeSlotViewSet, AppointmentViewSet,
    current_user, CreatePatientView
)

router = DefaultRouter()
router.register(r'doctors', DoctorViewSet)
router.register(r'slots', TimeSlotViewSet, basename='slot')
router.register(r'appointments', AppointmentViewSet, basename='appointment')

urlpatterns = [
    path('admin/', admin.site.urls),

    # 认证获取 Token
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),

    # 当前用户信息
    path('api/current-user/', current_user, name='current-user'),


    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/admin/create-doctor/', CreateDoctorView.as_view(), name='create_doctor'),
    path('api/admin/create-patient/', CreatePatientView.as_view(), name='create_patient'),
    path('api/', include(router.urls)),
]