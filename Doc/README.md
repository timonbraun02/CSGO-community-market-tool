## Documentation
Currency is set to € by default.
To change currency:
- go to line 55
- find: "https://steamcommunity.com/market/priceoverview/?appid=730&currency=3&market_hash_name="
- to change the currency to $, change currency=1 in the string

## Required Python Libs
- pandas
- openpyxl
- requests
