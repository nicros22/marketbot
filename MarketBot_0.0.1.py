import requests
from time import sleep
from selenium import webdriver

def get_session(list_of_tuples):
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    #options.add_experimental_option('excludeSwitches', ['enable-automation'])
    #options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(executable_path='C:\DanislavScripts\chromedriver.exe', options=options)
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source':'''
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
        '''
    })
    try:
        driver.maximize_window()
        driver.get('https://market-old.csgo.com')
        sleep(5)
        driver.get('https://market-old.csgo.com/float/3770702114/188530139')
        sleep(5)
    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()

API_KEY = '4D63LphrMh5Jh82RX14P65H045R0yk4'
CURRENCY = 'RUB'
ratio = 1.18
YUAN = 11.2
items = []
name_of_selling_items = []
phase_list = ['phase1', 'phase2', 'phase3', 'phase4', 'sapphire', 'ruby', 'emerald', 'blackpearl']

class Items():
    items = []
    def __init__(self, name, id, price=None, min_price=0):
        self.name = name
        self.id = id
        self.price = int(price*float(100))
        self.min_price = int(min_price*float(100))
        Items.items.append(self)


def ping():
    answer = requests.get(f'https://market.csgo.com/api/v2/ping?key={API_KEY}')
    while not (
            answer.headers["content-type"].strip().startswith("application/json") and
            answer.status_code == 200
        ):
            try:
                answer = requests.get(f'https://market.csgo.com/api/v2/ping?key={API_KEY}')
            except:
                print('Не удалось включить продажи, пробую снова')
                sleep(3)
    return answer.json()

def get_request(request):

    return f'https://market.csgo.com/api/v2/{request}'


def get_params(item_name=None, cur=CURRENCY, price=None, item_id=None): #Получить параметры на определенный запрос
    if type(item_name) == list:
        params = {
        'key': f'{API_KEY}',
        'list_hash_name[]': tuple(item_name)
        }
        return params

    params = {
    'hash_name': f'{item_name}',
    'key': f'{API_KEY}',
    'item_id':f'{item_id}',
    'price':f'{price}',
    'cur':f'{cur}',
    }

    return params


def items_on_sell(): 
    items_to_sell = requests.get(get_request('items'), params = get_params())
    while not (
            items_to_sell.headers["content-type"].strip().startswith("application/json") and
            items_to_sell.status_code == 200
        ):
            try:
                items_to_sell = requests.get(get_request('items'), params = get_params())
            except:
                print('Не получить список предметов которые уже стоят на продаже')
                sleep(3) #пока самый продвинутый вариант решения ошибки
    return items_to_sell.json()

def create_item_objects():

    buy_history_file = open('buyhistory.txt', 'r', encoding='utf-8')
    buy_history_data = buy_history_file.readlines()
    buy_history_dict = dict()

    items = items_on_sell()['items']

    if items:
        for item in buy_history_data:
            data = item.split("/")
            name = data[0]
            price = data[1]
            buy_price = int(float(price)*YUAN)
            buy_history_dict[name] = buy_price
        for i in items:
            if (i['market_hash_name'] in ['StatTrak™ AK-47 | Blue Laminate (Field-Tested)'] or
                i['status'] in ['2', '3', '4']):
                ...
            else:
                if buy_history_dict.get(i['market_hash_name']):
                    Items(i['market_hash_name'],
                        i['item_id'], i['price'],
                        buy_history_dict[i['market_hash_name']]*ratio)
                else:
                    Items(i['market_hash_name'], i['item_id'], i['price'])
    

def get_list_of_actual_items(list_of_hash_names):
    
    if len(list_of_hash_names)>50:

        middle_index = len(list_of_hash_names) // 2

        first_half = list_of_hash_names[:middle_index]
        second_half = list_of_hash_names[middle_index:]

        request1 = requests.get(get_request('search-list-items-by-hash-name-all'),
                        params=get_params(item_name=first_half))
        request2 = requests.get(get_request('search-list-items-by-hash-name-all'),
                        params=get_params(item_name=second_half))
            
        while not (
            request1.headers["content-type"].strip().startswith("application/json") and
            request1.status_code == 200 and
            request2.headers["content-type"].strip().startswith("application/json") and
            request2.status_code == 200
            ):
            try:
                request1 = requests.get(get_request('search-list-items-by-hash-name-all'),
                        params=get_params(item_name=first_half))
                request2 = requests.get(get_request('search-list-items-by-hash-name-all'),
                        params=get_params(item_name=second_half))
            except:
                print('Не удалось получить список предметов, хз что не то')
                sleep(3) #пока самый продвинутый вариант решения ошибки

        final_list = request1.json()['data']
        final_list.update(request2.json()['data'])
        return final_list

    else:
        final_list = requests.get(get_request('search-list-items-by-hash-name-all'),
                            params=get_params(item_name=list_of_hash_names))

        while not (
            final_list.headers["content-type"].strip().startswith("application/json") and
            final_list.status_code == 200
        ):
            try:
                final_list = requests.get(get_request('search-list-items-by-hash-name-all'),
                            params=get_params(item_name=list_of_hash_names))
            except:
                print('Не удалось получить список предметов, хз что не то')
                sleep(3) #пока самый продвинутый вариант решения ошибки
        return final_list.json()['data']


def change_prices():
    if not Items.items:
        sleep(0.3)
        create_item_objects()
    if not name_of_selling_items:
        for i in Items.items:
            name_of_selling_items.append(i.name)

    list_of_actual_items = get_list_of_actual_items(name_of_selling_items)
    for skin in Items.items:
        sleep(0.3)
        list_of_same_item_data = list_of_actual_items[skin.name]
        
        first_item = list_of_same_item_data[0]
        second_item = list_of_same_item_data[1]

        second_price = int(second_item['price'])
        first_id = str(first_item['id'])
        first_price = int(first_item['price'])

        print(f'Название предмета {skin.name} --  {skin.id} -- цена {skin.price} минимальная цена {skin.min_price}\n'
              f'Минимальная цена на маркете {first_price/100} -- {first_id}, Вторая цена {second_price/100}')

        if (first_id == skin.id and skin.price == second_price-1) or (skin.price == skin.min_price and first_id != skin.id):
            ...
        elif skin.price < skin.min_price:
            new_price = skin.min_price
            try:
                requests.get(get_request('set-price'),
                                params = get_params(item_name=skin.name, item_id=skin.id, price=new_price))
                print(f'Установил минимальную цену на {skin.name} {new_price/100}')
                skin.price = new_price
            except:
                print("Сетевая ошибка")
        elif first_id == skin.id:
            new_price = second_price-1
            try:
                requests.get(get_request('set-price'),
                                params = get_params(item_name=skin.name, item_id=skin.id, price=new_price))
                print(f'Поменял цену {skin.name} с {skin.price/100} на {new_price/100}')
                skin.price = new_price
            except:
                print("Сетевая ошибка")
        elif first_id != skin.id and first_price <= skin.min_price and skin.price != skin.min_price:
            new_price = skin.min_price
            try:
                request = requests.get(get_request('set-price'),
                            params = get_params(item_name=skin.name, item_id=skin.id, price=new_price))
                print(f'Установил минимальную цену {new_price/100} для {skin.name}')
                skin.price = new_price
                print(skin.price)
            except:
                print('Не удалось сменить цену')
                print(request)
        elif first_id != skin.id and first_price > skin.min_price and skin.price != skin.min_price:
            new_price = first_price-1
            try:
                request = requests.get(get_request('set-price'),
                            params = get_params(item_name=skin.name, item_id=skin.id, price=new_price))
                print(f'Поменял цену {skin.name} с {skin.price/100} на {new_price/100}')
                skin.price = new_price
                print(skin.price)
            except:
                print("Сетевая ошибка")
                print(request)


def put_on_sale():
    list_on_sell = []
    items_already_on_sale = items_on_sell()['items']
    if items_already_on_sale != None:
        for item in items_already_on_sale:
            list_on_sell.append(item['market_hash_name'])
    request = requests.get(get_request('my-inventory'),
                           params={
                                'key':API_KEY,
                            }).json()['items']
    dict_add_to_sell = dict()
    for item in request:
        if item['market_hash_name'] not in list_on_sell and item['tradable']==1:
            dict_add_to_sell[item['market_hash_name']]=item['id']
    for item in dict_add_to_sell:
        request = requests.get(get_request('add-to-sale'),
                               params={
                                    'id':dict_add_to_sell[item],
                                    'cur':CURRENCY,
                                    'price':9999900,
                                    'key':API_KEY,
                               })
        if request.status_code == 502:
            print(f'Ошибка 502 bad gateway --- {request.text}')
            print('Пробуем выставить снова')
            count = 0
            while count < 3:
                request = requests.get(get_request('add-to-sale'),
                               params={
                                    'id':dict_add_to_sell[item],
                                    'cur':CURRENCY,
                                    'price':9999900,
                                    'key':API_KEY,
                               })
                if request.status_code == 200:
                    print(f'Все же удалось выставить вещь с {count+2} раза')
                    break
                count += 1
                sleep(1)
        if request.json()['success']==True:
            print(f'Успешно добавлен предмет {item} на продажу')

def auto_buy():
        path = 'filters.txt'
        try:
            filters = open(path, 'r', encoding='utf-8')
        except:
            print(f"Такого файла по пути {path} не существует")
        
        filters_data = filters.readlines()

        list_of_names = []
        
        for line in filters_data:
            data = line.split("/")
            name = data[0]

            if name not in list_of_names:
                list_of_names.append(name)
        for i in range(1500000):
            sleep(1)
            actual_data_for_items_list = get_list_of_actual_items(list_of_names)
            for line in filters_data:
                data = line.split("/")
                name = data[0]


                try:
                    min_float = float(data[1])
                except:
                    min_float = 0
                
                try:
                    max_float = float(data[2])
                except:
                    max_float = 1
                
                try:
                    max_price = float(data[3])*100
                except:
                    max_price = 999999999

                
                try:
                    phase_filter = data[4].strip()
                    if phase_filter not in phase_list:
                        phase_filter = None
                except:
                    phase_filter = None
                
                
                
                if len(actual_data_for_items_list)==0:
                    print('Нету предметов по заданным именам')
                    break
                
                item_exists = 1
                try:
                    actual_item_data = actual_data_for_items_list[name]
                except KeyError:
                    item_exists = 0

                if item_exists == 1:
                    for item in actual_item_data:
                        item_id = item['id']
                        item_price = int(item['price'])
                        item_phase = item['extra'].get('phase')
                        

                        float_of_item_on_market = item['extra'].get('float')
                        if float_of_item_on_market != None and phase_filter != None:
                            float_of_item_on_market = float(item['extra'].get('float'))

                            if (item_price <= max_price and
                                min_float <= float_of_item_on_market <= max_float and
                                item_phase == phase_filter):
                                print(f'Название: {name}|| {item_phase}\n'
                                    f'Цена: {item_price/100} Флоат: {float_of_item_on_market}\n'
                                    f'ID: {item_id}\n')
                                
                        if float_of_item_on_market != None and phase_filter == None:
                            float_of_item_on_market = float(item['extra'].get('float'))

                            if (item_price <= max_price and
                                min_float <= float_of_item_on_market <= max_float):
                                print(f'Название: {name}\n'
                                    f'Цена: {item_price/100} Флоат: {float_of_item_on_market}\n'
                                    f'ID: {item_id}\n')
                            
                                #if item_price < 2000000:
                                #        link = f'https://market.csgo.com/api/v2/buy?key={API_KEY}&id={item_id}&price={item_price}'
                                #        request = requests.get(link)
                                #        sleep(0.3)
                                #        print(request.json())
                        
                        if float_of_item_on_market == None and phase_filter != None:

                            if (item_price <= max_price and
                                item_phase == phase_filter):
                                print(f'Название: {name}|| {item_phase}\n'
                                    f'Цена: {item_price/100}\n'
                                    f'ID: {item_id}\n')

                        
                        if float_of_item_on_market == None and phase_filter == None:
                            if max_float==1 and min_float==0 and item_price <= max_price:
                                print(f'Название: {name}\n'
                                    f'Цена: {item_price/100}\n'
                                    f'ID: {item_id}\n')
                                
                                if item_price < 40000:
                                    link = f'https://market.csgo.com/api/v2/buy?key={API_KEY}&id={item_id}&price={item_price}'
                                    request = requests.get(link)
                                    sleep(0.3)
                            
                    


def main():
    type_action = input(
        "Выберите действие:\n[1] Выставить предметы на продажу\n[2] Обновление цен\n"
        "[3] Найти вещи по фильтрам\n")
    
    if '1' in type_action:
        ping()
        put_on_sale()
    
    if '2' in type_action:
        while True:
            ping()
            for i in range(10):
                change_prices()
                print('Круг смены цен закончен')
                sleep(0.4)
            name_of_selling_items = []
            Items.items = []
            sleep(0.4)
    
    if '3' in type_action:
        auto_buy()

                
                




    if type_action not in ['1', '2', '3']:
        main()

if __name__ == "__main__":
    main()