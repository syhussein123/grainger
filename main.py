productIDList = ["35JE49", "796P22", "1234"]

#https://www.grainger.com/product/FULHAM-Fluorescent-Ballast-120V-AC-35JE49
#https://www.grainger.com/product/PHILIPS-Compact-LED-Bulb-LED-796P22
#
questionList = [["Is the Fulham flourescent ballast compatible with an F14T5 type of lamp?", "How would I install this flourescent ballast?", "How does this ballast compare to other ballasts on the market?"],
                ["What is the current for this light", "How would I install this light?", "How does this light compare to other lights on the market?"], ["xyz", "abc"]]
answerList = [["Yes, it is compatible with this type of lamp", "Here is a guide of steps: ", "It has more wattage and is compatible with a variety of lamps"],
              ["65 mA", "Here is a guide of steps: ", "It is shatter resistant and frosted"],
              ["abx", "def"]]

# get input product ID from user
inputProductID = input("Enter the productID: ")
inputProductID = inputProductID.strip() #trim leading and trailing whitespace

# check if product is already in database, if not add it to database
if inputProductID in productIDList:
    index = productIDList.index(inputProductID)
    print("Product found in database...")
else:
    index = len(productIDList) - 1
    print("Product not found in database...Adding...")


# get inputs for questions
inputQuestion = input("Enter the question the customer asked: ")
inputAnswer = input("Enter the answer you gave: ")

#append at the end of the sublist absed on index
questionList[index].append(inputQuestion)
answerList[index].append(inputAnswer)


#testing to see if appended properly
for ans in answerList[index]:
    print(ans)
