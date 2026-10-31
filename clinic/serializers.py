from rest_framework import serializers
from .models import Doctor, Patient, TimeSlot, Appointment
from django.contrib.auth.models import User

class DoctorSerializer(serializers.ModelSerializer): # 医生序列化器
    # 获取关联的 User 模型里的 username 和 email 字段，方便前端直接显示
    username = serializers.ReadOnlyField(source='user.username')
    email = serializers.ReadOnlyField(source='user.email')

    class Meta:
        model = Doctor
        fields = ['id', 'username', 'email', 'specialty', 'phone', 'bio']
        # 前端只能读取这些信息，如果要修改医生信息，其实是要修改底层的 User。


class TimeSlotSerializer(serializers.ModelSerializer): # 时间段序列化器
    # 这里套了 DoctorSerializer，前端看到时间段的同时，也能看到这个医生是谁
    doctor = DoctorSerializer(read_only=True)
    # 额外的doctor_id，这样管理员添加时间段时可以只传医生ID
    doctor_id = serializers.PrimaryKeyRelatedField(
        queryset=Doctor.objects.all(), source='doctor', write_only=True
    )

    class Meta:
        model = TimeSlot
        fields = ['id', 'doctor', 'doctor_id', 'date', 'start_time', 'is_available']
        # id是系统自动生成的。前端请求时，传 doctor_id, date, start_time就行

class PatientSerializer(serializers.ModelSerializer): # 患者序列化器
    username = serializers.ReadOnlyField(source='user.username')
    email = serializers.ReadOnlyField(source='user.email')

    class Meta:
        model = Patient
        fields = ['id', 'username', 'email', 'phone']


class AppointmentSerializer(serializers.ModelSerializer): # 预约序列化器
    #这里套了PatientSerializer，让前端能直接看到是哪个患者约了哪个时间段
    patient = PatientSerializer(read_only=True)
    time_slot = TimeSlotSerializer(read_only=True)

    # 提交预约时，前端只要传 time_slot_id 就够了（因为患者是通过 Token 识别的）
    time_slot_id = serializers.PrimaryKeyRelatedField(
        queryset=TimeSlot.objects.all(), source='time_slot', write_only=True
    )

    class Meta:
        model = Appointment
        fields = ['id', 'patient', 'time_slot', 'time_slot_id', 'status', 'notes', 'created_at']
        #我们在 models.py 里设置了一个时间段只能被预约一次（OneToOne），所以这里提交时，如果有重复，Django 会在序列化校验时自动拦截并报错