from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, func
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    category = Column(String)
    price = Column(String)
    description = Column(String)
    link = Column(String)
    pic = Column(String)
    weCarry = Column(Integer)

    # For nice printing
    def __repr__(self):
        return "Test()"
    def __str__(self):
        return ("===============\n" + self.title + "\n" + self.link + "\n" + self.description + "\n" + self.category + "\n" + self.price + "\n" + self.pic + "\n===============")


# Testing
if __name__ == "__main__":
    engine = create_engine('sqlite:///test.sqlite')
    session = sessionmaker()
    session.configure(bind=engine)
    Base.metadata.create_all(engine)

    test = Product(title="Test Product", category="Category", price="Price", description="Description goes here", link="linklinklink", pic="piclink")

    print(test)
