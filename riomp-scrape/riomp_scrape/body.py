from riomp_scrape.objects import Person
from bs4 import BeautifulSoup as bs, Tag

class Body:
    def __init__(self,
                 name: str,
                 contact_person: str,
                 contact_phone: str,
                 contact_email: str,
                 body_address: str,
                 body_phone: str,
                 body_tty: str,
                 body_fax: str,
                 body_website: str,
                 body_email: str,
                 facebook: str,
                 twitter: str,
                 instagram: str,
                 linkedin: str,
                 attributes: dict[str, str],
                 description: str,
                 responsibilities: str,
                 people: dict[str, list[Person]]):
        pass


def parse_body(text: str):
    soup = bs(text, "html.parser")

    forms = soup.find_all('form')
    
    header_form = forms[0]

    name: str = header_form.find('h1').get_text()
    row_div = header_form.find('div').find('div')
    contact_person: str = row_div.find('div').next_sibling().get_text()
    row_div = row_div.next_sibling()
    phone: str = row_div.find('div').next_sibling().get_text()
    row_div = row_div.next_sibling()
    email: str = row_div.find('div').next_sibling().find('a').get_text()

    print(name, contact_person, phone, email)


    