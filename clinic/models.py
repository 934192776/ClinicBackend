from django.db import models
from django.contrib.auth.models import User


# 导入django自带的User表（这个是Django内置的用户表，存账号，密码，用户名）

class Doctor(models.Model):
    """ 定义医生，（对应数据库的医生表），一对一关联Django内置User """
    # 一个用户User对应一个医生资料
    user = models.OneToOneField(  # User字段：一对一关联内置User表， OneToOneField 一对一：一个User只能绑定一个医生，一个医生只属于一个User
        User,  # 关联目标表：Django内置User表
        on_delete=models.CASCADE,  # 删除规则。CASCADE = 删父删子（删掉这个User账号时，对应的医生资料一起删除
        related_name='doctor_profile'  # related_name：反向查询名字，以后拿到User对象时,可以用User.doctor_profile直接找到对应的医生信息
    )

    specialty = models.CharField(max_length=100)  # 科室， CharField短字符串，max_length=100 最多存100个字符， 必须填写

    phone = models.CharField(max_length=20)  # 联系电话，短文本，不设数字类型是因为手机号 可能有+，横杠，不要用Integrity

    bio = models.TextField(blank=True)  # 医生简介. TextField长文本. black=True 表单可以不填，允许为空

    created_at = models.DateTimeField(auto_now_add=True)  # 创建时间， auto_now_add=True 这条记录第一次存入数据库时，自动记录当前时间，之后不会自动改变

    def __str__(self):
        # 显示用户名（不是单独存name）
        return f"Dr. {self.user.username}"  # 在后台admin，调试打印的时候，显示这个字符串，方便看懂，不存入数据库

    class Meta:  # Meta 给这张表加配置，不是字段
        ordering = ['-created_at']  # 默认排序规则。-created_at 负号-代表倒序，最新创建的医生排在最前面


class Patient(models.Model):
    """ 定义患者，（数据库患者表），一对一关联Django内置User， 一个账号User对应一份患者资料"""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,  # 删除规则。CASCADE = 删父删子（删掉这个User账号时，对应的患者资料一起删除
        related_name='patient_profile'  # related_name反向查询名字。以后拿到user对象时，可以用User.patient_profile直接找到对应的患者信息
    )

    phone = models.CharField(max_length=20)  # 患者手机号。

    created_at = models.DateTimeField(auto_now_add=True)  # 创建时间， auto_now_add=True 这条记录第一次存入数据库时，自动记录当前时间，之后不会自动改变

    def __str__(self):  # 显示用户名（不是单独存name）
        return self.user.username  # 后台展示的时候直接显示患者用户名，在后台admin，调试打印的时候，显示这个字符串，方便看懂，不存入数据库

    class Meta:  # 给这张表加配置，不是字段
        ordering = ['-created_at']  # 默认排序规则。-created_at 负号-代表倒序，最新创建的医生排在最前面


class TimeSlot(models.Model):
    """ 定义时间段，（时间表），医生创建可预约的时间段 """

    doctor = models.ForeignKey(  # FK外键关联医生，一个医生可以有多个时间段，一条TimeSlot = 医生一个空闲时段
        Doctor,
        on_delete=models.CASCADE,  # 删除规则。CASCADE = 删父删子（删掉这个User账号时，对应的预约的时间段的资料一起删除
        related_name='time_slots'  # 反向查询：doctor.time_slots直接拿到这个医生全部空闲时间
    )

    date = models.DateField()  # date日期字段，只存年月日

    start_time = models.TimeField()  # 时间字段，只存几点几分

    is_available = models.BooleanField(default=True)  # is_available是否可预约,布尔值： default=True 默认新建出来就是“可预约”

    # 创建时间
    created_at = models.DateTimeField(auto_now_add=True)  # 这条时间段记录的创建时间

    class Meta:
        unique_together = ['doctor', 'date', 'start_time']  # 防止医生重复创建一模一样的空闲时段：同一医生、同一天、同一时间只能有一个时间段，不能出现第2条
        ordering = ['date', 'start_time']  # 默认：先按日期排，同一天再按时间从小到大排

    def __str__(self):
        return f"{self.doctor.user.username} - {self.date} - {self.start_time}"


class Appointment(models.Model):
    """ 定义预约，（预约表），患者预约时间段，绑定一个空闲时间段"""

    STATUS_CHOICES = [
        ('Booked', '已预约'),
        ('Cancelled', '已取消'),  # 常量，下拉选项：预约状态只有2种，已预约/已取消
    ]

    patient = models.ForeignKey(  # 外键关联患者，一对多：一个患者可以有多个预约
        Patient,
        on_delete=models.CASCADE,  # 删除规则。CASCADE = 删父删子（删掉这个User账号时，对应的预约的时间段的资料一起删除
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