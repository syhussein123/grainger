import sqlite3
import json
import re

# Vectorize all question texts using TF-IDF, imports and global variables 
from sklearn.feature_extraction.text import TfidfVectorizer 
from sklearn.metrics.pairwise import cosine_similarity
vectorizer = None
tfidf_matrix = None
rows = None


def parse_json_transcript(file_path):

    records = []
    current_product_id = None
    qa_pending = None

    with open(file_path, "r", encoding="utf-8") as f:
        transcript_data = json.load(f)

    for result in transcript_data.get("results", []):
        alt = result.get("alternatives", [])[0]
        utterance = alt.get("transcript", "").strip()

        # Look for a product ID mention in the utterance.
        prod_id_match = re.search(r'product\s*ID\s*([0-9]+)', utterance, re.IGNORECASE)
        if prod_id_match:
            current_product_id = prod_id_match.group(1)

        # Identify a Customer question.
        if utterance.startswith("Customer:"):
            text = utterance.split("Customer:")[-1].strip()
            if text.endswith('?'):
                qa_pending = {"product_id": current_product_id, "question": text}

        # Look for an Agent answer following a Customer question.
        elif utterance.startswith("Agent:"):
            text = utterance.split("Agent:")[-1].strip()
            if qa_pending and text:
                qa_pending["answer"] = text
                records.append(qa_pending)
                qa_pending = None

    return records


def review_and_edit_records(records):
    """
    Provides a CLI-based interface for the agent to review and optionally edit the extracted records.
    """
    print("\nReview the extracted Q&A records:\n")
    for idx, record in enumerate(records, start=1):
        print(f"Record {idx}:")
        print(f"  Product ID: {record['product_id']}")
        print(f"  Question  : {record['question']}")
        print(f"  Answer    : {record['answer']}")
        while True:
            edit_option = input("Do you want to edit this record? (y/n): ").strip().lower()
            if edit_option == 'y':
                field = input("Which field do you want to edit? (product/question/answer): ").strip().lower()
                if field in ["product", "question", "answer"]:
                    new_val = input(f"Enter new value for {field}: ").strip()
                    if field == "product":
                        record["product_id"] = new_val
                    elif field == "question":
                        record["question"] = new_val
                    elif field == "answer":
                        record["answer"] = new_val
                    print("Updated record:")
                    print(f"  Product ID: {record['product_id']}")
                    print(f"  Question  : {record['question']}")
                    print(f"  Answer    : {record['answer']}")
                else:
                    print("Invalid field. Please choose product, question, or answer.")
            elif edit_option == 'n':
                break
            else:
                print("Please enter 'y' or 'n'.")
        print("\n")
    return records


def get_existing_connection(db_path="qa.db"):
    """
    Opens a connection to the existing database that already includes the Product and Question tables.
    Update db_path with your actual database file.
    """
    try:
        conn = sqlite3.connect(db_path)
        return conn
    except Exception as e:
        print("Error connecting to the database:", e)
        return None

def insert_question_records(conn, records):
    """
    Inserts each Q&A record into the existing Question table.
    Assumes that the extracted product_id corresponds to the Product.g_item_no.
    """
    cursor = conn.cursor()
    for rec in records:
        try:
            # Convert product_id to integer to match g_item_no type.
            g_item_no = int(rec["product_id"])
        except ValueError:
            print(f"Invalid product id found: {rec['product_id']} in record {rec}")
            continue

        cursor.execute('''
            INSERT INTO Question (g_item_no, question_text, answer_text)
            VALUES (?, ?, ?)
        ''', (g_item_no, rec["question"], rec["answer"]))
    conn.commit()




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


def print_all_questions(conn):
    """
    Prints all rows from the Question table in the connected SQLite database.

    The function queries for question_id, g_item_no, question_text, and answer_text,
    then prints them with headers.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT question_id, g_item_no, question_text, answer_text FROM Question")
    rows = cursor.fetchall()

    if rows:
        header = f"{'Question ID':<12} {'Product ID':<10} {'Question':<50} {'Answer':<50}"
        print(header)
        print("-" * len(header))
        for question_id, product_id, question_text, answer_text in rows:
            print(f"{question_id:<12} {product_id:<10} {question_text:<50} {answer_text:<50}")
    else:
        print("No questions found in the database.")

#  This function adds an entry to the question table
# def insert_q_and_a(conn, question, answer, product_id):
#     # find product id, if product doesn't exist, exit
#     cursor = conn.cursor()
#     cursor.execute("SELECT g_item_no FROM Product WHERE g_item_no = ?", (product_id,))
#     row = cursor.fetchone()
#     if row is None:
#         print(f"Product '{product_id}' not found!")
#         return
#     else:
#         g_item_no = row[0]
#
#     # check for duplicate questions. if duplicate, exit
#     cursor.execute(
#         "SELECT question_id FROM Question WHERE g_item_no = ? AND LOWER(question_text) = LOWER(?)",
#         (g_item_no, question)
#     )
#     duplicate = cursor.fetchone()
#     if duplicate is not None:
#         print("This question already exists for the product.")
#         return
#
#     # Now, insert the new question and answer into the Question table.
#     sql = "INSERT INTO Question (g_item_no, question_text, answer_text) VALUES (?, ?, ?)"
#     cursor.execute(sql, (g_item_no, question, answer))
#     conn.commit()
#     print("New question and answer have been inserted successfully.")




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
          "A - Add a question\n" +
          "P - View all question/answer pairs\n")

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

        # TECH REP OPTION
        # agent logs in and presses a to initiate transcript processing
        # system prompts agent to select json file (transcript)
        # file path is processed
        # All this would happen automatically in real world application after agent hangs up the phone

        # once file is processed and q and a pairs are extracted, agent can review
        # agent modifies it if needed
        # after agent confirms, it is added to the database
        if command == 'a':
            file_path = input("Enter the path to the JSON transcript file: ").strip()
            try:
                records = parse_json_transcript(file_path)
                if not records:
                    print("No Q&A pairs were found in the transcript.")
                    return
                records = review_and_edit_records(records)

                print("Final Q&A entries:")
                for idx, rec in enumerate(records, start=1):
                    print(f"{idx}. Product ID: {rec['product_id']} | Question: {rec['question']} | Answer: {rec['answer']}")
                confirm = input("Are you happy with these entries? (y/n): ").strip().lower()
                if confirm == 'y':
                    insert_question_records(conn, records)

                else:
                    print("Record insertion canceled.")
            except FileNotFoundError:
                print("The file was not found. Please check the path and try again.")
            except json.JSONDecodeError:
                print("There was an error parsing the JSON file. Please ensure the file is in proper JSON format.")

            # user_question = input("\nEnter the question to add: ")
            # user_answer = input("\nEnter the answer: ")
            # user_p_id = input("\nEnter the product id (only numbers): ")
            #
            # insert_q_and_a(conn, user_question, user_answer, user_p_id)
            # cursor.execute("SELECT question_id, question_text, answer_text, g_item_no FROM Question")
            # rows = cursor.fetchall()  # Update global rows
            # question_texts = [row[1] for row in rows]
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform(question_texts)
            #
            print("TF-IDF model updated with new question.\n")
            continue

        if command == 'p':
            print_all_questions(conn)
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

