import requests
from bs4 import BeautifulSoup
from product import *
import urllib
import os
import re


categoryLinks = ["cbd-on-the-go/", "pure-cbd-oil/", "cbd-vape-juice/", "cbd-isolate/", "cbd-oil-capsules/", "cbd-edibles/", "cbd-oil-tinctures-liquids/", "cbd-hemp-oil-body-care/", "cbd-for-pets/"]


# Create list
linkList = []

# Parse page for links
for category in categoryLinks:
    # Get page
    page = requests.get("https://hempmedspx.com/" + category)
    # Because one is messed up, ugh
    if category is "cbd-oil-capsules":
        page = requests.get("https://hempmedspx.com/product-category/cbd-oil-capsules/")

    # Create a BeautifulSoup object
    soup = BeautifulSoup(page.text, 'html.parser')

    # Pull text from product list
    productList = soup.find_all(class_='product-info')

    # Create list
    tempList = []
    for item in productList:
        tempList.append(item.get("href"))
    linkList.append(tempList)


engine = create_engine('sqlite:///LMBB.sqlite')
session = sessionmaker()
session.configure(bind=engine)
Base.metadata.create_all(engine)
s=session()

# Go through all the product pages
for cat in range(len(linkList)):
    for myLink in linkList[cat]:
        print(myLink)

        # Get page
        page = requests.get(myLink)

        # Create a BeautifulSoup object
        soup = BeautifulSoup(page.text, 'html.parser')

        try:
            # Pull relevant info from product list
            title = str(soup.find(class_='product_title').text)
            amount = str(soup.find(class_='amount'))
            description = str(soup.find(class_='woocommerce-product-details__short-description'))
            # Remove HTML tags from description
            htmlReg = r'<[^>]*>'
            description = re.sub(htmlReg, "", description)


            # Images
            imageNameFinal = ""
            imgs = soup.findAll(True, class_ = ["vc_single_image-img", "woocommerce-product-gallery__image"])
            print(imgs)
            for img in imgs:
                # For the two different image types
                try:
                    imgUrl = img["src"]
                except Exception:
                    imgUrl = img.a["href"]

                imgName = imgUrl.split("/")[-1]
                imageNameFinal = imgName
                print(img)
                print(imgUrl)
                print()
                print()
                urllib.request.urlretrieve(imgUrl, filename=("../static/images/Products/" + imgName))




            s.add(Product(title=title, category=categoryLinks[cat], price=amount, description=description, link=myLink, pic=imageNameFinal, weCarry=0))
        except Exception:
            print(Exception)
s.commit()
s.close()
print("done")
