from rest_framework import permissions

# 只有管理员或医生可以修改，其他人只能看
class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        # 医生和 Admin可以操作
        return request.user and request.user.is_staff


class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # 管理员和医生拥有操作权限
        if request.user.is_staff:
            return True
        if request.method in permissions.SAFE_METHODS:
            return True
        # 普通患者只能操作自己的
        return obj.patient.user == request.user