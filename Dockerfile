FROM centos
MAINTAINER vallard@benincosa.com
# install additional Packages
RUN yum -y install git make gcc python-devel
# Get PIP
RUN curl https://bootstrap.pypa.io/get-pip.py | python - 
# Get the Updated repos
RUN pip install ansible
RUN git clone https://github.com/ciscoucs/ucsmsdk && cd /ucsmsdk && make install && cd / && \
    git clone https://github.com/ciscoucs/ucsm_apis && cd /ucsm_apis && make install && cd / 
RUN git clone https://github.com/vallard/ucsm-ansible && cd /ucsm-ansible && python install.py && cd /
CMD ["/bin/bash"]
