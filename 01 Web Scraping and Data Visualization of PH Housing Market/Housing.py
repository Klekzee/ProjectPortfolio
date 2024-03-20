from bs4 import BeautifulSoup
import requests
import pandas as pd
from geopy.geocoders import Nominatim

# New header in case python default gets blocked by the site.
headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36 OPR/38.0.2220.41'}

houselinks = []
data = []
house_id = 0

# Requesting all the house selling links in all pages.
for x in range(0,1): # Change the range values for the pages
    result = requests.get('https://www.lamudi.com.ph/house/buy/?page={}'.format(x)).text
    soup = BeautifulSoup(result, 'lxml')
    houselist = soup.find_all('div', {'ListingCell-AllInfo ListingUnit'})

    # Inputing the links into the 'houslinks list'.
    for house in houselist:
        links = house.find('a', {"class":'js-listing-link'}).get('href')
        houselinks.append(links)


# Requesting all the links from 'houselinks list' one by one to get data out of them.
for links in houselinks:
    f = requests.get(links, headers=headers).text
    hun = BeautifulSoup(f,'lxml')

    # Title
    try:
        title = hun.find('h1', {'class':'Title-pdp-title'}).text.replace('\n','').strip()
    except:
        title = None

    # Location
    try:
        temp_loc = hun.find('h3', {'class':'Title-pdp-address'}).text.replace('\n','')
        location = " ".join(temp_loc.split()).replace("ñ", "n")

        # Geopy to get the latitude and longitude coordinates
        geolocator = Nominatim(user_agent='HousingProject001')
        loc = geolocator.geocode(location)
        if loc:
            coords = {"Latitude": loc.latitude, 'Longitude': loc.longitude}
        else:
            coords = {"Latitude": None, 'Longitude': None}

        latitude = coords.get("Latitude")
        longitude = coords.get("Longitude")

    except:
        location = None

    # Price    
    try:
        price = hun.find('span', {'class':'FirstPrice'}).text.replace('\n','').strip().replace('₱', '').replace(',', '')
    except:
        price = None

    # Bedroom / Bathroom / Floor Area / Land Area (They are grouped together since they have similar class names and I used a more complicated method to scrape the data)
    try:
        lname = []
        lnumber = []

        # Since the elements have the same class name, we need to iterate each one of them and store them inside a list.
        for name in hun.find_all('div', {'class': "ellipsis"}):
            x = name.text.replace('\n','').strip()
            lname.append(x)

        for number in hun.find_all('div', {'class': 'last'}):
            y = number.text.replace('\n','').strip()
            lnumber.append(y)

        # Converting the lists into 1 dictionary
        details = dict(zip(lname, lnumber))

        bedrooms = details.get('Bedrooms')
        bathrooms = details.get('Bathrooms')
        floor_area = details.get('Floor area (m²)')
        land_area = details.get('Land Size (m²)')
    except:
        bedrooms = None
        bathrooms = None
        floor_area = None
        land_area = None

    house_id += 1

    # Creating a 'house' dictionary and inputing it into 'data' list for pandas DataFrame.
    house = {'House_ID': house_id, 'Description': title, 'Location': location, 'Price': price, 'Bedrooms': bedrooms, 'Bathrooms': bathrooms, 'Floor Area': floor_area, 'Land Area': land_area, 'Latitude': latitude, 'Longitude': longitude}

    data.append(house)


df = pd.DataFrame(data)

# pd DataFrame display options.
pd.set_option('display.max_colwidth', 70)
print(df)

# Export to .csv
df.to_csv('Housing_v2.csv', index=False)

# FOR FUTURE ME :>
# TODO: improve geocoding and put house/area rating or something like that
#       improve performance (Very slow right now due to geolocating)