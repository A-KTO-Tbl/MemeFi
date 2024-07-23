from requests import post
from threading import Thread, Lock
from os import system as sys
from platform import system as s_name
from time import sleep
from random import randint, uniform
from colorama import Fore
from typing import Literal
from datetime import datetime, timedelta
from json import loads
from urllib.parse import unquote
from itertools import cycle

from Core.Tools.HPV_Getting_File_Paths import HPV_Get_Accounts
from Core.Tools.HPV_Proxy import HPV_Proxy_Checker
from Core.Tools.HPV_User_Agent import HPV_User_Agent

from Core.Config.HPV_Config import *







class HPV_MemeFi:
    '''
    AutoBot Ferma /// HPV
    ---------------------
    [1] - `Улучшение бустов`
        [1.1] - `Попытка улучшить буст 'Damage' (урон за один тап)`
        
        [1.2] - `Попытка улучшить буст 'EnergyCap' (максимальная ёмкость энергии)`
        
        [1.3] - `Попытка улучшить буст 'EnergyRechargeRate' (скорость восстановления энергии)`
        
        
    [2] - `Попытка апгрейда текущего босса`
    
    
    [3] - `Взаимодействие с TapBot`
        [3.1] - `Если TapBot уже приобретен - происходит сбор монет и перезапуск бота`
            [3.1.1] - `Сбор монет, собранных с помощью TapBota`
            
            [3.1.2] - `Запуск TapBota`
            
            [3.1.3] - `Ожидание от 3 до 4 часов`
            
            [3.1.4] - `Повторение действий 3 раза через каждые 3-4 часов`
            
        [3.2] - `Если TapBot отсутствует - происходит его приобретение`
            [3.2.1] - `Покупка TapBot`
    
            
    [4] - `Ожидание от 5 до 6 часов`
    
    
    [5] - `Повторение действий через 5-6 часов`
    '''



    def __init__(self, Name: str, URL: str, Proxy: dict) -> None:
        self.Domain = 'https://api-gw-tg.memefi.club/graphql' # Домен игры
        self.Name = Name                     # Ник аккаунта
        self.URL = URL                       # Уникальная ссылка для авторизации в mini app
        self.Proxy = Proxy                   # Прокси (при наличии)
        self.UA = HPV_User_Agent()           # Генерация уникального User Agent
        self.Token = self.Authentication()   # Токен аккаунта



    def URL_Clean(self, URL: str) -> str:
        '''Очистка уникальной ссылки от лишних элементов'''

        try:
            return unquote(URL.split('#tgWebAppData=')[1].split('&tgWebAppVersion')[0])
        except:
            return ''



    def Current_Time(self) -> str:
        '''Текущее время'''

        return Fore.BLUE + f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'



    def Logging(self, Type: Literal['Success', 'Warning', 'Error'], Name: str, Smile: str, Text: str) -> None:
        '''Логирование'''

        with Console_Lock:
            COLOR = Fore.GREEN if Type == 'Success' else Fore.YELLOW if Type == 'Warning' else Fore.RED # Цвет текста
            DIVIDER = Fore.BLACK + ' | '   # Разделитель

            Time = self.Current_Time()     # Текущее время
            Name = Fore.MAGENTA + Name     # Ник аккаунта
            Smile = COLOR + str(Smile)     # Смайлик
            Text = COLOR + Text            # Текст лога

            print(Time + DIVIDER + Smile + DIVIDER + Text + DIVIDER + Name)



    def Authentication(self) -> str:
        '''Аутентификация аккаунта'''

        URL = unquote(unquote(unquote(self.URL.split('#tgWebAppData=')[1].split('&tgWebAppVersion')[0]))).split('&')

        _query_id = URL[0].split('=')[1]
        _user = loads(URL[1].split('=')[1])
        _user_str = URL[1].split('=')[1]
        _auth_date = URL[2].split('=')[1]
        _hash = URL[3].split('=')[1]

        try:username = _user['username']
        except:username = ''

        Headers = {'User-Agent': self.UA, 'Content-Type': 'application/json', 'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Android WebView";v="122"', 'sec-ch-ua-mobile': '?1', 'sec-ch-ua-platform': '"Android"', 'origin': 'https://tg-app.memefi.club', 'x-requested-with': 'org.telegram.messenger', 'sec-fetch-site': 'same-site', 'sec-fetch-mode': 'cors', 'sec-fetch-dest': 'empty', 'referer': 'https://tg-app.memefi.club/', 'accept-language': 'ru,ru-RU;q=0.9,en-US;q=0.8,en;q=0.7'}
        Json = {'operationName': 'MutationTelegramUserLogin', 'variables': {'webAppData': {'auth_date': int(_auth_date), 'hash': _hash, 'query_id': _query_id, 'checkDataString': 'auth_date=' + _auth_date + '\nquery_id=' + _query_id + '\nuser=' + _user_str, 'user': {'id': _user['id'], 'allows_write_to_pm': True, 'first_name': _user['first_name'], 'last_name': _user['last_name'], 'username': username, 'language_code': _user['language_code'], 'version': '7.4', 'platform': 'android'}}}, 'query': 'mutation MutationTelegramUserLogin($webAppData: TelegramWebAppDataInput!) {\n  telegramUserLogin(webAppData: $webAppData) {\n    access_token\n    __typename\n  }\n}'}

        try:
            Token = post(self.Domain, headers=Headers, json=Json, proxies=self.Proxy).json()['data']['telegramUserLogin']['access_token']
            self.Logging('Success', self.Name, '🟢', 'Инициализация успешна!')
            return Token
        except:
            self.Logging('Error', self.Name, '🔴', 'Ошибка инициализации!')
            return ''



    def ReAuthentication(self) -> None:
        '''Повторная аутентификация аккаунта'''

        self.Token = self.Authentication()



    def Get_Info(self) -> dict:
        '''Получение информации об игроке'''

        Headers = {'authority': 'api-gw-tg.memefi.club', 'accept': '*/*', 'accept-language': 'ru,en;q=0.9,uz;q=0.8', 'authorization': f'Bearer {self.Token}', 'content-type': 'application/json', 'origin': 'https://tg-app.memefi.club', 'referer': 'https://tg-app.memefi.club/', 'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "YaBrowser";v="24.4", "Yowser";v="2.5"', 'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Windows"', 'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-site', 'user-agent': self.UA}
        Json = {'operationName': 'QUERY_GAME_CONFIG', 'variables': {}, 'query': 'query QUERY_GAME_CONFIG {\n  telegramGameGetConfig {\n    ...FragmentBossFightConfig\n    __typename\n  }\n}\n\nfragment FragmentBossFightConfig on TelegramGameConfigOutput {\n  _id\n  coinsAmount\n  currentEnergy\n  maxEnergy\n  weaponLevel\n  zonesCount\n  tapsReward\n  energyLimitLevel\n  energyRechargeLevel\n  tapBotLevel\n  currentBoss {\n    _id\n    level\n    currentHealth\n    maxHealth\n    __typename\n  }\n  freeBoosts {\n    _id\n    currentTurboAmount\n    maxTurboAmount\n    turboLastActivatedAt\n    turboAmountLastRechargeDate\n    currentRefillEnergyAmount\n    maxRefillEnergyAmount\n    refillEnergyLastActivatedAt\n    refillEnergyAmountLastRechargeDate\n    __typename\n  }\n  bonusLeaderDamageEndAt\n  bonusLeaderDamageStartAt\n  bonusLeaderDamageMultiplier\n  nonce\n  __typename\n}'}

        try:
            HPV = post(self.Domain, headers=Headers, json=Json, proxies=self.Proxy).json()['data']['telegramGameGetConfig']

            Balance = f'{HPV["coinsAmount"]:,}' # Текущий баланс

            Current_Energy = HPV['currentEnergy'] # Текущая энергия
            Max_Energy = HPV['maxEnergy'] # Максимальная энергия
            Bot = HPV['tapBotLevel'] # Наличие или отсутствие бота
            Tap_LVL = HPV['weaponLevel'] + 1 # Уровень тапа
            Max_Energy_LVL = HPV['energyLimitLevel'] + 1 # Уровень максимальной энергии
            Recovery_Rate_LVL = HPV['energyRechargeLevel'] + 1 # Уровень скорости восстановления

            Boss_LVL = HPV['currentBoss']['level'] # Уровень босса
            Boss_Health = HPV['currentBoss']['currentHealth'] # Текущее состояние здоровья босса

            Turbo = HPV['freeBoosts']['currentTurboAmount'] # Кол-во бустов "Turbo"
            Recharge = HPV['freeBoosts']['currentRefillEnergyAmount'] # Кол-во бустов "Recharge"

            return {'Balance': Balance, 'Current_Energy': Current_Energy, 'Max_Energy': Max_Energy, 'Bot': Bot, 'Tap_LVL': Tap_LVL, 'Max_Energy_LVL': Max_Energy_LVL, 'Recovery_Rate_LVL': Recovery_Rate_LVL, 'Boss_LVL': Boss_LVL, 'Boss_Health': Boss_Health, 'Turbo': Turbo, 'Recharge': Recharge}
        except:
            return None



    def Get_Bots(self) -> int:
        '''Получение кол-ва доступных ботов'''

        URL = 'https://api-gw-tg.memefi.club/graphql'
        Headers = {'accept': '*/*', 'accept-language': 'ru,en;q=0.9,uz;q=0.8', 'authorization': f'Bearer {self.Token}', 'content-type': 'application/json', 'origin': 'https://tg-app.memefi.club', 'priority': 'u=1, i', 'referer': 'https://tg-app.memefi.club/', 'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-site', 'user-agent': self.UA}
        Json = {'operationName': 'TapbotConfig', 'variables': {}, 'query': 'fragment FragmentTapBotConfig on TelegramGameTapbotOutput {\n  damagePerSec\n  endsAt\n  id\n  isPurchased\n  startsAt\n  totalAttempts\n  usedAttempts\n  __typename\n}\n\nquery TapbotConfig {\n  telegramGameTapbotGetConfig {\n    ...FragmentTapBotConfig\n    __typename\n  }\n}'}

        try:
            return 3 - post(URL, headers=Headers, json=Json, proxies=self.Proxy).json()['data']['telegramGameTapbotGetConfig']['usedAttempts']
        except:
            return 0



    def Buy_TapBot(self) -> None:
        '''Покупка TapBot, если он ещё не приобретён'''

        Headers = {'authority': 'api-gw-tg.memefi.club', 'accept': '*/*', 'accept-language': 'ru,en;q=0.9,uz;q=0.8', 'authorization': f'Bearer {self.Token}', 'content-type': 'application/json', 'origin': 'https://tg-app.memefi.club', 'referer': 'https://tg-app.memefi.club/', 'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "YaBrowser";v="24.4", "Yowser";v="2.5"', 'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Windows"', 'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-site', 'user-agent': self.UA}
        Json = {'operationName': 'telegramGamePurchaseUpgrade', 'variables': {'upgradeType': 'TapBot'}, 'query': 'mutation telegramGamePurchaseUpgrade($upgradeType: UpgradeType!) {\n  telegramGamePurchaseUpgrade(type: $upgradeType) {\n    ...FragmentBossFightConfig\n    __typename\n  }\n}\n\nfragment FragmentBossFightConfig on TelegramGameConfigOutput {\n  _id\n  coinsAmount\n  currentEnergy\n  maxEnergy\n  weaponLevel\n  zonesCount\n  tapsReward\n  energyLimitLevel\n  energyRechargeLevel\n  tapBotLevel\n  currentBoss {\n    _id\n    level\n    currentHealth\n    maxHealth\n    __typename\n  }\n  freeBoosts {\n    _id\n    currentTurboAmount\n    maxTurboAmount\n    turboLastActivatedAt\n    turboAmountLastRechargeDate\n    currentRefillEnergyAmount\n    maxRefillEnergyAmount\n    refillEnergyLastActivatedAt\n    refillEnergyAmountLastRechargeDate\n    __typename\n  }\n  bonusLeaderDamageEndAt\n  bonusLeaderDamageStartAt\n  bonusLeaderDamageMultiplier\n  nonce\n  __typename\n}'}

        try:
            HPV = post(self.Domain, headers=Headers, json=Json, proxies=self.Proxy)

            try:
                HPV.json()['data']['telegramGamePurchaseUpgrade']['tapBotLevel']
                self.Logging('Success', self.Name, '🟢', 'TapBot куплен!')
            except:
                Message = HPV.json()['errors'][0]['message']
                if Message == 'You don\'t have enough coins to purchase this upgrade':
                    self.Logging('Warning', self.Name, '🟡', 'Не удалось купить TapBot! Недостаточно монет!')
        except:
            self.Logging('Error', self.Name, '🔴', 'Не удалось купить TapBot!')



    def TapBot_Collection(self) -> None:
        '''Сбор монет, собранных с помощью TapBota'''

        Headers = {'authority': 'api-gw-tg.memefi.club', 'accept': '*/*', 'accept-language': 'ru,en;q=0.9,uz;q=0.8', 'authorization': f'Bearer {self.Token}', 'content-type': 'application/json', 'origin': 'https://tg-app.memefi.club', 'referer': 'https://tg-app.memefi.club/', 'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "YaBrowser";v="24.4", "Yowser";v="2.5"', 'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Windows"', 'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-site', 'user-agent': self.UA}
        Json = {'operationName': 'TapbotClaim', 'variables': {}, 'query': 'fragment FragmentTapBotConfig on TelegramGameTapbotOutput {\n  damagePerSec\n  endsAt\n  id\n  isPurchased\n  startsAt\n  totalAttempts\n  usedAttempts\n  __typename\n}\n\nmutation TapbotClaim {\n  telegramGameTapbotClaimCoins {\n    ...FragmentTapBotConfig\n    __typename\n  }\n}'}

        try:
            post(self.Domain, headers=Headers, json=Json, proxies=self.Proxy).json()['data']['telegramGameTapbotClaimCoins']['damagePerSec']
            self.Logging('Success', self.Name, '🟢', 'Монеты с TapBot собраны!')
        except:
            self.Logging('Error', self.Name, '🔴', 'Не удалось собрать монеты с TapBot!')



    def TapBot_Start(self) -> None:
        '''Запуск TapBota'''

        Headers = {'authority': 'api-gw-tg.memefi.club', 'accept': '*/*', 'accept-language': 'ru,en;q=0.9,uz;q=0.8', 'authorization': f'Bearer {self.Token}', 'content-type': 'application/json', 'origin': 'https://tg-app.memefi.club', 'referer': 'https://tg-app.memefi.club/', 'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "YaBrowser";v="24.4", "Yowser";v="2.5"', 'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Windows"', 'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-site', 'user-agent': self.UA}
        Json = {'operationName': 'TapbotStart', 'variables': {}, 'query': 'fragment FragmentTapBotConfig on TelegramGameTapbotOutput {\n  damagePerSec\n  endsAt\n  id\n  isPurchased\n  startsAt\n  totalAttempts\n  usedAttempts\n  __typename\n}\n\nmutation TapbotStart {\n  telegramGameTapbotStart {\n    ...FragmentTapBotConfig\n    __typename\n  }\n}'}

        try:
            post(self.Domain, headers=Headers, json=Json, proxies=self.Proxy).json()['data']['telegramGameTapbotStart']['damagePerSec']
            self.Logging('Success', self.Name, '🟢', 'TapBot запущен!')
        except:
            self.Logging('Error', self.Name, '🔴', 'Не удалось запустить TapBot!')



    def Update_Boosts(self, UP_Type: Literal['Damage', 'EnergyCap', 'EnergyRechargeRate']) -> bool:
        '''Обновление бустов'''

        Headers = {'accept': '*/*', 'accept-language': 'ru,en;q=0.9,uz;q=0.8', 'authorization': f'Bearer {self.Token}', 'content-type': 'application/json', 'origin': 'https://tg-app.memefi.club', 'priority': 'u=1, i', 'referer': 'https://tg-app.memefi.club/', 'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-site', 'user-agent': self.UA}
        Json = {'operationName': 'telegramGamePurchaseUpgrade', 'variables': {'upgradeType': UP_Type}, 'query': 'mutation telegramGamePurchaseUpgrade($upgradeType: UpgradeType!) {\n  telegramGamePurchaseUpgrade(type: $upgradeType) {\n    ...FragmentBossFightConfig\n    __typename\n  }\n}\n\nfragment FragmentBossFightConfig on TelegramGameConfigOutput {\n  _id\n  coinsAmount\n  currentEnergy\n  maxEnergy\n  weaponLevel\n  zonesCount\n  tapsReward\n  energyLimitLevel\n  energyRechargeLevel\n  tapBotLevel\n  currentBoss {\n    _id\n    level\n    currentHealth\n    maxHealth\n    __typename\n  }\n  freeBoosts {\n    _id\n    currentTurboAmount\n    maxTurboAmount\n    turboLastActivatedAt\n    turboAmountLastRechargeDate\n    currentRefillEnergyAmount\n    maxRefillEnergyAmount\n    refillEnergyLastActivatedAt\n    refillEnergyAmountLastRechargeDate\n    __typename\n  }\n  bonusLeaderDamageEndAt\n  bonusLeaderDamageStartAt\n  bonusLeaderDamageMultiplier\n  nonce\n  __typename\n}'}

        try:
            post(self.Domain, headers=Headers, json=Json, proxies=self.Proxy).json()['data']['telegramGamePurchaseUpgrade']
            return True
        except:
            return False



    def Update_LVL_Boss(self) -> bool:
        '''Апгрейд босса'''

        Headers = {'accept': '*/*', 'accept-language': 'ru,en;q=0.9,uz;q=0.8', 'authorization': f'Bearer {self.Token}', 'content-type': 'application/json', 'origin': 'https://tg-app.memefi.club', 'priority': 'u=1, i', 'referer': 'https://tg-app.memefi.club/', 'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-site', 'user-agent': self.UA}
        Json = {'operationName': 'telegramGameSetNextBoss', 'variables': {}, 'query': 'mutation telegramGameSetNextBoss {\n  telegramGameSetNextBoss {\n    ...FragmentBossFightConfig\n    __typename\n  }\n}\n\nfragment FragmentBossFightConfig on TelegramGameConfigOutput {\n  _id\n  coinsAmount\n  currentEnergy\n  maxEnergy\n  weaponLevel\n  zonesCount\n  tapsReward\n  energyLimitLevel\n  energyRechargeLevel\n  tapBotLevel\n  currentBoss {\n    _id\n    level\n    currentHealth\n    maxHealth\n    __typename\n  }\n  freeBoosts {\n    _id\n    currentTurboAmount\n    maxTurboAmount\n    turboLastActivatedAt\n    turboAmountLastRechargeDate\n    currentRefillEnergyAmount\n    maxRefillEnergyAmount\n    refillEnergyLastActivatedAt\n    refillEnergyAmountLastRechargeDate\n    __typename\n  }\n  bonusLeaderDamageEndAt\n  bonusLeaderDamageStartAt\n  bonusLeaderDamageMultiplier\n  nonce\n  __typename\n}'}

        try:
            post(self.Domain, headers=Headers, json=Json, proxies=self.Proxy).json()['data']
            return True
        except:
            return False



    def Run(self) -> None:
        '''Активация бота'''

        while True:
            try:
                if self.Token: # Если аутентификация успешна
                    INFO = self.Get_Info()


                    Bot = INFO['Bot'] # Получение информации о наличии или отсутствии бота
                    Balance = INFO['Balance'] # Баланс
                    Boss = INFO['Boss_LVL'] # Уровень босса
                    Boss_Health = INFO['Boss_Health'] # Текущее состояние здоровья босса
                    Turbo, Recharge = INFO['Turbo'], INFO['Recharge'] # Доступное кол-во бустов


                    Tap_LVL = INFO['Tap_LVL'] # Уровень тапа
                    Max_Energy_LVL = INFO['Max_Energy_LVL'] # Уровень максимальной энергии
                    Recovery_Rate_LVL = INFO['Recovery_Rate_LVL'] # Уровень скорости восстановления


                    self.Logging('Success', self.Name, '💰', f'Баланс: {Balance} /// Уровень босса: {Boss}')
                    Changes = 0 # Сколько произошло изменений

                    # Улучшение `Damage` буста (урон за один тап)
                    if Tap_LVL < MAX_DAMAGE_LVL:
                        if self.Update_Boosts('Damage'):
                            self.Logging('Success', self.Name, '⚡️', 'Буст `Damage` улучшен!')
                            Changes += 1 # +1 если буст улучшится
                            sleep(randint(33, 103)) # Промежуточное ожидание

                    # Улучшение `EnergyCap` буста (максимальная ёмкость энергии)
                    if Max_Energy_LVL < MAX_ENERGY_CAP_LVL:
                        if self.Update_Boosts('EnergyCap'):
                            self.Logging('Success', self.Name, '⚡️', 'Буст `EnergyCap` улучшен!')
                            Changes += 1 # +1 если буст улучшится
                            sleep(randint(33, 103)) # Промежуточное ожидание

                    # Улучшение `EnergyRechargeRate` буста (скорость восстановления энергии)
                    if Recovery_Rate_LVL < MAX_RECHARGING_SPEED_LVL:
                        if self.Update_Boosts('EnergyRechargeRate'):
                            self.Logging('Success', self.Name, '⚡️', 'Буст `EnergyRechargeRate` улучшен!')
                            Changes += 1 # +1 если буст улучшится
                            sleep(randint(33, 103)) # Промежуточное ожидание


                    # Попытка апгрейда текущего босса
                    if Boss_Health <= 0:
                        if self.Update_LVL_Boss():
                            self.Logging('Success', self.Name, '👾', 'Текущий босс побеждён! Активирован новый босс!')
                            Changes += 1 # +1 если буст улучшится
                            sleep(randint(33, 103)) # Промежуточное ожидание


                    # Если произошли какие-либо изменения, апгрейд бустов и/или апгрейд босса
                    if Changes:
                        _INFO = self.Get_Info()
                        _Balance, _Boss = _INFO['Balance'], _INFO['Boss_LVL'] # Баланс и Уровень босса
                        self.Logging('Success', self.Name, '💰', f'Баланс: {_Balance} /// Уровень босса: {_Boss}')


                    # Взаимодействие с TapBot
                    if Bot: # Если TapBot уже приобретен - происходит сбор монет и перезапуск бота
                        Get_Bots = self.Get_Bots() # Получение кол-ва доступных ботов
                        for _ in range(Get_Bots):
                            sleep(randint(33, 103)) # Предварительно ожидание
                            self.TapBot_Collection() # Сбор монет, собранных с помощью TapBota

                            sleep(randint(33, 103)) # Промежуточное ожидание
                            self.TapBot_Start() # Запуск TapBota

                            Waiting = randint(11_000, 14_000) # Значение времени в секундах для ожидания
                            Waiting_STR = (datetime.now() + timedelta(seconds=Waiting)).strftime('%Y-%m-%d %H:%M:%S') # Значение времени в читаемом виде

                            self.Logging('Warning', self.Name, '⏳', f'Взаимодействия с ботом окончено, следующее повторение: {Waiting_STR}!')

                            sleep(Waiting) # Ожидание от 3 до 4 часов
                            self.ReAuthentication() # Повторная аутентификация аккаунта

                        sleep(randint(33, 103)) # Промежуточное ожидание
                        self.TapBot_Collection() # Сбор монет, собранных с помощью TapBota

                    else: # Если TapBot отсутствует - происходит его приобретение
                        self.Buy_TapBot()


                    Waiting = randint(18_000, 22_000) # Значение времени в секундах для ожидания
                    Waiting_STR = (datetime.now() + timedelta(seconds=Waiting)).strftime('%Y-%m-%d %H:%M:%S') # Значение времени в читаемом виде

                    self.Logging('Success', self.Name, '💰', f'Баланс: {self.Get_Info()["Balance"]} /// Уровень босса: {self.Get_Info()["Boss_LVL"]}')
                    self.Logging('Warning', self.Name, '⏳', f'Следующий старт сбора монет: {Waiting_STR}!')

                    sleep(Waiting) # Ожидание от 5 до 6 часов
                    self.ReAuthentication() # Повторная аутентификация аккаунта

                else: # Если аутентификация не успешна
                    sleep(randint(33, 66)) # Ожидание от 33 до 66 секунд
                    self.ReAuthentication() # Повторная аутентификация аккаунта
            except:
                pass







if __name__ == '__main__':
    sys('cls') if s_name() == 'Windows' else sys('clear')

    Console_Lock = Lock()
    Proxy = HPV_Proxy_Checker()

    def Start_Thread(Account, URL, Proxy = None):
        MemeFi = HPV_MemeFi(Account, URL, Proxy)
        MemeFi.Run()

    if Proxy:
        DIVIDER = Fore.BLACK + ' | '
        Time = Fore.BLUE + f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
        Text = Fore.GREEN + f'Проверка прокси окончена! Работоспособные: {len(Proxy)}'
        print(Time + DIVIDER + '🌐' + DIVIDER + Text)
        sleep(5)

    try:
        for Account, URL in HPV_Get_Accounts().items():
            if Proxy:
                Proxy = cycle(Proxy)
                Thread(target=Start_Thread, args=(Account, URL, next(Proxy),)).start()
            else:
                Thread(target=Start_Thread, args=(Account, URL,)).start()
    except:
        print(Fore.RED + '\n\tОшибка чтения `HPV_Account.json`, ссылки указаны некорректно!')


