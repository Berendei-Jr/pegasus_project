if !(ls .venv &> /dev/null)
then
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
fi
python main.py
