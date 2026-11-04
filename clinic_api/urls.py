from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

# 导入所有的 ViewSets 和 视图函数
from clinic.views import (
    DoctorViewSet, TimeSlotViewSet, AppointmentViewSet,
    current_user, create_admin
)

router = DefaultRouter()
router.register(r'doctors', DoctorViewSet)
router.register(r'slots', TimeSlotViewSet)
router.register(r'appointments', AppointmentViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),

    # 认证获取 Token
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),

    # 当前用户信息 (你的前端靠这个判断是不是 Admin)
    path('api/current-user/', current_user, name='current-user'),

    # 临时救急用的接口
    path('api/create-admin/', create_admin, name='create-admin'),

    # 注册所有的 API 路由
    path('api/', include(router.urls)),
]