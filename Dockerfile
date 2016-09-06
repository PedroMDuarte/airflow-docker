# AUTHOR: Pedro M Duarte
# DESCRIPTION: Airflow container
# BUILD: docker build --rm -t airflow-docker .
# SOURCE: https://github.com/PedroMDuarte/airflow-docker

FROM python:3.5
MAINTAINER pmd323@gmail.com
###############################################################################

RUN apt-get update && apt-get -y install \
    tree \
    htop \
    vim \
    telnet \
    net-tools \
    freetds-dev \
    build-essential \
    python-dev \
    openssh-server

# Postgresql client
RUN echo 'deb http://apt.postgresql.org/pub/repos/apt/ trusty-pgdg main 9.5' >/etc/apt/sources.list.d/postgresql.list && \
    curl https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - && \
    apt-get update && apt-get -y install \
    postgresql-client-9.5 \
    libpq-dev

# SSH server
EXPOSE 22
RUN mkdir /var/run/sshd && \
    echo 'root:root' | chpasswd && \
    sed -i 's/PermitRootLogin without-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \
    # SSH login fix. Otherwise user is kicked off after login
    sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd
ENV NOTVISIBLE "in users profile"
RUN echo "export VISIBLE=now" >> /etc/profile && \
    echo "KexAlgorithms=diffie-hellman-group1-sha1" >> /etc/ssh/sshd_config
# http://unix.stackexchange.com/questions/169341/key-based-authentication-from-pycharm-jsch-to-openbsd-fails
# http://stackoverflow.com/questions/26424621/algorithm-negotiation-fail-ssh-in-jenkins

ENV TERM=xterm

###################################################################
# Airflow
###################################################################

RUN mkdir -p /opt/airflow
ENV AIRFLOW_HOME=/opt/airflow
COPY ./conf/airflow.cfg /opt/airflow/airflow.cfg
COPY ./setup_airflow_connections.py /opt/airflow/setup_airflow_connections.py

WORKDIR /opt
RUN git clone https://github.com/PedroMDuarte/incubator-airflow.git
WORKDIR /opt/incubator-airflow
RUN git checkout connections-cli
RUN pip install -e .[devel,all_dbs]

# expose port for airflow log server
EXPOSE 8793

# expose port for airflow webserver
EXPOSE 8080

# expose port for flower
EXPOSE 5555

# expose port for ssh
EXPOSE 22

COPY ./entrypoint.sh /opt/airflow/entrypoint.sh
WORKDIR ${AIRFLOW_HOME}
