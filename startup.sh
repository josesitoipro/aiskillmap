python -m venv antenv
source antenv/bin/activate
pip install -r requirements.txt
gunicorn project.wsgi --bind=0.0.0.0 --timeout 600
