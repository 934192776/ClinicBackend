from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError, PermissionDenied
from django.contrib.auth.models import User
from .models import Doctor, Patient, TimeSlot, Appointment
from .serializers import DoctorSerializer, DoctorUpdateSerializer, PatientSerializer, TimeSlotSerializer, \
    AppointmentSerializer
from .permissions import IsAdminOrReadOnly, IsOwnerOrAdmin


# 医生
class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return DoctorUpdateSerializer
        return DoctorSerializer

    def perform_destroy(self, instance):
        user = instance.user
        instance.delete()
        user.delete()


# 时间段
class TimeSlotViewSet(viewsets.ModelViewSet):
    serializer_class = TimeSlotSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        doctor_id = self.request.query_params.get('doctor_id')
        queryset = TimeSlot.objects.all()

        if user.is_staff and not user.is_superuser:
            queryset = queryset.filter(doctor__user=user)
        elif doctor_id:
            queryset = queryset.filter(doctor_id=doctor_id)

        return queryset.order_by('date', 'start_time')

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        if request.user.is_staff and not request.user.is_superuser:
            data['doctor_id'] = request.user.doctor_profile.id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        try:
            serializer.save()
        except Exception as e:
            raise ValidationError({"error": f"Failed to create slot. Reason: {str(e)}"})

    def perform_destroy(self, instance):
        user = self.request.user
        if user.is_staff and not user.is_superuser:
            if instance.doctor.user != user:
                raise PermissionDenied("You can only delete your own time slots.")
        instance.delete()


# 预约
class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Appointment.objects.all().order_by('-created_at')
        elif user.is_staff:
            return Appointment.objects.filter(time_slot__doctor__user=user).order_by('-created_at')
        else:
            return Appointment.objects.filter(patient__user=user).order_by('-created_at')

    def perform_create(self, serializer):
        user = self.request.user


        if user.is_superuser:
            patient_id = self.request.data.get('patient_id')
            if not patient_id:
                raise ValidationError("Admin must provide patient_id to book on behalf of a patient.")
            try:
                patient = Patient.objects.get(id=patient_id)
            except Patient.DoesNotExist:
                raise ValidationError("Patient not found.")


        elif user.is_staff:
            raise ValidationError("Doctors cannot book appointments. Please use a patient account.")


        else:
            patient, created = Patient.objects.get_or_create(
                user=user,
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
        time_slot = appointment.time_slot
        time_slot.is_available = True
        time_slot.save()
        appointment.delete()
        return Response({"message": "Appointment cancelled and slot released successfully."}, status=status.HTTP_200_OK)


# 获取当前用户信息
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def current_user(request):
    return Response({
        'id': request.user.id,
        'username': request.user.username,
        'is_staff': request.user.is_staff,
        'is_superuser': request.user.is_superuser
    })


# 管理员专属接口（管理患者）
@api_view(['GET', 'DELETE'])
@permission_classes([IsAdminUser])
def manage_patients(request, pk=None):
    if request.method == 'GET':

        patients = User.objects.filter(is_staff=False).values('id', 'username', 'email')
        return Response(list(patients))
    elif request.method == 'DELETE':
        try:
            user = User.objects.get(id=pk, is_staff=False)
            user.delete()
            return Response({"message": "Patient deleted"}, status=204)
        except User.DoesNotExist:
            return Response({"error": "Patient not found"}, status=404)


# 患者注册接口
class RegisterView(APIView):
    permission_classes = []

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        phone = request.data.get('phone', '')

        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, password=password)

        Patient.objects.create(user=user, phone=phone)
        return Response({"message": "Patient registered successfully"}, status=status.HTTP_201_CREATED)


# Admin 创建医生接口
class CreateDoctorView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        specialty = request.data.get('specialty', '')
        phone = request.data.get('phone', '')
        bio = request.data.get('bio', '')

        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, password=password, is_staff=True)
        Doctor.objects.create(user=user, specialty=specialty, phone=phone, bio=bio)

        return Response({"message": "Doctor created successfully"}, status=status.HTTP_201_CREATED)