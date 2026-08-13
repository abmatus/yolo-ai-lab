FROM nvcr.io/nvidia/l4t-pytorch:r35.2.1-pth2.0-py3

ENV DEBIAN_FRONTEND=noninteractive
ENV LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libgomp.so.1

WORKDIR /workspace

RUN apt-get update && apt-get install -y \
    python3-pip \
    libgl1-mesa-glx \
    libglib2.0-0 \
    graphviz \
    zip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir --upgrade pip setuptools wheel "packaging>=24.0"

RUN pip3 install --no-cache-dir \
    "pyzmq<26.0.0" \
    "jupyterlab>=3.6.0,<4.0.0" \
    "ultralytics==8.1.34" \
    "opencv-python-headless==4.9.0.80" \
    "matplotlib<3.8.0" \
    "pandas<2.1.0" \
    "seaborn" \
    "reportlab==4.1.0" \
    "pyyaml"

EXPOSE 8888

CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=''"]
