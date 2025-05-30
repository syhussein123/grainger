import sqlite3
import json
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

vectorizer = None
tfidf_matrix = None
rows = None  # will hold (question_id, question_text, answer_text, g_item_no) → we’ll reshape this

def parse_json_transcript(file_path):
    # list to store q and a dictionaries
    records = []
    current_product_id = None
    qa_pending = None

    with open(file_path, "r", encoding="utf-8") as f:
        transcript_data = json.load(f)
    for result in transcript_data.get("results", []):
        alt = result.get("alternatives", [])[0]
        utterance = alt.get("transcript", "").strip()

        # Look for a product ID pattern
        prod_id_match = re.search(r'product\s*ID\s*([0-9]+)', utterance, re.IGNORECASE)
        if prod_id_match:
            current_product_id = prod_id_match.group(1)

        # Identify a Customer question.
        if utterance.startswith("Customer:"):
            text = utterance.split("Customer:")[-1].strip()
            if text.endswith('?'):
                # qa_pending = {"product_id": current_product_id, "question": text}
                qa_pending = {
                    "product_id": current_product_id,
                    "question": text,
                    "answer": None,
                    "additional_answers": []
                }

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
                print()
                print("You Can: \n -Update Product ID \n -Update Question \n -Update Answer \n -Add Additional Information \n -Append Important Information to Current Answer")
                print()
                field = input("Which field? (product/question/answer/add/append):").strip().lower()
                if field in ["product", "question", "answer"]:
                    new_val = input(f"Enter new value for {field}: ").strip()
                    if field == "product":
                        record["product_id"] = new_val
                    elif field == "question":
                        record["question"] = new_val
                    else:  # answer
                        record["answer"] = new_val
                elif field == "add":
                    extra = input("Enter ADDITIONAL info to add: ").strip()
                    record["additional_answers"].append(extra)
                elif field == "append":
                    more_text = input("Enter the text to append to the main answer: ").strip()
                    if record["answer"]:
                        record["answer"] += " " + more_text
                    else:
                        record["answer"] = more_text
                    print("Updated main answer after appending:")
                    print(f"  {record['answer']}")
                else:
                    print("Invalid choice. Use product, question, answer, or add.")
                    continue

                # reprint the updated record:
                print("Updated record:")
                print(f"  Product ID: {record['product_id']}")
                print(f"  Question  : {record['question']}")
                print(f"  Primary   : {record['answer']}")
                if record["additional_answers"]:
                    print("  Extras  :")
                    for extra in record["additional_answers"]:
                        print(f"    - {extra}")
                else:
                    print("Invalid field. Please choose product, question, or answer.")
            elif edit_option == 'n':
                break
            else:
                print("Please enter 'y' or 'n'.")
        print("\n")
    return records

def insert_question_records(conn, records):
    """
    Inserts each record into Question + Answer.
    Stores the one primary answer, then any additional_answers as non-primary.
    """
    cursor = conn.cursor()
    for rec in records:
        try:
            g_item_no = int(rec["product_id"])
        except ValueError:
            print(f"Invalid product id: {rec['product_id']}")
            continue

        # 1) Insert the question
        cursor.execute(
            "INSERT INTO Question (g_item_no, question_text) VALUES (?, ?)",
            (g_item_no, rec["question"])
        )
        qid = cursor.lastrowid

        # 2) Insert the primary answer
        cursor.execute(
            "INSERT INTO Answer (question_id, answer_text, is_primary) VALUES (?, ?, 1)",
            (qid, rec["answer"])
        )

        # 3) Insert any additional answers
        for extra in rec.get("additional_answers", []):
            cursor.execute(
                "INSERT INTO Answer (question_id, answer_text, is_primary) VALUES (?, ?, 0)",
                (qid, extra)
            )

    conn.commit()


def create_example_data(conn):
    cursor = conn.cursor()
    # Drop tables if they already exist
    cursor.execute("DROP TABLE IF EXISTS Product")
    cursor.execute("DROP TABLE IF EXISTS Question")
    cursor.execute("DROP TABLE IF EXISTS Answer")

    # 1) Product table (unchanged)
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

    # 2) Question table
    cursor.execute('''
    CREATE TABLE Question (
      question_id INTEGER PRIMARY KEY,
      g_item_no    INTEGER,
      question_text VARCHAR(255),
      FOREIGN KEY (g_item_no) REFERENCES Product(g_item_no)
    )
    ''')

    # 3) Answer table
    cursor.execute('''
    CREATE TABLE Answer (
      answer_id   INTEGER PRIMARY KEY,
      question_id INTEGER,
      answer_text TEXT,
      is_primary  BOOLEAN DEFAULT 0,
      upvotes     INTEGER DEFAULT 0,
      FOREIGN KEY (question_id) REFERENCES Question(question_id)
    )
    ''')

    # --- dummy data ---
    products = [
        (1001, 12345, 'Super Adhesive',   'UltraBond Series', 'Red',    'Matte', 'Tube',     '50ml',  '30', 'minutes', 'Industrial use'),
        (1002, 67890, 'Waterproof Sealant','SealPro Series',   'Blue',   'Glossy','Bottle',   '100ml', '45', 'minutes', 'Building & construction'),
        (1003, 54321, 'High-Temp Sealant','HeatShield Series', 'Yellow', 'Satin', 'Cartridge', '200ml', '60', 'minutes', 'Automotive')
    ]
    cursor.executemany('''
      INSERT INTO Product
      (g_item_no, mfr_model, product_name, brand_series, color,
       finishing_features, container_type, container_size,
       working_time, working_time_type, product_use)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', products)

    # questions
    questions = [
        # Question 1: Damp surfaces
        (1, 1001, 'Is this adhesive safe to use on damp wood or concrete?'),
        # Question 2: Fume exposure
        (2, 1001, 'Does this adhesive release harmful fumes during curing on wood?'),
        # Question 3: Enclosed spaces
        (3, 1001, 'Can this product be applied in enclosed spaces without ventilation?'),
        # You could add more safety questions here, e.g.:
        # (4, 1001, 'Is it safe to use this adhesive around children or pets?'),
        # (5, 1001, 'Is this product flammable or heat-sensitive?'),
    ]



    cursor.executemany('''
      INSERT INTO Question (question_id, g_item_no, question_text)
      VALUES (?, ?, ?)
    ''', questions)

    # answers: one primary per qid plus three “additional info” each
    answers = [
        # Q1: Damp surfaces
        (1, 1,
          'Yes, most construction adhesives are moisture-resistant, but for optimal strength, surfaces should be as dry as possible.', 1),
        (2, 1,
          'Applying on damp surfaces may extend cure time; ensure surfaces are at least surface-dry before use.', 0),
        (3, 1,
          'Pre-treat very porous materials (like untreated wood) with a primer to improve bonding.', 0),
        (4, 1,
          'Avoid applying below 40°F (4°C), as low temperatures can significantly slow curing.', 0),

        # Q2: Fume exposure
        (5, 2,
          'The adhesive emits minimal VOCs during curing, but you should always work in a well-ventilated area.', 1),
        (6, 2,
          'Wearing a respirator and gloves further reduces inhalation and skin-contact risks.', 0),
        (7, 2,
          'Refer to the Safety Data Sheet (SDS) for full details on chemical exposure limits.', 0),
        (8, 2,
          'Keep containers tightly sealed when not in use to limit any off-gassing.', 0),

        # Q3: Enclosed spaces
        (9, 3,
          'Ventilation is strongly recommended; use fans or open windows to maintain air flow.', 1),
        (10, 3,
         'Avoid confined spaces without airflow—fume buildup can cause headaches or drowsiness.', 0),
        (11, 3,
         'Take regular breaks outside the work area to minimize long-term exposure.', 0),
        (12, 3,
         'Always comply with local occupational health and safety guidelines when using indoors.', 0),

    ]
    cursor.executemany('''
      INSERT INTO Answer (answer_id, question_id, answer_text, is_primary)
      VALUES (?, ?, ?, ?)
    ''', answers)

    conn.commit()

def tfidf_search_all(user_input, question_texts, tfidf_matrix, threshold=0.2):
    """
    Returns a list of (question_id, question_text, g_item_no, similarity)
    for all questions whose TF-IDF similarity > threshold.
    """
    user_vec = vectorizer.transform([user_input])
    sims = cosine_similarity(user_vec, tfidf_matrix)[0]

    matches = [(i, score) for i, score in enumerate(sims) if score > threshold]
    matches.sort(key=lambda x: x[1], reverse=True)

    results = []
    for idx, score in matches:
        qid, qtext, gid = rows[idx]
        results.append((qid, qtext, gid, score))
    return results

def print_all_qas(conn):
    """
    Prints all Q&As in columns: Question ID | Product ID | Question | Answer
    with primary answers first, then extras (upvotes DESC, answer_id ASC).
    """
    cursor = conn.cursor()
    cursor.execute('''
      SELECT
        q.question_id AS QID,
        q.g_item_no   AS PID,
        q.question_text AS Question,
        a.answer_text   AS Answer
      FROM Question q
      JOIN Answer   a ON q.question_id = a.question_id
      ORDER BY
        q.question_id,
        a.is_primary  DESC,
        a.upvotes     DESC,
        a.answer_id   ASC
    ''')
    rows = cursor.fetchall()

    if not rows:
        print("No Q&A entries found.")
        return

    header = f"{'QID':<5} {'PID':<5} {'Question':<50} {'Answer':<50}"
    print(header)
    print("-" * len(header))
    for qid, pid, qtext, atext in rows:
        print(f"{qid:<5} {pid:<5} {qtext:<50} {atext:<50}")
    print()

def main():
    global vectorizer, tfidf_matrix, rows

    conn = sqlite3.connect(":memory:")
    create_example_data(conn)
    cursor = conn.cursor()

    # Define product categories and associated product IDs
    categories = {
        "adhesives": set(range(1000, 1006)),
        "safety":    set(range(2000, 2006)),
        "light":     set(range(3000, 3006)),
    }

    # Build the TF‑IDF model
    cursor.execute("SELECT question_id, question_text, g_item_no FROM Question")
    rows = cursor.fetchall()
    question_texts = [r[1] for r in rows]
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(question_texts)

    while True:
        print()
        print("Grainger Product Guide\n" +
          "Q - Question lookup\n" +
          "A - Add An Answer\n" +
          "P - View all question/answer pairs\n" +
          "E - Exit\n")
        print()
        cmd = input("Enter command: ").strip().lower()
        print()
        if cmd in ('e', 'exit'):
            break

        elif cmd == 'q':
            # Ask for product category first
            print("\nAvailable categories: adhesives, safety, light")
            cat = input("Enter a product category (or 'exit' to return): ").strip().lower()
            if cat == 'exit':
                print()
                continue

            if cat not in categories:
                print("Unknown category. Returning to main menu.\n")
                continue

            allowed_ids = categories[cat]

            while True:
                user_query = input("\nEnter your question (or type 'exit' to return to main menu): ").strip()
                if user_query.lower() == 'exit':
                    print()
                    break

                results = [
                    r for r in tfidf_search_all(user_query, question_texts, tfidf_matrix)
                    if r[2] in allowed_ids
                ]

                if not results:
                    print("No matching questions found for that category.")
                    continue

                while True:
                    for qid, qtext, gid, score in results[:3]:
                        cursor.execute("SELECT product_name FROM Product WHERE g_item_no = ?", (gid,))
                        pname = cursor.fetchone()[0]
                        print(f"\nProduct: {pname}")
                        print(f"Question: {qtext}")

                        cursor.execute(
                            "SELECT answer_text FROM Answer WHERE question_id = ? AND is_primary = 1",
                            (qid,)
                        )
                        primary = cursor.fetchone()
                        if primary:
                            print(f"Answer: {primary[0]}")

                        cursor.execute(
                            """SELECT answer_id, answer_text, upvotes
                               FROM Answer
                               WHERE question_id = ? AND is_primary = 0
                               ORDER BY upvotes DESC, answer_id ASC""",
                            (qid,)
                        )
                        extras = cursor.fetchall()
                        if extras:
                            print("Additional Info:")
                            for aid, txt, uv in extras:
                                print(f" • [{aid}] {txt}  (upvotes: {uv})")

                        print(f"Similarity: {score*100:.1f}%")
                        print("-"*40)

                    action = input("Enter 'u <answer_id>' to upvote, 'f <answer_id>' to flag, or press Enter for new query: ").strip().lower()
                    if action == '':
                        print()
                        break

                    if action.startswith('u '):
                        try:
                            aid = int(action.split()[1])
                            cursor.execute(
                                "UPDATE Answer SET upvotes = upvotes + 1 WHERE answer_id = ? AND is_primary = 0",
                                (aid,)
                            )
                            if cursor.rowcount:
                                conn.commit()
                                new_score = cursor.execute(
                                    "SELECT upvotes FROM Answer WHERE answer_id = ?", (aid,)
                                ).fetchone()[0]
                                print(f"Answer {aid} upvoted! New score: {new_score}")
                            else:
                                print(f"Cannot upvote {aid}: not found or primary answer.")
                        except ValueError:
                            print("Invalid answer ID.")
                    elif action.startswith('f '):
                        try:
                            aid = int(action.split()[1])
                            reason = input("Enter flag reason: ").strip()
                            print(f"Answer {aid} flagged for review. Reason: {reason}")
                        except ValueError:
                            print("Invalid answer ID.")
                    else:
                        print("Unrecognized command.\n")

        elif cmd == 'a':
            (file_path) = input("Enter the path to the JSON transcript file: ").strip()
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

                vectorizer = TfidfVectorizer()
                tfidf_matrix = vectorizer.fit_transform(question_texts)
                print("TF-IDF model updated with new question.\n")
                continue

        elif cmd == 'p':
            print_all_qas(conn)
            print()

        else:
            print("Unknown command. Please enter Q, P, or E.")

    conn.close()


if __name__ == "__main__":
    main()


# if flagged as unhelpful move to the bottom
# add a note for next rep


# import sqlite3
# import json
# import re
#
# # Vectorize all question texts using TF-IDF, imports and global variables
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity
# vectorizer = None
# tfidf_matrix = None
# rows = None
#
#
# # This function parses through the json file
# # json file is generated by the phone transcript being sent
# # to an api, for example Google Cloud Speech-to-Text, Microsoft Azure Speech, AWS Transcribe
# # that api returns the json file to us
#
# def parse_json_transcript(file_path):
#     # list to store q and a dictionaries
#     records = []
#     current_product_id = None
#     qa_pending = None
#
#     with open(file_path, "r", encoding="utf-8") as f:
#         transcript_data = json.load(f)
#
#     # json object has a key "results" that contains a list
#     # this code iterates over the list
#
#     # HAVE ALL QUESTIONS BE PRODUCT SELECTION FOCUSED - HOW DO YOU KNOW WHICH ONE YOU NEED? ------------------------------------------------------------------------
#     # BRUSHLESS AND BRUSHED MOTORS - WHEN DO YOU NEED ONE VS THE OTHER? --------------------------------------------------
#     # FOR THE PROTOTYPE: HAVE IT SHOW UP IN THE PROTOTYPE -------------------------------------------------------------------
#     # HAVE TOP THREE QUESTIONS ALWAYS SHOW UP AS YOU SCROLL THROUGH GRAINGER -------------------------------------------------------
#     # HOW WOULD IT WORK IF THEY DONT USE SPEECH TO TEXT?
#     # ADD CATEGORY
#     # PRESENTATION - INTRO SLIDE, VIDEO/LIVE DEMO, HOW WOULD YOU DEPLOY? METRICS?
#     # how do you make sure it stays secure? part 1 shows them the questions, part 2 it links with their salesforce data and brings up frequent things
#     # argument - easy to do
#     # order reminder tool - your company buys this every 8 days, you havent ordered in 18 days, do you want to buy this?
#     # Keepstock - vending machine tells grainger its empty EX personal safety equipment
#
#
#     for result in transcript_data.get("results", []):
#         alt = result.get("alternatives", [])[0]
#         utterance = alt.get("transcript", "").strip()
#
#         # Look for a product ID pattern
#         prod_id_match = re.search(r'product\s*ID\s*([0-9]+)', utterance, re.IGNORECASE)
#         if prod_id_match:
#             current_product_id = prod_id_match.group(1)
#
#         # Identify a Customer question.
#         if utterance.startswith("Customer:"):
#             text = utterance.split("Customer:")[-1].strip()
#             if text.endswith('?'):
#                 qa_pending = {"product_id": current_product_id, "question": text}
#
#         # Look for an Agent answer following a Customer question.
#         elif utterance.startswith("Agent:"):
#             text = utterance.split("Agent:")[-1].strip()
#             if qa_pending and text:
#                 qa_pending["answer"] = text
#                 records.append(qa_pending)
#                 qa_pending = None
#
#     return records
#
#
# def review_and_edit_records(records):
#     """
#     Provides a CLI-based interface for the agent to review and optionally edit the extracted records.
#     """
#     print("\nReview the extracted Q&A records:\n")
#     for idx, record in enumerate(records, start=1):
#         print(f"Record {idx}:")
#         print(f"  Product ID: {record['product_id']}")
#         print(f"  Question  : {record['question']}")
#         print(f"  Answer    : {record['answer']}")
#         while True:
#             edit_option = input("Do you want to edit this record? (y/n): ").strip().lower()
#             if edit_option == 'y':
#                 field = input("Which field do you want to edit? (product/question/answer): ").strip().lower()
#                 if field in ["product", "question", "answer"]:
#                     new_val = input(f"Enter new value for {field}: ").strip()
#                     if field == "product":
#                         record["product_id"] = new_val
#                     elif field == "question":
#                         record["question"] = new_val
#                     elif field == "answer":
#                         record["answer"] = new_val
#                     print("Updated record:")
#                     print(f"  Product ID: {record['product_id']}")
#                     print(f"  Question  : {record['question']}")
#                     print(f"  Answer    : {record['answer']}")
#                 else:
#                     print("Invalid field. Please choose product, question, or answer.")
#             elif edit_option == 'n':
#                 break
#             else:
#                 print("Please enter 'y' or 'n'.")
#         print("\n")
#     return records
#
#
# def get_existing_connection(db_path="qa.db"):
#     """
#     Opens a connection to the existing database that already includes the Product and Question tables.
#     Update db_path with your actual database file.
#     """
#     try:
#         conn = sqlite3.connect(db_path)
#         return conn
#     except Exception as e:
#         print("Error connecting to the database:", e)
#         return None
#
# def insert_question_records(conn, records):
#     """
#     Inserts each Q&A record into the existing Question table.
#     Assumes that the extracted product_id corresponds to the Product.g_item_no.
#     """
#     cursor = conn.cursor()
#     for rec in records:
#         try:
#             # Convert product_id to integer to match g_item_no type.
#             g_item_no = int(rec["product_id"])
#         except ValueError:
#             print(f"Invalid product id found: {rec['product_id']} in record {rec}")
#             continue
#
#         cursor.execute('''
#             INSERT INTO Question (g_item_no, question_text, answer_text)
#             VALUES (?, ?, ?)
#         ''', (g_item_no, rec["question"], rec["answer"]))
#     conn.commit()
#
#
#
#
# # This function creates the dummy data we are going to use for the demo.
# #  right now its super simple for testing but we can make it closer to the info they have on their catalog later
# def create_example_data(conn):
#     cursor = conn.cursor()
#     # Drop tables if they already exist (for demo purposes)
#     cursor.execute("DROP TABLE IF EXISTS Product")
#     cursor.execute("DROP TABLE IF EXISTS Question")
#
#     # Create Product table
#     cursor.execute('''
#         CREATE TABLE Product (
#             g_item_no INTEGER PRIMARY KEY,
#             mfr_model INTEGER,
#             product_name VARCHAR(255),
#             brand_series VARCHAR(100),
#             color VARCHAR(50),
#             finishing_features VARCHAR(50),
#             container_type VARCHAR(50),
#             container_size VARCHAR(100),
#             working_time VARCHAR(100),
#             working_time_type VARCHAR(50),
#             product_use VARCHAR(100)
#
#         )
#     ''')
#
#     # Create Question table with a foreign key to Product table
#     cursor.execute('''
#         CREATE TABLE Question (
#             question_id INTEGER PRIMARY KEY,
#             g_item_no INTEGER,
#             question_text VARCHAR(255),
#             answer_text VARCHAR(255),
#             FOREIGN KEY (g_item_no) REFERENCES Product(g_item_no)
#         )
#     ''')
#
#     # Insert dummy data into the Product table
#     products = [
#         (1001, 12345, 'Super Adhesive', 'UltraBond Series', 'Red', 'Matte', 'Tube', '50ml', '30', 'minutes', 'Industrial use'),
#         (1002, 67890, 'Waterproof Sealant', 'SealPro Series', 'Blue', 'Glossy', 'Bottle', '100ml', '45', 'minutes', 'Building and construction'),
#         (1003, 54321, 'High-Temp Sealant', 'HeatShield Series', 'Yellow', 'Satin', 'Cartridge', '200ml', '60', 'minutes', 'Automotive')
#     ]
#     cursor.executemany('''
#         INSERT INTO Product
#         (g_item_no, mfr_model, product_name, brand_series, color, finishing_features, container_type, container_size, working_time, working_time_type, product_use)
#         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#     ''', products)
#
#     # Insert dummy data into the Question table
#     questions = [
#         (1, 1001, 'How do I install Super Adhesive?', 'Clean the surface, apply the adhesive evenly, and allow it to cure for 30 minutes.'),
#         (2, 1002, 'How do I apply Waterproof Sealant?', 'Ensure surfaces are dry, apply a thin layer, and let dry for 45 minutes.'),
#         (3, 1003, 'What are the temperature limits for High-Temp Sealant?', 'This sealant is rated for use up to 500°F.')
#     ]
#     cursor.executemany('''
#         INSERT INTO Question (question_id, g_item_no, question_text, answer_text)
#         VALUES (?, ?, ?, ?)
#     ''', questions)
#
#     conn.commit()
#
#
# def print_all_questions(conn):
#     """
#     Prints all rows from the Question table in the connected SQLite database.
#
#     The function queries for question_id, g_item_no, question_text, and answer_text,
#     then prints them with headers.
#     """
#     cursor = conn.cursor()
#     cursor.execute("SELECT question_id, g_item_no, question_text, answer_text FROM Question")
#     rows = cursor.fetchall()
#
#     if rows:
#         header = f"{'Question ID':<12} {'Product ID':<10} {'Question':<50} {'Answer':<50}"
#         print(header)
#         print("-" * len(header))
#         for question_id, product_id, question_text, answer_text in rows:
#             print(f"{question_id:<12} {product_id:<10} {question_text:<50} {answer_text:<50}")
#     else:
#         print("No questions found in the database.")
#
#
#
# #function that will use the tfidf protocal that will use cosine simalarity in order to find similar matches over 30%.
# def tfidf_search_all(user_input, question_texts, tfidf_matrix, threshold=0.2):
#     user_vec = vectorizer.transform([user_input])
#     similarities = cosine_similarity(user_vec, tfidf_matrix)[0]
#
#     # Pair each similarity score with the corresponding row index
#     scored_matches = [(i, score) for i, score in enumerate(similarities) if score > threshold]
#
#     # Sort by score descending
#     scored_matches.sort(key=lambda x: x[1], reverse=True)
#
#     # Return a list of tuples: (question_text, answer_text, product_id, similarity)
#     results = []
#     for i, score in scored_matches:
#         question_text, answer_text, product_id = rows[i][1], rows[i][2], rows[i][3]
#         results.append((question_text, answer_text, product_id, score))
#
#     return results
#
#
#
#
# def main():
#     global vectorizer, tfidf_matrix, rows #global variables to allow the search and save.
#
#
#
#     # Connect to an in-memory SQLite database using sqlite3
#     # This is so that you start with a clean slate every time you run the code
#     conn = sqlite3.connect(":memory:")
#     # Create tables and dummy data
#     create_example_data(conn)
#     cursor = conn.cursor()
#
#     #gets existing questions from the database in order to build the tfidf model (may need to tweak the code in order to do this after questions are added )
#     cursor.execute("SELECT question_id, question_text, answer_text, g_item_no FROM Question")
#     rows = cursor.fetchall()
#     #vectorization
#     question_texts = [row[1] for row in rows]
#     vectorizer = TfidfVectorizer()
#     tfidf_matrix = vectorizer.fit_transform(question_texts)
#
#     # program menu (we can add more commands here if we need)
#     print("Grainger Product Guide\n" +
#           "Q - Question lookup\n" +
#           "A - Add a question\n" +
#           "P - View all question/answer pairs\n")
#
#     # loop for keeping the program running
#     while True:
#         # enter a command from the main menu
#         command = input("\nEnter your command (or type 'exit' to quit): ")
#         command = command.strip().lower()
#         if command == 'exit':
#             break
#
#         print("You entered: " + command + "\n")
#
#         # SEARCH A QUESTION
#         if command == 'q':
#             while True:
#                 user_query = input("\nEnter your question: (or type 'exit' to quit): ")
#
#                 if user_query == 'exit':
#                     break
#                 # result = tfidf_search(user_query, question_texts, tfidf_matrix)
#                 # if result:
#                 #     question_text, answer_text, product_id = result[1], result[2], result[3]
#                 #     cursor.execute("SELECT product_name FROM Product WHERE g_item_no = ?", (product_id,))
#                 #     product_name = cursor.fetchone()[0]
#                 #     print(f"\nProduct: {product_name}")
#                 #     print(f"Question: {question_text}")
#                 #     print(f"Answer: {answer_text}")
#                 #     print("-" * 40)
#                 # else:
#                 #     print("No matching questions found. Consider adding this as new data if it's a common query.")
#                 results = tfidf_search_all(user_query, question_texts, tfidf_matrix)
#                 if results:
#                     for question_text, answer_text, product_id, score in results[:3]:
#                         cursor.execute("SELECT product_name FROM Product WHERE g_item_no = ?", (product_id,))
#                         product_name = cursor.fetchone()[0]
#                         print(f"\nProduct: {product_name}")
#                         print(f"Question: {question_text}")
#                         print(f"Answer: {answer_text}")
#                         print(f"Similarity: {score * 100:.1f}%")
#                         print("-" * 40)
#                         print()
#                 else:
#                     print("No matching questions found.")
#
#         # TECH REP OPTION
#         # agent logs in and presses a to initiate transcript processing
#         # system prompts agent to select json file (transcript)
#         # file path is processed
#         # All this would happen automatically in real world application after agent hangs up the phone
#
#         # once file is processed and q and a pairs are extracted, agent can review
#         # agent modifies it if needed
#         # after agent confirms, it is added to the database
#         if command == 'a':
#             file_path = input("Enter the path to the JSON transcript file: ").strip()
#             try:
#                 records = parse_json_transcript(file_path)
#                 if not records:
#                     print("No Q&A pairs were found in the transcript.")
#                     return
#                 records = review_and_edit_records(records)
#
#                 print("Final Q&A entries:")
#                 for idx, rec in enumerate(records, start=1):
#                     print(f"{idx}. Product ID: {rec['product_id']} | Question: {rec['question']} | Answer: {rec['answer']}")
#                 confirm = input("Are you happy with these entries? (y/n): ").strip().lower()
#                 if confirm == 'y':
#                     insert_question_records(conn, records)
#
#                 else:
#                     print("Record insertion canceled.")
#             except FileNotFoundError:
#                 print("The file was not found. Please check the path and try again.")
#             except json.JSONDecodeError:
#                 print("There was an error parsing the JSON file. Please ensure the file is in proper JSON format.")
#
#             # user_question = input("\nEnter the question to add: ")
#             # user_answer = input("\nEnter the answer: ")
#             # user_p_id = input("\nEnter the product id (only numbers): ")
#             #
#             # insert_q_and_a(conn, user_question, user_answer, user_p_id)
#             # cursor.execute("SELECT question_id, question_text, answer_text, g_item_no FROM Question")
#             # rows = cursor.fetchall()  # Update global rows
#             # question_texts = [row[1] for row in rows]
#             vectorizer = TfidfVectorizer()
#             tfidf_matrix = vectorizer.fit_transform(question_texts)
#             print("TF-IDF model updated with new question.\n")
#             continue
#
#         if command == 'p':
#             print_all_questions(conn)
#             continue
#
#
#     # close the program
#     conn.close()
#
#
#
# if __name__ == "__main__":
#     main()
#

