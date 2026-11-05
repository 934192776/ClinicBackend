# clinic/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Doctor, Patient, TimeSlot, Appointment
from .serializers import DoctorSerializer, PatientSerializer, TimeSlotSerializer, AppointmentSerializer
from .permissions import IsAdminOrReadOnly, IsOwnerOrAdmin

# ==========================================
# 1. 医生视图集
# ==========================================
class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [IsAdminOrReadOnly]

# ==========================================
# 2. 时间段视图集
# ==========================================
class TimeSlotViewSet(viewsets.ModelViewSet):
    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer
    permission_classes = [IsAdminOrReadOnly]

# ==========================================
# 3. 预约视图集（核心逻辑）
# ==========================================
class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Appointment.objects.all().order_by('-created_at')
        else:
            return Appointment.objects.filter(patient__user=user).order_by('-created_at')

    def perform_create(self, serializer):
        patient, created = Patient.objects.get_or_create(
            user=self.request.user,
            defaults={'phone': ''}
        )
        serializer.save(patient=patient)
        time_slot = serializer.validated_data.get('time_slot')
        time_slot.is_available = False
        time_slot.save()

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        appointment = self.get_object()
        if appointment.status == 'Cancelled':
            return Response({"error": "This appointment is already cancelled."}, status=status.HTTP_400_BAD_REQUEST)

        appointment.status = 'Cancelled'
        appointment.save()

        time_slot = appointment.time_slot
        time_slot.is_available = True
        time_slot.save()

        return Response({"message": "Appointment cancelled successfully."}, status=status.HTTP_200_OK)

# ==========================================
# 4. 获取当前用户信息（它独立在类的外面！）
# ==========================================
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def current_user(request):
    """返回当前登录用户的信息，用来判断权限"""
    return Response({
        'id': request.user.id,
        'username': request.user.username,
        'is_staff': request.user.is_staff,
        'is_superuser': request.user.is_superuser
    })
