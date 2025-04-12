import sqlite3
# Vectorize all question texts using TF-IDF, imports and global variables 
from sklearn.feature_extraction.text import TfidfVectorizer 
from sklearn.metrics.pairwise import cosine_similarity
vectorizer = None
tfidf_matrix = None
rows = None

# This function creates the dummy data we are going to use for the demo.
#  right now its super simple for testing but we can make it closer to the info they have on their catalog later
def create_example_data(conn):
    cursor = conn.cursor()
    # Drop tables if they already exist (for demo purposes)
    cursor.execute("DROP TABLE IF EXISTS Product")
    cursor.execute("DROP TABLE IF EXISTS Question")

    # Create Product table
    cursor.execute('''
        CREATE TABLE Product (
            g_item_no INTEGER PRIMARY KEY,
            mfr_model INTEGER,
            product_name VARCHAR(255),
            brand_series VARCHAR(100),
            color VARCHAR(50),
            finishing_features VARCHAR(50),
            container_type VARCHAR(50),
            container_size VARCHAR(100),
            working_time VARCHAR(100),
            working_time_type VARCHAR(50),
            product_use VARCHAR(100)
            
        )
    ''')

    # Create Question table with a foreign key to Product table
    cursor.execute('''
        CREATE TABLE Question (
            question_id INTEGER PRIMARY KEY,
            g_item_no INTEGER,
            question_text VARCHAR(255),
            answer_text VARCHAR(255),
            FOREIGN KEY (g_item_no) REFERENCES Product(g_item_no)
        )
    ''')

    # Insert dummy data into the Product table
    products = [
        (1001, 12345, 'Super Adhesive', 'UltraBond Series', 'Red', 'Matte', 'Tube', '50ml', '30', 'minutes', 'Industrial use'),
        (1002, 67890, 'Waterproof Sealant', 'SealPro Series', 'Blue', 'Glossy', 'Bottle', '100ml', '45', 'minutes', 'Building and construction'),
        (1003, 54321, 'High-Temp Sealant', 'HeatShield Series', 'Yellow', 'Satin', 'Cartridge', '200ml', '60', 'minutes', 'Automotive')
    ]
    cursor.executemany('''
        INSERT INTO Product 
        (g_item_no, mfr_model, product_name, brand_series, color, finishing_features, container_type, container_size, working_time, working_time_type, product_use)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', products)

    # Insert dummy data into the Question table
    questions = [
        (1, 1001, 'How do I install Super Adhesive?', 'Clean the surface, apply the adhesive evenly, and allow it to cure for 30 minutes.'),
        (2, 1002, 'How do I apply Waterproof Sealant?', 'Ensure surfaces are dry, apply a thin layer, and let dry for 45 minutes.'),
        (3, 1003, 'What are the temperature limits for High-Temp Sealant?', 'This sealant is rated for use up to 500°F.')
    ]
    cursor.executemany('''
        INSERT INTO Question (question_id, g_item_no, question_text, answer_text)
        VALUES (?, ?, ?, ?)
    ''', questions)

    conn.commit()



# This function allows the user to search for questions in the question table, and returns the answer
#def search_questions(conn, search_query):
    #cursor = conn.cursor()
    #sql = """
        #SELECT q.question_text, q.answer_text, p.product_name 
        #FROM Question AS q
        #JOIN Product AS p ON q.g_item_no = p.g_item_no
        #WHERE q.question_text LIKE ?
    #"""
    #cursor.execute(sql, ('%' + search_query + '%',))
    #return cursor.fetchall()


#  This function adds an entry to the question table
#  NOTE: should we have this functionality? Because how do we even know the question is right? Shouldn't only tech reps
#    be able to add questions?
def insert_q_and_a(conn, question, answer, product_id):
    # find product id, if product doesn't exist, exit
    cursor = conn.cursor()
    cursor.execute("SELECT g_item_no FROM Product WHERE g_item_no = ?", (product_id,))
    row = cursor.fetchone()
    if row is None:
        print(f"Product '{product_id}' not found!")
        return
    else:
        g_item_no = row[0]

    # check for duplicate questions. if duplicate, exit
    cursor.execute(
        "SELECT question_id FROM Question WHERE g_item_no = ? AND LOWER(question_text) = LOWER(?)",
        (g_item_no, question)
    )
    duplicate = cursor.fetchone()
    if duplicate is not None:
        print("This question already exists for the product.")
        return

    # Now, insert the new question and answer into the Question table.
    sql = "INSERT INTO Question (g_item_no, question_text, answer_text) VALUES (?, ?, ?)"
    cursor.execute(sql, (g_item_no, question, answer))
    conn.commit()
    print("New question and answer have been inserted successfully.")

#function that will use the tfidf protocal that will use cosine simalarity in order to find similar matches over 30%.
# def tfidf_search(user_input, question_texts, tfidf_matrix):
#     user_vec = vectorizer.transform([user_input]) #vectorizing the data
#     similarities = cosine_similarity(user_vec, tfidf_matrix) #cosine simalarity
#     best_match_idx = similarities.argmax() #sorts the indexes by best match
#     best_score = similarities[0, best_match_idx] #simalarity scores

#     if best_score > 0.3:  # we can change this but I did above 30% for now. 
#         return rows[best_match_idx]
#     else:
#         return None
def tfidf_search_all(user_input, question_texts, tfidf_matrix, threshold=0.2):
    user_vec = vectorizer.transform([user_input])
    similarities = cosine_similarity(user_vec, tfidf_matrix)[0]

    # Pair each similarity score with the corresponding row index
    scored_matches = [(i, score) for i, score in enumerate(similarities) if score > threshold]

    # Sort by score descending
    scored_matches.sort(key=lambda x: x[1], reverse=True)

    # Return a list of tuples: (question_text, answer_text, product_id, similarity)
    results = []
    for i, score in scored_matches:
        question_text, answer_text, product_id = rows[i][1], rows[i][2], rows[i][3]
        results.append((question_text, answer_text, product_id, score))

    return results

def main():
    global vectorizer, tfidf_matrix, rows #global variables to allow the search and save. 

    # Connect to an in-memory SQLite database using sqlite3
    # This is so that you start with a clean slate every time you run the code
    conn = sqlite3.connect(":memory:")
    # Create tables and dummy data
    create_example_data(conn)
    cursor = conn.cursor()

    #gets existing questions from the database in order to build the tfidf model (may need to tweak the code in order to do this after questions are added )
    cursor.execute("SELECT question_id, question_text, answer_text, g_item_no FROM Question")
    rows = cursor.fetchall()
    #vectorization 
    question_texts = [row[1] for row in rows]
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(question_texts)
    
    # program menu (we can add more commands here if we need)
    print("Grainger Product Guide\n" +
          "Q - Question lookup\n" +
          "A - Add a question\n")

    # loop for keeping the program running
    while True:
        # enter a command from the main menu
        command = input("\nEnter your command (or type 'exit' to quit): ")
        command = command.strip().lower()
        if command == 'exit':
            break

        print("You entered: " + command + "\n")

        # SEARCH A QUESTION
        if command == 'q':
            while True:
                user_query = input("\nEnter your question: (or type 'exit' to quit): ")

                if user_query == 'exit':
                    break
                # result = tfidf_search(user_query, question_texts, tfidf_matrix)
                # if result:
                #     question_text, answer_text, product_id = result[1], result[2], result[3]
                #     cursor.execute("SELECT product_name FROM Product WHERE g_item_no = ?", (product_id,))
                #     product_name = cursor.fetchone()[0]
                #     print(f"\nProduct: {product_name}")
                #     print(f"Question: {question_text}")
                #     print(f"Answer: {answer_text}")
                #     print("-" * 40)
                # else:
                #     print("No matching questions found. Consider adding this as new data if it's a common query.")
                results = tfidf_search_all(user_query, question_texts, tfidf_matrix)
                if results:
                    for question_text, answer_text, product_id, score in results[:3]:
                        cursor.execute("SELECT product_name FROM Product WHERE g_item_no = ?", (product_id,))
                        product_name = cursor.fetchone()[0]
                        print(f"\nProduct: {product_name}")
                        print(f"Question: {question_text}")
                        print(f"Answer: {answer_text}")
                        print(f"Similarity: {score * 100:.1f}%")
                        print("-" * 40)
                        print()
                else:
                    print("No matching questions found.")

        # ADD A QUESTION/ANSWER COMBO *see note at the beginning of this function - not sure if we should have this functionality*
        if command == 'a':
            user_question = input("\nEnter the question to add: ")
            user_answer = input("\nEnter the answer: ")
            user_p_id = input("\nEnter the product id (only numbers): ")

            insert_q_and_a(conn, user_question, user_answer, user_p_id)
            cursor.execute("SELECT question_id, question_text, answer_text, g_item_no FROM Question")
            rows = cursor.fetchall()  # Update global rows
            question_texts = [row[1] for row in rows]
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform(question_texts)

            print("TF-IDF model updated with new question.\n")
            continue


    # close the program
    conn.close()



if __name__ == "__main__":
    main()



# /* FARIHA'S CODE */

# productIDList = ["35JE49", "796P22", "1234"]
#
# #https://www.grainger.com/product/FULHAM-Fluorescent-Ballast-120V-AC-35JE49
# #https://www.grainger.com/product/PHILIPS-Compact-LED-Bulb-LED-796P22
# #
# questionList = [["Is the Fulham flourescent ballast compatible with an F14T5 type of lamp?", "How would I install this flourescent ballast?", "How does this ballast compare to other ballasts on the market?"],
#                 ["What is the current for this light", "How would I install this light?", "How does this light compare to other lights on the market?"], ["xyz", "abc"]]
# answerList = [["Yes, it is compatible with this type of lamp", "Here is a guide of steps: ", "It has more wattage and is compatible with a variety of lamps"],
#               ["65 mA", "Here is a guide of steps: ", "It is shatter resistant and frosted"],
#               ["abx", "def"]]
#
# # get input product ID from user
# inputProductID = input("Enter the productID: ")
# inputProductID = inputProductID.strip() #trim leading and trailing whitespace
#
# # check if product is already in database, if not add it to database
# if inputProductID in productIDList:
#     index = productIDList.index(inputProductID)
#     print("Product found in database...")
# else:
#     index = len(productIDList) - 1
#     print("Product not found in database...Adding...")
#
#
# # get inputs for questions
# inputQuestion = input("Enter the question the customer asked: ")
# inputAnswer = input("Enter the answer you gave: ")
#
# #append at the end of the sublist absed on index
# questionList[index].append(inputQuestion)
# answerList[index].append(inputAnswer)
#
#
# #testing to see if appended properly
# for ans in answerList[index]:
#     print(ans)

