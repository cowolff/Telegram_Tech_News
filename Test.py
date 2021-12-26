from Database import Data
from Amazon_Crawler import check_loop, product_in_database

if __name__ == "__main__":
    database = Data("chats.db")
    api_key = ""
    product_in_database("B097CB1YVL", "DE", "Samsung", database)