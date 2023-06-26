import requests, json, typing
from bs4 import BeautifulSoup

class FourLapiParser:

    def __init__(self) -> None:
        self.domain = 'https://4lapy.ru'
        self.page = 1
        self.file_name = 'output.json'
        self.backup = []
        self.headers = {
            'Content-Type': 'text/html; charset=UTF-8',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            
        }
        self.max_page = self.define_max_page()
        

    def define_max_page(self) -> int:
        base_url = f'https://4lapy.ru/catalog/sobaki/korm-sobaki/?section_id=165&sort=popular&page={self.page}'
        req = requests.get(base_url, headers=self.headers)
        soup = BeautifulSoup(req.text, 'lxml')
        return int(soup.find_all('li', {'class': 'b-pagination__item'})[-2].find('a').text.strip())

    def collect_data(self) -> list[dict]:
        base_url = f'https://4lapy.ru/catalog/sobaki/korm-sobaki/?section_id=165&sort=popular&page={self.page}'
        req = requests.get(base_url, headers={
            'Content-Type': 'text/html; charset=UTF-8',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
        })
        soup = BeautifulSoup(req.text, 'lxml')
        data = soup.find('div', {'id': 'websiteElement-catalog-products-wrapper'}).find_all('div', {'class':['b-common-item','b-common-item--catalog-item', 'js-product-item']})
        return data
    
    def product_is_available(self, id: int, link) -> bool:
        try:
            req = requests.get(f'https://api.retailrocket.ru/api/1.0/partner/5b151eb597a528b658db601e/items/?itemsIds={id}&format=json', headers=self.headers).json()[0]
             
            if req['IsAvailable']:
                return True
            else:
                if self.double_check(req['Url']):
                    return True
                return False
        except IndexError:
            print(f'Product with some error has id - {id}. API for this product returns empty list.')
            if self.double_check(link):
                return True
            return False

    def double_check(self, url) -> bool:
        req = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(req.text, 'lxml')
        marker = soup.select('li.b-product-information__item.js-current-offer-availability')[0].find('div', {'class': 'b-product-information__value'})
        if marker.text.strip() == 'В наличии' or marker.text.strip() == 'Только самовывоз':
            return True
        return False
    
    def prepare_data(self) -> typing.Dict[str, typing.Any]:
        output = []
        data = self.collect_data()
        for element in data:
            product_id = int(element.select('a.b-weight-container__link.js-price.active-link')[0].get('data-offerid'))
            product_link = self.domain + element.find('a', {'class': ['b-common-item__image-link', 'js-item-link']}).get('href')
            if self.product_is_available(product_id, product_link):
                previous_price = element.select('a.b-weight-container__link.js-price.active-link')[0].get('data-oldprice')
                if previous_price == '':
                    previous_price = 0
                output.append({
                    'product_id': product_id,
                    'product_name': element.find('span', {'class': ['b-item-name', 'js-item-name']}).text.strip(),
                    'product_link': product_link,
                    'product_current_price': float(element.find('span', {'class': ['b-common-item__bottom_current_price']}).find('span').text.strip()),
                    'product_previous_price': float(previous_price),
                    'product_brand': element.find('span', {'class': 'span-strong'}).text.strip()
                })

        self.backup.append(output)

        print(f'\rСпарсилось {self.page - 1} из {self.max_page} страниц', end='')

        if self.page - 1 != self.max_page:
            self.page += 1
            self.prepare_data()
        return self.backup
    
    def output_file(self) -> typing.TextIO:
        data = self.prepare_data()

        with open(self.file_name, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        
            

parser = FourLapiParser()
parser.output_file()