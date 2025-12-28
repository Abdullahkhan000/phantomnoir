# Use official Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project code
COPY . .

# Expose port
EXPOSE 8000

# Run migrations, load data, then start server
CMD sh -c "python manage.py migrate && python manage.py loaddata initial_data.json && gunicorn core.wsgi:application --bind 0.0.0.0:8000"
