

from django.db import models
from django.contrib.auth.models import User


class Doctor(models.Model):
    """
    医生模型
    一对一关联Django内置User
    """
    # 一对一关联User
    # 一个用户对应一个医生资料
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='doctor_profile'
    )

    # 科室
    specialty = models.CharField(max_length=100)

    # 联系电话
    phone = models.CharField(max_length=20)

    # 简介
    bio = models.TextField(blank=True)

    # 创建时间
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # 显示用户名（不是单独存name）
        return f"Dr. {self.user.username}"

    class Meta:
        ordering = ['-created_at']


class Patient(models.Model):
    """
    患者模型
    一对一关联Django内置User
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='patient_profile'
    )

    # 联系电话
    phone = models.CharField(max_length=20)

    # 创建时间
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

    class Meta:
        ordering = ['-created_at']


class TimeSlot(models.Model):
    """
    时间段模型
    医生创建可预约的时间段
    """
    # 外键关联医生
    # 一个医生可以有多个时间段
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name='time_slots'
    )

    # 日期
    date = models.DateField()

    # 开始时间
    start_time = models.TimeField()

    # 是否可预约
    is_available = models.BooleanField(default=True)

    # 创建时间
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # 防止重复：同一医生、同一天、同一时间只能有一个时间段
        unique_together = ['doctor', 'date', 'start_time']
        ordering = ['date', 'start_time']

    def __str__(self):
        return f"{self.doctor.user.username} - {self.date} - {self.start_time}"


class Appointment(models.Model):
    """
    预约模型
    患者预约时间段
    """
    STATUS_CHOICES = [
        ('Booked', '已预约'),
        ('Cancelled', '已取消'),
    ]

    # 外键关联患者
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='appointments'
    )

    # 一对一关联时间段
    # 一个时间段只能被预约一次（防止重复预约）
    time_slot = models.OneToOneField(
        TimeSlot,
        on_delete=models.CASCADE,
        related_name='appointment'
    )

    # 预约状态
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Booked'
    )

    # 患者备注（选填）
    notes = models.TextField(blank=True)

    # 创建时间
    created_at = models.DateTimeField(auto_now_add=True)

    # 更新时间
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.patient.user.username} - {self.time_slot.doctor.user.username}"

    class Meta:
        ordering = ['-created_at']