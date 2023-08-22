FROM ubuntu:22.04

# RUN apt-get install libressl-dev
RUN apt-get update
RUN apt-get -y install libssl-dev python3 python3-dev python3-pip
RUN apt-get -y install wget curl git g++ cargo openssl pkg-config git-lfs
RUN apt-get -y install postgresql-client libpq-dev
# RUN apt-get -y install postgresql postgresql-client
RUN env

RUN python3 --version

WORKDIR /usr/src/app

COPY . .

RUN find / -name .cargo -print
RUN which cargo

RUN cargo --version

RUN rustc --version

RUN pip install --upgrade pip

RUN git lfs install --force

RUN git clone https://github.com/grivaz/FlyBaseAnnotationHelper.git

RUN cp /usr/src/app/config.ini /usr/src/app/FlyBaseAnnotationHelper/config/config.ini

WORKDIR /usr/src/app/FlyBaseAnnotationHelper

RUN git lfs install

RUN git clone https://huggingface.co/cgrivaz/FlyBaseGeneAbstractClassifier.git

WORKDIR /usr/src/app

# RUN echo $PWD
RUN pip install --prefer-binary -r requirements.txt

RUN pip3 install torch --index-url https://download.pytorch.org/whl/cpu
# pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# TODO Add this step to the GoCD pipeline.
#curl https://ftp.ncbi.nlm.nih.gov/pub/pmc/PMC-ids.csv.gz --output input_files/PMC-ids.csv.gz
# gunzip PMC-ids.csv.gz

ENTRYPOINT /bin/sh
# CMD ["python3", "-u", "FlyBaseAnnotationHelper/update_resources.py"]