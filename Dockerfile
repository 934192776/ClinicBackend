# 1. 指定基础镜像：使用官方提供的轻量级 Python 3.11 运行环境
FROM python:3.11-slim

# 2. 设置环境变量，防止 Python 把生成的字节码文件（.pyc）写进硬盘，并让控制台日志实时输出
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. 在容器内部创建一个名为 /app 的工作目录，并切换进去
WORKDIR /app

# 4. 把我们本地 backend 文件夹里的 requirements.txt 复制到容器的 /app 目录下
COPY requirements.txt /app/

# 5. 在容器内运行 pip 命令安装所有的依赖包（如 Django, DRF 等）
RUN pip install --no-cache-dir -r requirements.txt

# 6. 把本地 backend 目录下的所有代码（包括 manage.py, clinic 等）全部复制到容器的 /app 目录
COPY . /app/

# 7. 声明容器运行时对外暴露的端口是 8000
EXPOSE 8000

# 8. 容器启动时，默认执行 Django 的开发服务器，绑定到 0.0.0.0 允许外部访问
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]