if !(ls .venv &> /dev/null)
then
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
fi
source .venv/bin/activate
python main.py
