FROM python:3
WORKDIR /usr/src/app

## Install packages
RUN apt-get update
RUN apt-get install -y vim
COPY requirements.txt ./ 
RUN pip3 install -r requirements.txt
COPY UserService .
EXPOSE 8000
CMD ["python", "manage.py", "runsslServer", "--host=0.0.0.0", "-p 8000"] 
# CMD ["gunicorn", "--workers=5" ,"--bind", "0.0.0.0:8000", "UserService.wsgi:application"]