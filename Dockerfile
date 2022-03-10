FROM pennsive/neuror:latest
WORKDIR /opt/pennsivepype
COPY . .
RUN pip3 install .
# docker build -t pennsive/pennsivepype:latest .