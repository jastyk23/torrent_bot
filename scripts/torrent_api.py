from typing import Any, Optional, Type

import aiohttp
import requests
import asyncio


class Client(object):
    def __init__(self, query: str = '', tracker_list: list = None):
        """
        Клиент поиска торрентов и получения magnet ссылок на exfreedomist.com
        :param query: Строка поиска
        :param tracker_list: Трекеры по которым искать
        """
        self._session: Optional[aiohttp.ClientSession] = None
        self._connector_class: Type[aiohttp.TCPConnector] = aiohttp.TCPConnector
        self._connector_init = dict(limit=10, ssl=False)
        self.query = query
        self.page = 0
        self.url_host = 'https://api.exfreedomist.com'  # мейн домен
        self.url_search = '/search'  # поиск
        self.url_search_count = '/search_count'  # найдено результатов
        self.url_infohash = '/infohash/'
        self.url_magnet = '/magnet/'
        self.url_board = '/board/'
        self.url_trackers = '/trackers'
        self.tracker_list = [] if tracker_list is None else tracker_list
        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }

    def set_page(self, page: int) -> None:
        self.page = page

    async def _get_new_session(self) -> aiohttp.ClientSession:
        """
        Новое подключение aiohttp
        :return: сессия подключения
        """
        return aiohttp.ClientSession(
            connector=self._connector_class(**self._connector_init)
        )

    async def _get_session(self) -> Optional[aiohttp.ClientSession]:
        """
        Проверяет дохлые сессии
        :return:
        """
        if self._session is None or self._session.closed:
            self._session = await self._get_new_session()

        if not self._session._loop.is_running():
            await self._session.close()
            self._session = await self._get_new_session()
        return self._session

    async def __get_board_info(self, board_id: int, tracker: str, session) -> str | int:
        """
        Получение информации о разделе торрента по id
        :param board_id: id раздела торрента
        :param tracker: названия трекера
        :param session: сессия подклоючения aiohttp
        :return: название раздела торрента
        """
        async with session.get(self.url_host + self.url_board + str(board_id) + f'?tracker={tracker}') as resp:
            match resp.status:
                case 200:
                    item = await resp.json()
                    return item['board_label']
                case 429:
                    return board_id
                case _:
                    raise ConnectionError(resp.status)

    async def __mutate_item(self, item: dict) -> dict:
        """
        Замена border_id на border_name
        :param item: информация торрента
        :return: исправленный словарь
        """
        item['board_name'] = await self.__get_board_info(item['board_id'], item['tracker'], await self._get_session())
        del item['board_id']
        return item

    async def __parse_resp(self, data: list) -> Any | None:
        """
        Асинхронный map
        :param data: списко торрентов
        :return:
        """
        try:
            return await asyncio.gather(*map(self.__mutate_item, data))
        finally:
            await self._session.close()

    def get_trackers(self) -> list:
        """
        Получает название трекеров
        :return:
        """
        resp = requests.get(self.url_host + self.url_trackers, headers=self.headers, verify=False).json()
        return resp['data']

    def search(self, count: bool = False) -> Any | None:
        """
        Поиск трекеров
        :param count: True | False
        :return: если count == True возвращает число найденных торрентов
        """
        req_data = {
            "query": self.query,
            "trackers": self.tracker_list,
            "order_by": "d",
            "filter_by_size": "",
            "limit": 5,
            "offset": self.page,
            "full_match": False,
        }
        if count:
            resp = requests.post(url=self.url_host + self.url_search_count, json=req_data, headers=self.headers,
                                 verify=False).json()
            return resp['size']
        else:
            resp = requests.post(url=self.url_host + self.url_search, json=req_data, headers=self.headers,
                                 verify=False).json()
            data = list(map(lambda x: {key: x[key] for key in x if key not in ['metric', 'topic_id', 'index_date']},
                            resp['data']))
            return asyncio.run(self.__parse_resp(data))

    def get_link(self, key: str) -> str:
        """
        Получение ссылки по ключу
        :param key:
        :return:
        """
        resp = requests.get(self.url_host + self.url_magnet + key, headers=self.headers, verify=False).json()
        return resp['data']['magnet_link']

    def get_infohash(self, key: str) -> str:
        """
        Н/Д
        :param key:
        :return:
        """
        resp = requests.get(self.url_host + self.url_infohash + key, headers=self.headers, verify=False).json()
        return resp['data']
