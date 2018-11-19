FROM python:3.6.1
MAINTAINER Jay Luo <jayluo9410@gmail.com>

# Create the group and user to be used in this container (read-only)
WORKDIR /home/flask/app/backend

RUN groupadd flaskgroup && useradd -m -g flaskgroup -s /bin/bash flask \
    && chown -R flask:flaskgroup /home/flask

# Install the package dependencies
COPY ./backend/requirements.txt /home/flask/app/backend/
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the source code into the container
COPY ./backend/ /home/flask/app/backend/

# After installing everthing, switch to right user
USER flask
