from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from clinic.views import RegisterView, CreateDoctorView

# 导入所有的 ViewSets 和 视图函数（加上 manage_patients）
from clinic.views import (
    DoctorViewSet, TimeSlotViewSet, AppointmentViewSet,
    current_user, manage_patients
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

    # 管理患者的接口
    path('api/patients/', manage_patients, name='patients-list'),
    path('api/patients/<int:pk>/', manage_patients, name='patient-detail'),

    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/admin/create-doctor/', CreateDoctorView.as_view(), name='create_doctor'),

    path('api/', include(router.urls)),
]