FROM python:2

WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5002
CMD [ "python", "./Accounts/routes.py" ]
