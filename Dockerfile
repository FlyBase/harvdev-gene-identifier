FROM rustlang/rust:nightly-alpine3.17


# RUN apk add libressl-dev
RUN apk add curl git g++ cargo openssl pkgconfig py3-pip python3-dev
RUN env
RUN python3 --version
WORKDIR /usr/src/app

COPY . .

#RUN find / -name .cargo -print
#RUN which cargo
#RUN source /usr/src/.cargo/env
#RUN apk add cargo
#RUN which cargo

#RUN cargo --version

##RUN rustc --version
#RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
#RUN source $HOME/.cargo/env && rustup default nightly && rustup update
## RUN rustup default nightly && rustup update
#RUN source $HOME/.cargo/env
#RUN rustc --version

RUN pip install --upgrade pip

#RUN git clone https://huggingface.co/cgrivaz/FlyBaseGeneAbstractClassifier.git
#RUN git clone https://github.com/grivaz/FlyBaseAnnotationHelper.git

# WORKDIR /usr/src/app/FlyBaseAnnotationHelper
# RUN echo $PWD

WORKDIR /usr/src/app
RUN pip install -r requirements.txt

WORKDIR /usr/src/app/FlyBaseAnnotationHelper
RUN echo $PWD
RUN pip install -r requirements.txt


#RUN pip3 install torch --index-url https://download.pytorch.org/whl/cpu

# In this mode PyTorch computations will run on your CPU, not your GPU
RUN git clone --recursive https://github.com/pytorch/pytorch
WORKDIR /usr/src/app/pytorch
RUN git submodule sync
RUN git submodule update --init --recursive
RUN python setup.py develop



WORKDIR /usr/src/app/

COPY data/fb_synonym_fb_2022_02.tsv FlyBaseAnnotationHelper/.
COPY data/currentDmelHsap.txt FlyBaseAnnotationHelper/.

# in input_files do
#curl https://ftp.ncbi.nlm.nih.gov/pub/pmc/PMC-ids.csv.gz --output input_files/PMC-ids.csv.gz
# gunzip PMC-ids.csv.gz
COPY data/PMC-ids.csv FlyBaseAnnotationHelper/.

ENTRYPOINT /bin/sh
# CMD ["python3", "-u", "FlyBaseAnnotationHelper/update_resources.py"]