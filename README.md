# Grainger Prototype
installations may be needed: 
<br><br> 
For mac, run these commands in terminal: <br>

brew install python <br>
hi 
python3 -m venv grainger-venv <br>
source grainger-venv/bin/activate <br>

pip install scikit-learn <br>

python main.py <br>

when done running: deactivate <br>
<br><br> 

## Progress so far: 
Fariha's code used arrays instead of a database, and added an entry into the array <br><br>
Kyla's code created the tables, and started the menu program options, and implemented super basic search functionality, and ability to add to the database *** <br><br> 

current program has 2 menu options: <br>
- Q - search for a question <br>
This only searches for the exact string, so if worded differently it won't show up

- A - add an entry in the question table (question/answer/grainger item #)
***The only thing with this is, should customer service reps even have this ability? Because they are not exprets? I know tech reps are supposed to fill this out so i think we should take this out

<br><br>

Shuroq added code in order to incorporate TFIDF searching, that way the user doesn't have to input the exact question in order to see if there is existence. <br>

Now we have an intelligent search algorithm in order to match queries that are being check in stored questions.  <br>

Searches are powered by TF-IDF. Users can type natural language questions, and the app returns the top 3 most similar Q&A matches from the database. <br>

- New Q&A entries auto-refresh the model. <br>
- Matching is semantic — not just keywords. <br>
- Results are sorted by confidence and shown as percentages. <br>

Example questions to try <br>
User input: "What’s the best way to use Super Adhesive?" <br>
Will match: "How do I install Super Adhesive?" <br>

<br>
User input: "Instructions for applying Waterproof Sealant" <br>
Will match: "How do I apply Waterproof Sealant" <br>

<br>
User Input: "Can this High-Temp Sealant handle extreme heat" <br>
Will match: "What the the temperature limits for High-Temp Sealant" <br>

## To Do:
- [ ] 
