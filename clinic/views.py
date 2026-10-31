from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Doctor, Patient, TimeSlot, Appointment
from .serializers import DoctorSerializer, PatientSerializer, TimeSlotSerializer, AppointmentSerializer
from .permissions import IsAdminOrReadOnly, IsOwnerOrAdmin


# 医生视图集
class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    # 权限：只有管理员能修改，其他人只能看
    permission_classes = [IsAdminOrReadOnly]


# 时间段视图集
class TimeSlotViewSet(viewsets.ModelViewSet):
    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer
    # 权限：只有管理员能创建/修改时间段，患者只能看
    permission_classes = [IsAdminOrReadOnly]


# 预约视图集（核心逻辑）
class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    # 权限：必须登录，且只能操作自己的（除了管理员）
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        """
        根据登录用户的角色，返回不同的数据
        管理员可以看所有预约，患者只能看自己的预约。
        """
        user = self.request.user
        if user.is_staff:
            return Appointment.objects.all().order_by('-created_at')
        else:
            # 返回当前用户关联的 Patient 的所有预约
            return Appointment.objects.filter(patient__user=user).order_by('-created_at')

    def perform_create(self, serializer):
        """
        当患者创建预约时，自动把当前登录用户绑定为 Patient，防止有人伪造。
        （这就是不用 try-except，而是重写方法解决安全问题）
        """
        # 获取或创建当前用户的 Patient 资料
        patient, created = Patient.objects.get_or_create(
            user=self.request.user,
            defaults={'phone': ''}
        )
        # 保存预约，把 time_slot 和 patient 绑定
        serializer.save(patient=patient)

        # 同时，把该时间段标记为不可用
        time_slot = serializer.validated_data.get('time_slot')
        time_slot.is_available = False
        time_slot.save()

    # 自定义 Action：取消预约
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        患者取消自己的预约。URL: /api/appointments/{id}/cancel/
        """
        appointment = self.get_object()  # 获取当前预约（权限已由 IsOwnerOrAdmin 过滤）

        if appointment.status == 'Cancelled':
            return Response({"error": "This appointment is already cancelled."}, status=status.HTTP_400_BAD_REQUEST)

        # 修改状态为已取消
        appointment.status = 'Cancelled'
        appointment.save()

        # 释放时间段
        time_slot = appointment.time_slot
        time_slot.is_available = True
        time_slot.save()

        return Response({"message": "Appointment cancelled successfully."}, status=status.HTTP_200_OK)