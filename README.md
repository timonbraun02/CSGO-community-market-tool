# CSGO-community-market-tool

This tool can help you to keep track of your investments in csgo cases on the steam community market by creating and maintaining excel sheets with current market prices.
It will probably work for other items such as skins.
The Example folder shows what a finished setup will look like.
To use the tool, you will need the python script and the file in the Config folder in the same folder on you pc.
The script will create all other excel sheets, when you run it or the first time.

## Quick-start guide

1. Copy the python script and the items.xlsx file in the same folder on your pc
2. Configure the items.xlsx file by deleting the example and adding your items to the sheet. You need to provide the item name, the amount you own and the url to the steam market page
3. Run the python script
4. It will open the command line and ask for an input
5. Select the first option by typing "1" and pressing ENTER
6. The script will create a price history database and an excel file with an overview of the current prices on the market
7. To refresh, run the script and select the first option
8. To avoid getting banned from requesting data from steam, the script will only allow you to refresh market prices once every hour 
9. Profit
