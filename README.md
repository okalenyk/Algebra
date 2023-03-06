### 1. Create .env file using .env.example
Basically for local start up you can just copy the `.env.example` as it is

**For production you should change .env**:
1) set BACKEND_SETTINGS_MODE to `production`
2) set HTTP_TEMPLATE_DIR to `/etc/nginx/templates/ssl`
3) change all passwords to secure
4) change variables with host, ports, etc. as required

### 2 Place SSL certificates to the ./docker/nginx/ssl dir

**Files have to be named exactly as in `./docker/nginx/templates/ssl/[template]`**

### 3 Start the project

> docker compose -f [docker-compose_file] up --build -d

For local development you should use `docker-compose.local.yml` and for production - `docker-compose.yml` (or leave file argument empty)

### 4 Run some commands inside the Django container 

Firstly connect to the container with Django. [container] is equal to either `dev-backend` or `backend`

> docker compose -f [docker-compose_file] exec [container] bash

Then run this inside the container

> python manage.py makemigrations

After the migrations are created you have to apply them

> python manage.py migrate

Then run this command to collect static files for nginx to be able to serve them

> python manage.py collectstatic

Create a superuser to be able to access admin site 

> python manage.py createsuperuser

### 5 Add network with subhraphs

1) Go to the `[HOST]:[PORT]/admin` (if you started a local version it should be `localhost/admin`)
2) Login with the credentials that you used in the previous step
3) Go to the _Networks_ tab
4) Click _Add Network_
5) Enter the links to 3 subgraphs
6) Click _Save_

And then after some time the task are going to be run taking into the account new network

### Update tasks

Default settings are:
1) Pools APR are calculated every 1 minute
2) Farmings APR are calculated evey 1 minute

To change the schedule:
1) Go to admin site
2) Go to _Periodic tasks_ tab
3) Choose interested task
4) Change _Interval Schedule_ in the _Schedule_ section
5) If there is no required interval setting you can add it with `+` button near it
