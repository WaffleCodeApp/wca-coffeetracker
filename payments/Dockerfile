FROM public.ecr.aws/docker/library/python:3.12

# Ensure Python output is unbuffered so logs appear immediately in CloudWatch
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./

# Set the CMD to your handler
CMD ["python", "-m", "awslambdaric", "handler.lambda_handler"]
