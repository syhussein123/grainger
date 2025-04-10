# https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server?view=sql-server-ver16

# import pyodbc
#
# print("Installed ODBC Drivers:")
# print(pyodbc.drivers())

# products:
# g_item_no INTEGER PRIMARY KEY,
# mfr_model INTEGER,
# product_name VARCHAR(255),
# brand_series VARCHAR(100),
# color VARCHAR(50),
# finishing_features VARCHAR(50),
# container_type VARCHAR(50),
# container_size VARCHAR(100),
# working_time VARCHAR(100),
# working_time_type VARCHAR(50),
# product_use VARCHAR(100)

# question:
# question_id INTEGER PRIMARY KEY,
# g_item_no INTEGER,
# question_text VARCHAR(255),
# answer_text VARCHAR(255),
# FOREIGN KEY (product_id) REFERENCES Product(product_id)


import sqlite3

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

def search_questions(conn, search_query):
    cursor = conn.cursor()
    sql = """
        SELECT q.question_text, q.answer_text, p.product_name 
        FROM Question AS q
        JOIN Product AS p ON q.g_item_no = p.g_item_no
        WHERE q.question_text LIKE ?
    """
    cursor.execute(sql, ('%' + search_query + '%',))
    return cursor.fetchall()

def insert_q_and_a(conn, question, answer, product_id):
    cursor = conn.cursor()
    cursor.execute("SELECT g_item_no FROM Product WHERE g_item_no = ?", (product_id,))
    row = cursor.fetchone()

    if row is None:
        print(f"Product '{product_id}' not found!")
        return
    else:
        g_item_no = row[0]

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


def main():
    # Connect to an in-memory SQLite database using sqlite3
    # This is so that you start with a clean slate every time you run the code
    conn = sqlite3.connect(":memory:")

    # Create tables and dummy data
    create_example_data(conn)
    # print("Dummy data created")

    print("Grainger Product Guide\n" +
          "Q - Question lookup\n" +
          "A - Add a question\n")

    # Interactive loop for searching questions
    while True:
        command = input("\nEnter your command (or type 'exit' to quit): ")
        command = command.strip().lower()
        if command == 'exit':
            break

        print("You entered: " + command + "\n")

        if command == 'q':
            while True:
                user_query = input("\nEnter your question: (or type 'exit' to quit): ")

                if user_query == 'exit':
                    break
                results = search_questions(conn, user_query)
                if results:
                    for question_text, answer_text, product_name in results:
                        print(f"\nProduct: {product_name}")
                        print(f"Question: {question_text}")
                        print(f"Answer: {answer_text}")
                        print("-" * 40)

                else:
                    print("No matching questions found. Consider adding this as new data if it's a common query.")

        if command == 'a':
            user_question = input("\nEnter the question to add: ")
            user_answer = input("\nEnter the answer: ")
            user_p_id = input("\nEnter the product id (only numbers): ")

            insert_q_and_a(conn, user_question, user_answer, user_p_id)
            continue



    conn.close()




if __name__ == "__main__":
    main()








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
