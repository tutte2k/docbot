2. create env:
   `python -m venv rag`
3. activate env:
   `./rag/scripts/activate` (on windows)
4. install requirements:
   `pip install -r requirements.txt`
5. to populate db with json content from data folder:
   `python populate_database.py` or `python populate_database.py --reset` to reset db contents before populating
6. to query the model open the app with:
   `python main.py`
