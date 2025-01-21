
FROM python

# Set the working directory inside the container
WORKDIR /app

# Install GDAL and other system dependencies
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    && apt-get clean

# Set the GDAL library path
ENV GDAL_LIBRARY_PATH=/usr/lib/libgdal.so

# Copy only the requirements file first for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt


COPY . .


EXPOSE 8000


CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
