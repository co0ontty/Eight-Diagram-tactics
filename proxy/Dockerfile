FROM ubuntu
RUN apt update -y &&\
    apt install nginx -y &&\
    echo "service nginx restart\ntail -f /var/log/nginx/*" >> /etc/startapache2.sh
CMD [ "sh","/etc/startapache2.sh"]