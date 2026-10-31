from django.contrib import admin
# 从 models 文件里导入这 4 个模型
from .models import Doctor, Patient, TimeSlot, Appointment

# 把模型注册到 Django Admin 后台
admin.site.register(Doctor)
admin.site.register(Patient)
admin.site.register(TimeSlot)
admin.site.register(Appointment)