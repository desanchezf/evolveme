# Versión de linux que se va a utilizar dentro del container
FROM python:3.14-bookworm

# Evita la generación de archivos de bytecode (.pyc)
ENV PYTHONDONTWRITEBYTECODE 1
# Evita el almacenamiento en búfer de la salida y el error estándar
ENV PYTHONUNBUFFERED 1

# Instalar dependencias del sistema y herramientas de compilación
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    gettext \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip install --upgrade pip
RUN python -m pip install -r requirements.txt
COPY . /code/
