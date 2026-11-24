FROM alpine:latest

#构建镜像时的软件源
ARG SOURCES_APK=mirrors.tuna.tsinghua.edu.cn
ARG SOURCES_PIP=https://pypi.tuna.tsinghua.edu.cn/simple

WORKDIR /app
COPY . /app
RUN sed -i "s/dl-cdn.alpinelinux.org/${SOURCES_APK}/g" /etc/apk/repositories
RUN apk add --no-cache tzdata ffmpeg py3-pip python3 nodejs npm su-exec
RUN ln -fs /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN pip3 install -i $SOURCES_PIP --break-system-packages --no-cache-dir -r requirements.txt

RUN mkdir -p /app/config /app/logs /app/backup_config /app/downloads && chmod -R 777 /app
ENTRYPOINT ["sh", "/app/docker-entrypoint.sh"]
CMD ["python3", "main.py"]
