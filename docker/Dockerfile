FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
EXPOSE 56741

ARG uid

ENV USER fuzz
ENV PASS fuzz

RUN apt update --fix-missing && apt -y upgrade --fix-missing
RUN apt install -y git cmake \
build-essential libssl-dev \
libcurl4-openssl-dev libncurses-dev \
g++ gcc \
make bc \
flex bison libelf-dev \
libssl-dev \
qemu-system-x86 qemu-utils \
sudo python3 python3-pip \
wget debootstrap \
ninja-build libz3-dev \
locales file \
vim jq

RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
        echo 'LANG="en_US.UTF-8"'>/etc/default/locale && \
        dpkg-reconfigure --frontend=noninteractive locales && \
        update-locale LANG=en_US.UTF-8

RUN addgroup --quiet --system kvm
RUN userdel -r ubuntu

RUN useradd -s /bin/bash -m -u $uid $USER 
RUN echo "$USER:$PASS" | chpasswd
RUN usermod -a -G kvm $USER

RUN echo "%$USER  ALL=(ALL:ALL) NOPASSWD: ALL" > /etc/sudoers.d/fuzz
RUN chmod 0440 /etc/sudoers.d/fuzz

RUN wget https://go.dev/dl/go1.23.5.linux-amd64.tar.gz
RUN rm -rf /usr/local/go ; tar -C /usr/local -xzf go1.23.5.linux-amd64.tar.gz

USER $USER

ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8
ENV PATH /usr/local/go/bin:$PATH

RUN pip install --user --break-system-packages networkx
RUN pip install --user --break-system-packages matplotlib

WORKDIR /home/$USER

CMD ["/bin/bash"]