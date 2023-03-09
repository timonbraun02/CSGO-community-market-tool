import requests as rq
import pandas as pd
import re
import locale
import time as t
import openpyxl
import os


#Item
class item():
    def __init__(self, URL, Name, Price, Owned, Total, Sold, Change):
        self.Name = Name
        self.Price = Price
        self.Change = Change
        self.Owned = Owned
        self.Total = Total
        self.Sold = Sold
        self.URL = URL


# make api request and return json 
def getJson(url):
    data = rq.get(url)
    if data.status_code == 200:
        return (data.json())
    else:
        print(data.status_code)
        return ("Error")


# call getJson and extract price and volume from json file
# returns [price, volume]
# both 0 if getJson returns "Error"
def updateData(url):
    newJson = getJson(url)
    if newJson != "Error":
        price_string = newJson['lowest_price']

        # change price_string to float and remove '€/$'-Symbol
        decimal_point_char = locale.localeconv()['decimal_point']
        clean = re.sub(r'[^0-9'+decimal_point_char+r']+', '', price_string)

        vol = newJson['volume'].replace(",", "")
        vol = int(vol)
        price = float(clean)/100
        return [price, vol]
    else:
        return [0, 0]

# format provided url to direct request to the desired adress which anwers with the json file
# returns url as string  
def formatURL(url):
    output = url.replace("https://steamcommunity.com/market/listings/730/",
                         "https://steamcommunity.com/market/priceoverview/?appid=730&currency=3&market_hash_name=")
    return output

#### Program starts here ###

#Program executes if it can find item.xlsx in the same folder as the script
try:
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    items = pd.read_excel(os.path.join(__location__, "items.xlsx"))
    item_info_from_api = []
    item_list_for_excel = []
    date_now = t.strftime("%d %m %Y %H")

    # Title
    print("|-------------------------------|")
    print("|                               |")
    print("|   CSGO-Comunity-Market Tool   |")
    print("|                               |")
    print("|-------------------------------|")

    # Asking for user input 
    while(True):
        ans = input("\nSelect you action:\n1) Refresh database\n2) Show last recorded data\n3) Exit\nType your answer: ")
        print("\n")
        if ans == "1":
            # try to open price history database    
            try:
                old_data = pd.read_excel("pricehistory_database.xlsx").tail(1)
                last_date = old_data.iloc[0, 0]

            except:  # in case there is no data base
                print("\nNo database found...")
                print("Creating data history file...")
                data_for_price_history = {"Date": t.strftime("%d %m %Y %H:%M:%S")}
                for i in range(len(items)):
                    data_for_price_history[items["Name"][i]] = 0
                history_df = pd.DataFrame(data_for_price_history, index=[0])
                last_date = "0"
                history_df.to_excel("pricehistory_database.xlsx", index=False)
                print("Done\n")

            # only allow api requests once every hour to avoid getting banned
            if date_now != last_date[0:13]:
                data_for_price_history = {"Date": t.strftime("%d %m %Y %H:%M:%S")}
                print("Requesting data...")
                price_history = pd.read_excel("pricehistory_database.xlsx") # get old price history from excel
                for i in range(len(items)):
                    newURL = formatURL(items["URL"][i])
                    item_info_from_api.append(updateData(newURL))
                    #item_info_from_api.append([0, 0]) # for testing purposes

                    # assing every item their properties and append them to list 
                    item_list_for_excel.append(item(
                        URL=newURL,
                        Name=items["Name"][i],
                        Owned=items["Amount"][i],
                        Price=item_info_from_api[i][0],
                        Total=item_info_from_api[i][0] * items["Amount"][i],
                        Sold=item_info_from_api[i][1],
                        Change=item_info_from_api[i][0] - float(price_history[items["Name"][i]].tail(1))))

                    data_for_price_history[items["Name"][i]] = item_info_from_api[i][0] # store price data in dict, {"Name": price}
                    print(str( round(((1+i)*100)/len(items),1)) + "%")    # progressbar
                print("Finished collecting data. Refreshing database...")
                new_history = pd.DataFrame(data_for_price_history, index=[0]) # make dataframe from collected price data

                new_df = pd.concat([price_history, new_history], ignore_index=True) # merge old price history data with new data, essentially append new data to the database 
                new_df.to_excel("pricehistory_database.xlsx", index=False) # save price history as excel file

                df = pd.DataFrame([i.__dict__ for i in item_list_for_excel]) # create dataframe from list of item objects

                df.to_excel("csgo_market_price.xlsx", sheet_name="current", index=False) # save dataframe as excel file
                book = openpyxl.load_workbook("csgo_market_price.xlsx") # open excel file 
                sheet = book.active
                sheet["A20"] = "Total" # write to individual cell
                sheet["B20"] = df["Total"].sum() # write to individual cell
                book.save("csgo_market_price.xlsx") # save file

                print("Finished refreshing database")
                print("Here is an overview:\n")
                print(df)
                break
            else: # incase user trys to refresh data twice in one hour
                try: # try to open the exel files
                    print("You can request new data only once an hour!")
                    print("Here is an overview of the most recent data:\n")
                    price_history = pd.read_excel("pricehistory_database.xlsx").tail(1) # get last line of price history database
                    print(price_history)
                    old_data = pd.read_excel("csgo_market_price.xlsx") # get item overview
                    print(old_data)
                    break
                except: # incase the excel files dont exist yet
                    print("An exception occurred!\nMost likely, the program could not find the requestet files.\nCheck if the pricehitory_database.xlsx and csgo_market_price.xlsx are in the same directory as the python script.\nIf you are running the programm for the first time, it has not created the files yet.\nYou have to run the first option to create the databases")
                    break
        elif ans == "2":
            try: # try to open the exel files
                price_history = pd.read_excel("pricehistory_database.xlsx").tail(1)
                print(price_history)
                case_data = pd.read_excel("csgo_market_price.xlsx")
                print(case_data)
                break
            except: # incase the excel files dont exist yet
                print("An exception occurred!\nMost likely, the program could not find the requestet files.\nCheck if the pricehitory_database.xlsx and csgo_market_price.xlsx are in the same directory as the python script.\nIf you are running the programm for the first time, it has not created the files yet.\nYou have to run the first option to create the databases")
        elif ans == "3": # Exit the program
            break
        else: # for any other input
            print("Unkown input.\nTry again.")
except: # incase the item.xlsx file doesnt exist or is not in the same folder as the python script
    print("An exception occurred.\nMake sure you provide the item.xlsx file in the same directory as the script!")

input("\nPress ENTER to exit.")
