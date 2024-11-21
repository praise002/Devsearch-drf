# DevSearch

# Features
* Share Projects
* Message other developers
* Rate others work
* Search other developers

# Tech Stack
* Django Rest Framework
* Postgres
* Docker
  
# How to run locally
* Download this repo or run: 
```bash
    $ git clone url(replace with the github url)
```

#### In the root directory:
- Create and activate a virtual environment
- Install all dependencies
```bash
    $ pip install -r requirements.txt
```
- Create an `.env` file and copy the contents from the `.env.example` to the file and set the respective values. A postgres database can be created with PG ADMIN or psql

- Run Locally
```bash
    $ python manage.py migrate
```
```bash
    $ python manage.py runserver
```

- Run With Docker
```bash
    $ docker-compose up  
```
```bash
    $ docker compose exec web python manage.py migrate
```
```bash
    $ docker compose exec web python manage.py createsuperuser
```
```bash
    $ docker-compose exec web python manage.py collectstatic
```

# API DOCS
<img src="./static/images/1-d.png">  
<img src="./static/images/2-d.png">  
<img src="./static/images/3-d.png">  
<img src="./static/images/4-d.png">  
<img src="./static/images/5-d.png">  

# Admin login
<img src="./static/images/devsearch-admin-login.png">  
v
# Admin dashboard
<img src="./static/images/devsearch-admin-dashboard-1.png">  
<img src="./static/images/devsearch-admin-dashboard-2.png">  

