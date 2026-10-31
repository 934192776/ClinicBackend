from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from clinic.views import DoctorViewSet, TimeSlotViewSet, AppointmentViewSet

# 创建 DRF 路由器，自动生成 API 地址
router = DefaultRouter()
router.register(r'doctors', DoctorViewSet)
router.register(r'slots', TimeSlotViewSet)
router.register(r'appointments', AppointmentViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    # 登录获取 Token 的 API (login: username, password -> token)
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    # 包含刚才生成的 API 路由
    path('api/', include(router.urls)),
]