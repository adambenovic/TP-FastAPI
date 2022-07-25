import httpx
import os
from hashlib import sha256
from app import schema


async def find_company_by_ico(ico):
    async with httpx.AsyncClient() as client:
        pub = os.environ['FINSTAT_PUBLIC_API_KEY']
        private = os.environ['FINSTAT_PRIVATE_API_KEY']

        result = await client.post('https://www.finstat.sk/api/detail.json', headers={
            'Content-Type': 'application/x-www-form-urlencoded'
        }, data={
            'Ico': ico,
            'apiKey': pub,
            'Hash': generate_hash_of_param_for_search_api(pub, private, ico)
        })

        return convert_finstat_data_to_company(result.json())


def generate_hash_seed(public_key, private_key, hashed_key_attribute):
    return 'SomeSalt+' + public_key + '+' + private_key + '++' + hashed_key_attribute + '+ended'


def generate_hash_of_param_for_search_api(pub, private, ico):
    return sha256(generate_hash_seed(pub, private, ico).encode()).hexdigest()


def data_to_str(data):
    for k in data:
        try:
            if data[k] is None:
                data[k] = ''
            else:
                data[k] = str(data[k])
        except:
            pass
    return data


def convert_finstat_data_to_company(data):
    company = schema.FinstatCompany()
    data = data_to_str(data)
    company.Ico = data['Ico']
    company.Dic = data['Dic']
    company.IcDPH = data['IcDPH']
    company.Name = data['Name']
    company.Street = data['Street']
    company.StreetNumber = data['StreetNumber']
    company.ZipCode = data['ZipCode']
    company.City = data['City']
    company.District = data['District']
    company.Region = data['Region']
    company.Country = data['Country']
    company.Activity = data['Activity']
    company.Created = data['Created']
    company.Cancelled = data['Cancelled']
    company.Url = data['Url']
    company.Revenue = data['Revenue']
    company.RevenueActual = data['RevenueActual']

    return company
