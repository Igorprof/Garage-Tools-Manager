from dataclasses import dataclass, asdict
from typing import List, Type
import json

CONFIG_FILE = './settings/settings.json'
DATABASE_FILE = './data.xlsx'

@dataclass
class Settings:
    start: str
    add_words: List[str]
    delete_words: List[str]
    stop_word: str
    search_words: List[str]
    allowed_users: List[str]
    pause: float
    speed_index: int
    rent_word: str

    @classmethod
    def from_dict(cls: Type['Settings'], obj: dict):        
        return cls(**obj)
    
    @classmethod
    def from_json(cls: Type['Settings'], config_file: str = CONFIG_FILE):
        data = json.load(open(config_file, 'r', encoding='utf-8'))
        return cls.from_dict(data)
    
    def save(self, config_file: str = CONFIG_FILE):
        json.dump(asdict(self), open(config_file, 'w', encoding='utf-8'), indent=4)

    def update(self, config_file: str = CONFIG_FILE):
        data = json.load(open(config_file, 'r', encoding='utf-8'))
        for key in data:
            setattr(self, key, data[key])
