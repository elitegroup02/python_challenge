# python_challenge

Python script that parses ips from a file in order to get RDAP and GEO data of them

## Setup
pip install virtualenv (if you don't already have virtualenv installed)
virtualenv python_challenge (creates a virtual env called 'python_challenge')
source python_challenge/bin/activate (to enter the virtual environment)
pip install -r requirements.txt

## Run
On your terminal: `python main.py $FILE_WITH_IPS` (a file called 'list_of_ips.txt' is included in this repo)

## Notes:
The file `output.json` will be created containing the lookup result
The file `http_cache.sqlite` will be created to cache http requests
