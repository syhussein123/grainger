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


## Kyla's update: upvote functionality
C:\Users\kgonza39\AppData\Local\anaconda3\python.exe C:\Users\kgonza39\PycharmProjects\grainger\main.py 
Grainger Product Guide
Q - Question lookup
P - View all question/answer pairs
E - Exit

Enter command: q

Enter your question (or type 'exit' to return to main menu): how install

Product: Super Adhesive
Question: How do I install Super Adhesive?
Answer: Clean the surface, apply the adhesive evenly, and allow it to cure for 30 minutes.
Additional Info:
 • [2] Clamp joints during curing for best bond strength.  (upvotes: 0)
 • [3] Use a primer on porous surfaces before applying the adhesive.  (upvotes: 0)
 • [4] Store unused adhesive in a cool, dry place to extend shelf life.  (upvotes: 0)
Similarity: 61.6%
..... MORE OUTPUT HERE

the number next to the additional info answer is the answer id, so when this is prompted:

Enter 'u <answer_id>' to upvote, 'f <answer_id>' to flag, or press Enter to new query:

and if you want to upvote answer 2, you just type in "u 2":
Answer 2 upvoted! New score: 1

Product: Super Adhesive
Question: How do I install Super Adhesive?
Answer: Clean the surface, apply the adhesive evenly, and allow it to cure for 30 minutes.
Additional Info:
 • [2] Clamp joints during curing for best bond strength.  (upvotes: 1) ----- SEE THE UPDATED UPVOTE HERE
 • [3] Use a primer on porous surfaces before applying the adhesive.  (upvotes: 0)
 • [4] Store unused adhesive in a cool, dry place to extend shelf life.  (upvotes: 0)
Similarity: 61.6%

then it will show the update. If you keep upvoting 4 for example, you'll see it move up the list the next time it is output. If you want to enter a new question just press enter without typing anything and you can enter another question


## To Do:
- [ ] 
