# Use an official Python runtime as a parent image
FROM python:3.11

# Set environment variables for TORCH to use CPU
ENV TORCH_DEVICE=cpu

# Install system requirements
RUN apt-get update && \
    apt-get install -y git curl wget unzip apt-transport-https \
    ghostscript lsb-release

# Install tesseract 5 (optional)
RUN echo "deb https://notesalexp.org/tesseract-ocr5/$(lsb_release -cs)/ $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/notesalexp.list > /dev/null && \
    apt-get update -oAcquire::AllowInsecureRepositories=true && \
    apt-get install -y --allow-unauthenticated notesalexp-keyring && \
    apt-get update && \
    apt-get install -y --allow-unauthenticated tesseract-ocr libtesseract-dev \
    libmagic1 ocrmypdf tesseract-ocr-eng tesseract-ocr-deu \
    tesseract-ocr-por tesseract-ocr-spa tesseract-ocr-rus \
    tesseract-ocr-fra tesseract-ocr-chi-sim tesseract-ocr-jpn \
    tesseract-ocr-kor tesseract-ocr-hin \
    pandoc \
    latexml

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD . /app


# Install any needed packages specified in requirements.lock
RUN pip install --no-cache-dir -r requirements.lock

# Uninstall torch
RUN pip uninstall torch torchvision torchaudio -y

# Install torch without CUDA support
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Set the tesseract data folder path for Ubuntu 22.04 with tesseract 5
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata

# Make port 80 available to the world outside this container
EXPOSE 80

# Run app.py when the container launches
CMD ["uvicorn", "convert_to_md.main:app", "--host", "0.0.0.0", "--port", "80", "--log-level", "debug"]




