## clone repo
// make sure server.py has the below code in it else clone
DATABASE_USERNAME = "pjm2188"
DATABASE_PASSWRD = quote_plus("Peterpeter01!")
DATABASE_HOST = "34.139.8.30"
DATABASEURI = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWRD}@{DATABASE_HOST}/proj1part2"


git clone https://github.com/eliwerstler/DBProj3.git
cd DBProj3

## Connect to VM
gcloud compute ssh cs4111-instance
cd ~/DBProj3

## environment
source venv/bin/activate

## dependencies
pip install flask sqlalchemy psycopg2-binary click


