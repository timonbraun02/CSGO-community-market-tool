import requests as rq
import pandas as pd
import re
import locale
import time as t
import openpyxl
import os

local_time = t.localtime(t.time())

test_url = "https://stackoverflow.com"

item_data = []


class item():
    def __init__(self, URL, Name, Price, Owned, Total, Sold, Change):
        self.Name = Name
        self.Price = Price
        self.Change = Change
        self.Owned = Owned
        self.Total = Total
        self.Sold = Sold
        self.URL = URL


def getJson(url):
    data = rq.get(url)
    if data.status_code == 200:
        return (data.json())
    else:
        print(data.status_code)
        return ("Error")


def updateData(url):
    newJson = getJson(url)
    if newJson != "Error":
        price_string = newJson['lowest_price']

        # dark magic: change price_string to float and remove '€'-Symbol
        decimal_point_char = locale.localeconv()['decimal_point']
        clean = re.sub(r'[^0-9'+decimal_point_char+r']+', '', price_string)
        # dark magic
        vol = newJson['volume'].replace(",", "")
        vol = int(vol)
        price = float(clean)/100
        return [price, vol]
    else:
        return [0, 0]


def formatURL(url):
    output = url.replace("https://steamcommunity.com/market/listings/730/",
                         "https://steamcommunity.com/market/priceoverview/?appid=730&currency=3&market_hash_name=")
    return output


def getChange(data_frame):
    data_frame.tail(2)
    for i in range(len(items["Name"])):
        change = [].append(data_frame[items["Name"][i]]
                           [0] - data_frame[items["Name"][i]][1])
        print(items["Name"][i])
        print(change)


__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
items = pd.read_excel(os.path.join(__location__, "items.xlsx"))
item_info_from_api = []
item_list_from_excel = []
date_now = t.strftime("%d %m %Y %H")

print("|-------------------------------|")
print("|                               |")
print("|   CSGO-Comunity-Market Tool   |")
print("|                               |")
print("|-------------------------------|")

while(True):
    ans = input("\nSelect you action:\n1) Refresh database\n2) Show last recorded data\n3) Exit\nType your answer: ")
    print("\n")
    if ans == "1":

        try:
            old_data = pd.read_excel("pricehistory_database.xlsx").tail(1)
            last_date = old_data.iloc[0, 0]

        except:  # falls es noch keine alten daten gibt
            print("\nNo database found...")
            print("Creating data history file...")
            data = {"Date": t.strftime("%d %m %Y %H:%M:%S")}
            for i in range(len(items)):
                data[items["Name"][i]] = 0
            history_df = pd.DataFrame(data, index=[0])
            last_date = "0"
            history_df.to_excel("pricehistory_database.xlsx", index=False)
            print("Done\n")

        if date_now != last_date[0:13]:
            data = {"Date": t.strftime("%d %m %Y %H:%M:%S")}
            print("Requesting data...")
            price_history = pd.read_excel("pricehistory_database.xlsx")
            for i in range(len(items)):
                newURL = formatURL(items["URL"][i])
                item_info_from_api.append(updateData(newURL))
                #item_info_from_api.append([0, 0])
                item_list_from_excel.append(item(
                    URL=newURL,
                    Name=items["Name"][i],
                    Owned=items["Amount"][i],
                    Price=item_info_from_api[i][0],
                    Total=item_info_from_api[i][0] * items["Amount"][i],
                    Sold=item_info_from_api[i][1],
                    Change=item_info_from_api[i][0] - float(price_history[items["Name"][i]].tail(1))))
                data[items["Name"][i]] = item_info_from_api[i][0]
                print(str(((1+i)*100)/len(items)) + "%")    # Progressbar
            print("Finished collecting data. Refreshing database...")
            new_history = pd.DataFrame(data, index=[0])

            new_df = pd.concat([price_history, new_history], ignore_index=True)
            new_df.to_excel("pricehistory_database.xlsx", index=False)

            df = pd.DataFrame([i.__dict__ for i in item_list_from_excel])

            df.to_excel("csgo_market_price.xlsx", sheet_name="current", index=False)
            book = openpyxl.load_workbook("csgo_market_price.xlsx")
            sheet = book.active
            sheet["A20"] = "Total"
            sheet["B20"] = df["Total"].sum()
            book.save("csgo_market_price.xlsx")

            print("Finished refreshing database")
            print("Here is an overview:\n")
            print(df)
            break
        else:
            try:
                print("You can request new data only once an hour!")
                print("Here is an overview of the most recent data:\n")
                price_history = pd.read_excel("pricehistory_database.xlsx").tail(1)
                print(price_history)
                old_data = pd.read_excel("csgo_market_price.xlsx")
                print(old_data)
                break
            except:
                print("An exception occurred!\nMost likely, the program could not find the requestet files.\nCheck if the pricehitory_database.xlsx and csgo_market_price.xlsx are in the same directory as the python script.\nIf you are running the programm for the first time, it has not created the files yet.\nYou have to run the first option to create the databases")
                break
    elif ans == "2":
         try:
            price_history = pd.read_excel("pricehistory_database.xlsx").tail(1)
            print(price_history)
            case_data = pd.read_excel("csgo_market_price.xlsx")
            print(case_data)
            break
         except:
            print("An exception occurred!\nMost likely, the program could not find the requestet files.\nCheck if the pricehitory_database.xlsx and csgo_market_price.xlsx are in the same directory as the python script.\nIf you are running the programm for the first time, it has not created the files yet.\nYou have to run the first option to create the databases")
    elif ans == "3":
        break
    else:
        print("Unkown input.\nTry again.")

input("\nPress ENTER to exit.")
