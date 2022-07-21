# Dependancies:

- NGINX:  https://www.digitalocean.com/community/tutorials/how-to-install-nginx-on-ubuntu-18-04

- Docker: https://docs.docker.com/engine/install/ubuntu/

- Docker Compose: https://docs.docker.com/compose/install/

- Certbot: https://certbot.eff.org/lets-encrypt/ubuntubionic-nginx.html

- Git: `sudo apt install git`

- PostgreSQL: https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-ubuntu-18-04

- Komodod - https://github.com/komodoplatform/komodo (you can use bootstrap from https://www.dexstats.info/bootstrap.php to speed things up)

- Pip3: `sudo apt install python3-pip` then `pip3 install --upgrade setuptools wheel`

- Psychpg2 `sudo apt-get install python-psycopg2` then `sudo apt-get install python3-dev build-essential libpq-dev  libgnutls28-dev gcc`

- mysql-client / connector `sudo apt-get install default-libmysqlclient-dev build-essential python3-mysql.connector`


# Clone repo
`git clone https://github.com/smk762/kmd_ntx_stats_docker`

`cd kmd_ntx_stats_docker`
 
Install Python Packages: `pip3 install -r requirements.txt` 

`sudo docker-compose build`  (needs to be run to apply code changes)

`sudo docker-compose up` (run to launch containers)

# Setup .env files (scripts pending...)
- pgsql credentials

- django secret key

- allowed hosts

# Create Database Tables

Make migrations: `"docker-compose run web python3 manage.py makemigrations"`

Apply migrations: `"docker-compose run web python3 manage.py migrate"`

Collect static files: `"docker-compose run web python3 manage.py collectstatic"`

See https://docs.djangoproject.com/en/3.0/ref/django-admin/ for more django admin commands.

# Applying code changes
`cd ~/kmd_ntx_stats_docker`

`docker-compose build`

`sudo chown $USER:$USER /home/$USER/kmd_ntx_stats_docker/postgres-data -R`

`docker-compose build`

`sudo cp -R static /var/www/stats.kmd.io/html`

# Adding new coins

add coin parmas to `scripts/base_58.py`

run `scripts/populate_coins_table.py`

run `scripts/populate_balances_table.py`

run `scripts/populate_addresses_table.py`

Check web pages to confirm display / no errors.
