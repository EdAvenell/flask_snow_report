from flask import Flask, render_template
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)

# code to run python app.py
# Function to scrape the snow data
def scrape_snow_data(url):
    page_to_scrape = requests.get(url)
    soup = BeautifulSoup(page_to_scrape.text, "html.parser")
    
    # Find the row for "Top Lift"
    top_lift_row = soup.find('td', string=lambda text: text and "Top Lift" in text)
    top_temp_cell = top_lift_row.find_next_sibling('td').find_next_sibling('td')
    top_temperature = top_temp_cell.find('span', class_='temp').text
    
    # Find the row for "Middle Lift"
    middle_lift_row = soup.find('td', string=lambda text: text and "Middle Lift" in text)
    middle_temp_cell = middle_lift_row.find_next_sibling('td').find_next_sibling('td')
    middle_temperature = middle_temp_cell.find('span', class_='temp').text

    # Find the fresh snow depth
    freshsnowfalldepth = soup.find_all('span', attrs={'class': 'snowht'})
    freshsnow_text = ', '.join([freshsnow.text for freshsnow in freshsnowfalldepth]) + " cm"

    # Find the new snow information and the date
    new_snow_div = soup.find('div', class_='is-hidden is-block-large-up')
    new_snow_amount = new_snow_div.find('span').text if new_snow_div else '-'

    # Check if the new snow amount contains "cm", else return '-'
    if 'cm' not in new_snow_amount:
        new_snow_amount = '-'

    div_text = new_snow_div.get_text() if new_snow_div else ''
    date_info = div_text.split('on')[-1].strip() if 'on' in div_text else '-'

    # Find the Top snow depth
    top_snow_depth_row = soup.find('th', string=lambda text: text and "Top snow depth" in text)
    top_snow_depth_cell = top_snow_depth_row.find_next_sibling('td')
    top_snow_depth = top_snow_depth_cell.text.strip()

    # Find the country 
    flag_container = soup.find('a', class_='location-header__flag-container')
    if flag_container:
        # Extract country from href attribute
        country = flag_container['href'].split('/')[2]
    else:
        country = '-'

    # Return the scraped data as a dictionary
    return {
        "top_temperature": top_temperature,
        "middle_temperature": middle_temperature,
        "fresh_snow": freshsnow_text,
        "new_snow": new_snow_amount,
        "new_snow_date": date_info,
        "top_snow_depth": top_snow_depth,
        "country": country,
    }


@app.route('/')
def index():
    # URLs to scrape
    urls = [
        "https://www.snow-forecast.com/resorts/Grindelwald/6day/mid",
        "https://www.snow-forecast.com/resorts/Zermatt/6day/mid",
        "https://www.snow-forecast.com/resorts/Klosters/6day/mid",
        "https://www.snow-forecast.com/resorts/Val-Thorens/6day/mid"
          ]
    
    # Scrape data from each URL
    snow_data = {url.split('/')[-3]: scrape_snow_data(url) for url in urls}

 # Reorganize the data to sort by country
    # Create a dictionary with countries as keys and list of data as values
    country_data = {}
    for location, data in snow_data.items():
        country = data['country']
        if country not in country_data:
            country_data[country] = []
        country_data[country].append({**data, 'location': location})

    # Sort the dictionary by country name
    sorted_country_data = dict(sorted(country_data.items()))

    # Flatten the data into a list of tuples (country, location, data)
    flattened_data = []
    for country, entries in sorted_country_data.items():
        for entry in entries:
            flattened_data.append((country, entry['location'], entry))

    # Render the sorted data in the HTML template
    return render_template('index.html', data=flattened_data)
    #Code to run the website python app.py  
if __name__ == '__main__':
    app.run(debug=True)