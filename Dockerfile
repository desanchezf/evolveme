# Versión de linux que se va a utilizar dentro del container
FROM python:3.12-bookworm

# Evita la generación de archivos de bytecode (.pyc)
ENV PYTHONDONTWRITEBYTECODE=1
# Evita el almacenamiento en búfer de la salida y el error estándar
ENV PYTHONUNBUFFERED=1
# Instala paquetes en el sistema sin entorno virtual (adecuado para Docker)
ENV UV_SYSTEM_PYTHON=1

# Copiar UV desde la imagen oficial
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Instalar dependencias del sistema y herramientas de compilación
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    gettext \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN uv pip install -r requirements.txt
COPY . /code/
