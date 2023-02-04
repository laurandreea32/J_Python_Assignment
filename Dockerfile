FROM python:3.8
WORKDIR /Joby_Python_Challenge
COPY ./requirements.txt /Joby_Python_Challenge/requirements.txt
RUN apt-get update && apt-get install -y iputils-ping
RUN pip install --no-cache-dir --upgrade -r /Joby_Python_Challenge/requirements.txt
COPY ./main.py /Joby_Python_Challenge/main.py
COPY ./unittests.py /Joby_Python_Challenge/unittests.py
CMD ["python3", "./main.py"]