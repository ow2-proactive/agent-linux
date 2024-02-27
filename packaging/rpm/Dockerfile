# create an image suitable for building rpm packages:
# docker build -t agent-linux-packaging-centos .

FROM centos:centos8

RUN sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-*

RUN sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-*

RUN yum update -y

RUN yum -y install git wget ruby ruby-devel gcc make rsync tar gzip rpm-build

RUN /usr/sbin/useradd --create-home --shell /bin/bash --uid 1000 packager

USER packager

ENV HOME /home/packager
ENV GEM_HOME /home/packager/gems
ENV PATH="/home/packager/bin:${PATH}"

RUN gem install dotenv -v 2.8.1

RUN gem install fpm -f -V --no-user-install --bindir $GEM_HOME/bin
