FROM alpine:latest

#运行时使用的用户及组ID
ARG UID=1000
#构建镜像时的软件源
ARG SOURCES_APK=mirrors.tuna.tsinghua.edu.cn
ARG SOURCES_PIP=https://pypi.tuna.tsinghua.edu.cn/simple

WORKDIR /app
COPY . /app
RUN <<USERADD
  addgroup -S -g "$UID" user
  adduser -S -u "$UID" -G user -h /app -s /bin/sh user
  echo "user "user" added and UID is ${UID}."
  sleep 5
USERADD
RUN sed -i "s/dl-cdn.alpinelinux.org/${SOURCES_APK}/g" /etc/apk/repositories
RUN apk add --no-cache tzdata ffmpeg py3-pip python3 nodejs npm
RUN ln -fs /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN pip3 install -i $SOURCES_PIP --break-system-packages --no-cache-dir -r requirements.txt

CMD chown -R user:user . && su -c "python3 main.py" user
