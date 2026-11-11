## clone repo
// credentials go in .env (see .env.example), never in code


git clone https://github.com/eliwerstler/DBProj3.git
cd DBProj3

## Connect to VM
gcloud compute ssh cs4111-instance
cd ~/DBProj3

## environment
source venv/bin/activate

## dependencies
pip install flask sqlalchemy psycopg2-binary click


