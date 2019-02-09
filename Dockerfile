FROM centos

RUN yum -y install epel-release; \ 
    yum -y install python2-pip;  

COPY ./requirements.txt /srv
COPY ./bootstrap.sh /srv
COPY ./app/ou_provisioner.py /srv

RUN pip install --no-cache-dir -r /srv/requirements.txt

ENTRYPOINT ["sh","/srv/bootstrap.sh"] 
