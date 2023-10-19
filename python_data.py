import requests
from bs4 import BeautifulSoup
import csv
import time

# Base URL for Amazon product listings
base_url = "https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_1"

# List to store scraped data
scraped_data = []

# Define the function to scrape data from a single product listing page
def scrape_product_listings(page_number):
    url = base_url + str(page_number)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        product_containers = soup.find_all("div", class_="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal")  # Adjust this selector based on Amazon's page structure

        for product in product_containers:
            product_url = "https://www.amazon.in" + product.find('a', class_='a-link-normal')['href']
            product_name = product.find('span', class_='a-size-medium a-color-base a-text-normal').text
            product_price = product.find('span', class_='a-price-whole').text
            rating_element = product.find('span', class_='a-icon-alt')
            rating = rating_element.text if rating_element else "N/A"
            num_reviews = product.find('span', class_='a-size-base').text

            # Extract additional details from product URLs
            additional_info = scrape_product_details(product_url)

            # Add the scraped data to the list
            scraped_data.append({
                "Product URL": product_url,
                "Product Name": product_name,
                "Product Price": product_price,
                "Rating": rating,
                "Number of Reviews": num_reviews,
                **additional_info
            })

def scrape_product_details(product_url):
    time.sleep(2)  # Add a delay to avoid overloading the server
    response = requests.get(product_url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        description = soup.find('span', id='productTitle').text.strip()
        asin_element = soup.find('th', text='ASIN')
        asin = asin_element.find_next('td').text.strip() if asin_element else "N/A"
        product_description_element = soup.find('div', id='productDescription')
        product_description = product_description_element.text.strip() if product_description_element else "N/A"
        manufacturer_element = soup.find('th', text='Manufacturer')
        manufacturer = manufacturer_element.find_next('td').text.strip() if manufacturer_element else "N/A"

        return {
            "Description": description,
            "ASIN": asin,
            "Product Description": product_description,
            "Manufacturer": manufacturer
        }

# Scrape at least 20 pages of product listings
for page_number in range(1, 21):
    scrape_product_listings(page_number)

# Define the CSV file path
csv_file_path = "amazon_product_data.csv"

# Write the scraped data to a CSV file
with open(csv_file_path, "w", newline="", encoding="utf-8") as csv_file:
    fieldnames = ["Product URL", "Product Name", "Product Price", "Rating", "Number of Reviews", "Description", "ASIN", "Product Description", "Manufacturer"]
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    writer.writeheader()
    for data in scraped_data:
        writer.writerow(data)

print(f"Scraped data saved to {csv_file_path}")
