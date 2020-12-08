FROM python:3.6.9-stretch

# ---------------------------------------------------------------------------------------------------------------------
# Install Java
RUN apt-get update && apt-get install openjdk-8-jdk -y && apt-get clean

# ---------------------------------------------------------------------------------------------------------------------
# Install Cytomine python client
RUN git clone https://github.com/cytomine-uliege/Cytomine-python-client.git
RUN cd /Cytomine-python-client && git checkout tags/v2.7.3 && pip install .
RUN rm -r /Cytomine-python-client

# ---------------------------------------------------------------------------------------------------------------------
# Install Icy.
RUN apt-get update && apt-get install -y unzip wget && \
    mkdir -p /icy && \
    cd /icy && \
    wget -O icy.zip https://zenodo.org/record/3562103/files/icy_1.9.9.1_with_plugins.zip?download=1 && \
    unzip icy.zip && \
    rm -rf icy.zip

# Add icy to the PATH
ENV PATH $PATH:/icy

RUN mkdir -p /icy/data/in && \
        mkdir -p /icy/protocols

RUN chmod -R a+rwx /icy 
# ---------------------------------------------------------------------------------------------------------------------
# Install Neubias-W5-Utilities (annotation exporter, compute metrics, helpers,...)
RUN apt-get update && apt-get install libgeos-dev -y && apt-get clean
RUN git clone https://github.com/Neubias-WG5/biaflows-utilities.git && \
    cd /biaflows-utilities/ && git checkout tags/v0.9.1 && pip install .

# install utilities binaries
RUN chmod +x /biaflows-utilities/bin/*
RUN cp /biaflows-utilities/bin/* /usr/bin/

# cleaning
RUN rm -r /biaflows-utilities

# ---------------------------------------------------------------------------------------------------------------------
# Install Protocol
ADD protocol.protocol /icy/protocols/protocol.protocol
ADD wrapper.py /app/wrapper.py

# for running the wrapper locally
ADD descriptor.json /app/descriptor.json

ENTRYPOINT ["python", "/app/wrapper.py"]
