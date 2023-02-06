FROM python:3.9-slim
# install git for pip to install from git
RUN apt-get update && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/* && \
    pip3 install --upgrade pip

WORKDIR /app

COPY . /app
RUN --mount=type=cache,target=/root/.cache \
    pip3 install .
CMD ["run_plugin", "--read_args_from_env", "True"]
