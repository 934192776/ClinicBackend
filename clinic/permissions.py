from rest_framework import permissions

# 只有管理员可以修改，其他人只能看（比如医生列表）
class IsAdminOrReadOnly(permissions.BasePermission):
    """
    自定义权限：只有管理员（is_staff）可以执行 POST, PUT, DELETE
    其他人（比如患者）只能执行 GET (查看)
    """
    def has_permission(self, request, view):
        # 如果是安全的方法（GET, HEAD, OPTIONS），直接放行
        if request.method in permissions.SAFE_METHODS:
            return True
        # 否则，必须是超级管理员（admin角色）
        return request.user and request.user.is_staff

# 只能操作自己的对象（防止患者取消别人的预约）
class IsOwnerOrAdmin(permissions.BasePermission):
    """
    自定义权限：患者只能操作自己的预约，管理员可以操作所有人的。
    """
    def has_object_permission(self, request, view, obj):
        # 如果是管理员，放行
        if request.user.is_staff:
            return True
        # 如果是 GET 等安全方法，放行
        if request.method in permissions.SAFE_METHODS:
            return True
        # 否则，检查这个预约的 patient.user 是不是当前登录的用户
        return obj.patient.user == request.user