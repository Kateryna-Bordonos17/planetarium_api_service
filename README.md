# Planetarium API Service
API Service for planetarium

## Features
- JWT authenticated
- Admin panel /admin/
- Documentation is located at /api/doc/swagger/
- Managing orders and tickets


## Installing using GitHub
Clone repository
```
git clone git@github.com:Katherine-Greg/planetarium_api_service.git
```

Setup project
```
cd planetarium_api_service

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
```

Setup your environment variables
```
set DB_HOST=<your db hostname> 
set DB_NAME=<your db name> 
set DB_USER=<your db username> 
set DB_PASSWORD=<your db user password> 
set SECRET_KEY=<your secret key>
set DEBUG=<True or False>
```

Make migrations
```
python manage.py makemigrations
python manage.py migrate
```

Run project
```
python manage.py runserver
```

## Run with Docker
Docker should be installed
```
docker-compose build
docker-compose up
```

## Getting access
```
- create user via /api/user/register/
- get access token via /api/user/token/
```

## Documentation
Swagger Documentation:
```
/api/doc/swagger/
```
## Redoc Documentation:
```
/api/doc/redoc/
```
