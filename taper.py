import pygame as py
import os
import json
import base64
import hashlib

py.init()

TARGET_RECT = py.Rect(72, 210, 256, 256)
SHOP_BUTTON_RECT = py.Rect(110, 520, 182, 67)
DEFAULT_THEME_RECT = py.Rect(28, 168, 96, 96)
BS_THEME_RECT = py.Rect(152, 168, 96, 96)
MINE_THEME_RECT = py.Rect(276, 168, 96, 96)
CLOSE_SHOP_RECT = py.Rect(362, 118, 24, 24)

SAVE_FILE = 'assets/player_data.dat'
SALT = b'taper_game_salt'

screen = py.display.set_mode((400, 600))
py.display.set_caption('Taper')

font_40 = py.font.Font('assets/fonts/default/OpenSans-SemiBold.ttf', 40)
font_22 = py.font.Font('assets/fonts/default/OpenSans-SemiBold.ttf', 22)
font_10 = py.font.Font('assets/fonts/default/OpenSans-SemiBold.ttf', 10)

bs_buy = font_22.render('10000', True, 'Black')
mine_buy = font_10.render('9999999999999', True, 'Black')

def encrypt_data(data):
    json_data = json.dumps(data)
    encrypted = base64.b64encode(json_data.encode('utf-8')).decode('utf-8')
    checksum = hashlib.sha256(SALT + json_data.encode('utf-8')).hexdigest()[:16]
    return encrypted + "." + checksum

def decrypt_data(encrypted_data):
    try:
        parts = encrypted_data.split(".")
        if len(parts) != 2:
            return get_default_data()
        
        encrypted, checksum = parts
        
        json_data = base64.b64decode(encrypted.encode('utf-8')).decode('utf-8')
        
        expected_checksum = hashlib.sha256(SALT + json_data.encode('utf-8')).hexdigest()[:16]
        if checksum != expected_checksum:
            print("Предупреждение: файл сохранения был изменен. Сброс данных.")
            return get_default_data()
        
        return json.loads(json_data)
    except Exception as e:
        print(f"Ошибка при чтении данных: {e}")
        return get_default_data()

def get_default_data():
    return {
        "money": 0,
        "themes": {
            "default": True,
            "brawlstars": False,
            "minecraft": False
        }
    }

def load_player_data():
    if not os.path.exists(SAVE_FILE):
        data = get_default_data()
        save_player_data(data)
        return data
    
    with open(SAVE_FILE, 'r') as file:
        encrypted_data = file.read().strip()
        return decrypt_data(encrypted_data)

def save_player_data(data):
    encrypted_data = encrypt_data(data)
    os.makedirs(os.path.dirname(SAVE_FILE), exist_ok=True)
    with open(SAVE_FILE, 'w') as file:
        file.write(encrypted_data)

def get_money():
    data = load_player_data()
    return data["money"]

def set_money(value):
    data = load_player_data()
    data["money"] = value
    save_player_data(data)

def is_theme_owned(theme_name):
    data = load_player_data()
    return data["themes"].get(theme_name, False)

def set_theme_owned(theme_name, owned=True):
    data = load_player_data()
    data["themes"][theme_name] = owned
    save_player_data(data)

def load_theme(theme_name):
    theme_path = f'assets/themes/{theme_name}'
    return {
        'background': py.image.load(f'{theme_path}/background.png').convert(),
        'target': py.image.load(f'{theme_path}/target.png').convert_alpha(),
        'money': py.image.load(f'{theme_path}/money.png').convert_alpha(),
        'money_small': py.image.load(f'{theme_path}/money_small.png').convert_alpha()
    }

themes = {
    'default': load_theme('default'),
    'brawlstars': load_theme('brawlstars'),
    'minecraft': load_theme('minecraft')
}

shop_img = py.image.load('assets/shop.png').convert_alpha()
themes_button = py.image.load('assets/themes-button.png').convert_alpha()
icon = py.image.load('assets/icon.png').convert_alpha()

py.display.set_icon(icon)

current_theme = 'default'
money = get_money()
shop = False
clock = py.time.Clock()
shop_pos = (-1000, -1000)
shop_elements = {
    'money1': (-1000, -1000),
    'money2': (-1000, -1000),
    'price1': (-1000, -1000),
    'price2': (-1000, -1000)
}

game = True
while game:
    mouse_pos = py.mouse.get_pos()
    mouse_click = False
    
    for e in py.event.get():
        if e.type == py.QUIT:
            game = False
        elif e.type == py.MOUSEBUTTONUP:
            mouse_click = True
    
    if mouse_click:
        if not shop and TARGET_RECT.collidepoint(mouse_pos):
            money = get_money()
            money_str = str(money)
            money_len = len(money_str)
            
            reward = 10 ** (money_len - 3) if money_len >= 4 else 1
            money += reward
            set_money(money)
            
        elif not shop and SHOP_BUTTON_RECT.collidepoint(mouse_pos):
            shop = True
            shop_pos = (0, 99)
            
            bs_theme_owned = is_theme_owned('brawlstars')
            mine_theme_owned = is_theme_owned('minecraft')
            
            if not bs_theme_owned:
                shop_elements['money1'] = (152, 325)
                shop_elements['price1'] = (170, 317)
            else:
                shop_elements['money1'] = (-1000, -1000)
                shop_elements['price1'] = (-1000, -1000)
                
            if not mine_theme_owned:
                shop_elements['money2'] = (276, 310)
                shop_elements['price2'] = (294, 310)
            else:
                shop_elements['money2'] = (-1000, -1000)
                shop_elements['price2'] = (-1000, -1000)
                
        elif shop and DEFAULT_THEME_RECT.collidepoint(mouse_pos):
            current_theme = 'default'
            
        elif shop and BS_THEME_RECT.collidepoint(mouse_pos):
            bs_theme_owned = is_theme_owned('brawlstars')
            if bs_theme_owned:
                current_theme = 'brawlstars'
                shop_elements['money1'] = (-1000, -1000)
                shop_elements['price1'] = (-1000, -1000)
            else:
                money = get_money()
                if money >= 10000:
                    set_theme_owned('brawlstars', True)
                    money -= 10000
                    set_money(money)
                    current_theme = 'brawlstars'
                    shop_elements['money1'] = (-1000, -1000)
                    shop_elements['price1'] = (-1000, -1000)
                    
        elif shop and MINE_THEME_RECT.collidepoint(mouse_pos):
            mine_theme_owned = is_theme_owned('minecraft')
            if mine_theme_owned:
                current_theme = 'minecraft'
                shop_elements['money2'] = (-1000, -1000)
                shop_elements['price2'] = (-1000, -1000)
            else:
                money = get_money()
                if money >= 9999999999999:
                    set_theme_owned('minecraft', True)
                    money -= 9999999999999
                    set_money(money)
                    current_theme = 'minecraft'
                    shop_elements['money2'] = (-1000, -1000)
                    shop_elements['price2'] = (-1000, -1000)
                    
        elif shop and CLOSE_SHOP_RECT.collidepoint(mouse_pos):
            shop = False
            shop_pos = (-1000, -1000)
            for key in shop_elements:
                shop_elements[key] = (-1000, -1000)
    
    current_assets = themes[current_theme]
    screen.blit(current_assets['background'], (0, 0))
    screen.blit(current_assets['target'], (72, 210))
    screen.blit(themes_button, (110, 520))
    
    screen.blit(shop_img, shop_pos)
    screen.blit(themes['default']['money_small'], shop_elements['money1'])
    screen.blit(themes['default']['money_small'], shop_elements['money2'])
    screen.blit(bs_buy, shop_elements['price1'])
    screen.blit(mine_buy, shop_elements['price2'])
    
    money_str = str(get_money())
    money_len = len(money_str)
    counter = font_40.render(money_str, True, 'Black')
    
    if int(money_str) < 10:
        screen.blit(current_assets['money'], (162, 25))
        screen.blit(counter, (220, 20))
    else:
        x_pos = 200 - ((48 + 8 + 19 * money_len + 2 * (money_len - 1)) / 2)
        screen.blit(current_assets['money'], (x_pos, 25))
        screen.blit(counter, (x_pos + 48 + 8, 20))
    
    py.display.update()
    clock.tick(60)
    
py.quit()
