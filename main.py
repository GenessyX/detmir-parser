import typing
import requests
import csv
import sys

def generate_session() -> requests.session:
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "DNT": "1",
        "Host": "api.detmir.ru",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0"
    }
    session = requests.session()
    session.headers.update(headers)
    return session

def get_data(session: requests.session, limit:int=30, offset:int=0, city:str='SPE', category:str='lego') -> list:
    endpoint = "https://api.detmir.ru/v2/products"
    prod_filter = "categories[].alias:{};promo:false;withregion:{}".format(category, city)
    payload = {"limit": limit, "offset": offset, "filter": prod_filter}
    response = session.get(endpoint, params=payload)
    if response.ok and len(response.json()):
        return response.json()
    else:
        return None

def get_csv_writer(file_name: str, field_names: list):
    csvfile = open(file_name, 'w', newline='')
    csv_writer = csv.DictWriter(csvfile, field_names)
    csv_writer.writeheader()
    return csv_writer, csvfile


def write_data(csv_writer: csv.DictWriter, json: list):
    for row in json:
        if row['promo']:
            promo_price = row['price']['price']
            price = row['old_price']['price']
        else:
            promo_price = None
            price = row['price']['price']
        csv_writer.writerow({
                                'id': row['id'], 
                                'title': row['title'], 
                                'price': price, 
                                'promo_price': promo_price, 
                                'url': row['link']['web_url']
                            })

def parse_site(city: str='RU-MOW', category: str = 'lego', logging: bool = True):
    session = generate_session()
    limit = 30
    offset = 0

    file_name = 'detmir-{}-{}.csv'.format(category, city)
    field_names = ["id", "title", "price", "promo_price", "url"]
    csv_writer, csvfile = get_csv_writer(file_name, field_names)

    while 1:
        data = get_data(session, limit, offset, city, category)
        if not data:
            break
        write_data(csv_writer, data)
        offset += limit
        if logging:
            sys.stdout.flush()
            sys.stdout.write("\rItem count - {}".format(str(offset)))
            sys.stdout.flush()
    csvfile.close()

def main():
    codes = {"RU-MOW": "Москва", "RU-SPE": "Санкт-Петербург"}
    categories = ['lego']

    for category in categories:
        print("\nCategory - {}".format(category))
        for code in codes:
            print("\nParsing {}".format(codes[code]))
            parse_site(code, category)
            print("\n")
    print("Finished.")

if __name__ == "__main__":
    main()
