import requests
from bs4 import BeautifulSoup
from article import *


# Create list
linkList = []

# Parse page for links
for i in range(1, 37):
    # Get page
    page = requests.get("https://hempmedspx.com/hemp-cbd-education/" + str(i))

    # Create a BeautifulSoup object
    soup = BeautifulSoup(page.text, 'html.parser')

    # Pull text from product list
    productList = soup.find_all(class_='entry_title')

    for x in productList:
        linkList.append(x)

engine = create_engine('sqlite:///LMBB.sqlite')
session = sessionmaker()
session.configure(bind=engine)
Base.metadata.create_all(engine)
s=session()

for l in linkList:
    s.add(Article(tags=str(l)))
s.commit()
s.close()
print("done")
