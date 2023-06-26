import requests, json, typing
from bs4 import BeautifulSoup

class FourLapiParser:

    def __init__(self) -> None:
        self.domain = 'https://4lapy.ru'
        self.page = 1
        self.items = 0
        self.file_name = 'output.json'
        self.backup = []

    def collect_data(self) -> list[dict]:
        base_url = f'https://4lapy.ru/catalog/sobaki/korm-sobaki/?section_id=165&sort=popular&page={self.page}'
        req = requests.get(base_url, headers={
            'Content-Type': 'text/html; charset=UTF-8',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
        })
        soup = BeautifulSoup(req.text, 'lxml')
        data = soup.find('div', {'id': 'websiteElement-catalog-products-wrapper'}).find_all('div', {'class':['b-common-item','b-common-item--catalog-item', 'js-product-item']})
        return data
    
    def prepare_data(self) -> typing.Dict[str, typing.Any]:
        output = []
        data = self.collect_data()
        for element in data:
            # Проверка на отсутствие товара в наличии
            if not element.find('span', {'class': 'b-common-item__text'}) or element.find('span', {'class': 'b-common-item__text'}).text.strip() == 'Только самовывоз':
                previous_price = element.find('span', {'class': ['b-common-item__prev-price', 'js-sale-origin']}).text.strip().split(' ')[0]
                if previous_price == '':
                    previous_price = 0
                output.append({
                    'product_id': int(element.get('data-productid').strip()),
                    'product_name': element.find('span', {'class': ['b-item-name', 'js-item-name']}).text.strip(),
                    'product_link': self.domain + element.find('a', {'class': ['b-common-item__image-link', 'js-item-link']}).get('href'),
                    'product_current_price': int(element.find('span', {'class': ['b-common-item__bottom_current_price']}).find('span').text.strip()),
                    'product_previous_price': int(previous_price),
                    'product_brand': element.find('span', {'class': 'span-strong'}).text.strip()
                })
        self.backup.append(output)
        if self.items < 100:
            self.items += len(data)
            self.page += 1
            self.prepare_data()
        return self.backup
    
    def output_file(self) -> typing.TextIO:
        data = self.prepare_data()
        print(len(data))
        with open(self.file_name, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        
            

parser = FourLapiParser()
parser.output_file()