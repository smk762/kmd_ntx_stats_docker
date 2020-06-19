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

sudo apt-get install
# Clone repo
`git clone https://github.com/smk762/kmd_ntx_stats_docker`
`cd kmd_ntx_stats_docker`

Install Python Packages: `pip3 install -r requirements.txt` 
`sudo docker-compose build`  (needs to be run to apply code changes)
`sudo docker-compose up` (run to launch containers)

# Setup
- update settings.py (secret key, pgsql auth, allowed hosts)
- setup .env files (script pending...)


more to come... (need details on overcoming pgsql connection issues - important to setup .env!)
