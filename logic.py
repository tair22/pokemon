from random import randint
import requests
import time

class Pokemon:
    pokemons = {}
    
    def __init__(self, pokemon_trainer):
        self.pokemon_trainer = pokemon_trainer   
        self.pokemon_number = randint(1, 1000)
        self.img = self.get_img()
        self.stats = self.get_stats()
        self.name = self.get_name()
        self.abilities = self.get_abilities()
        self.alternative_imgs = self.get_alternative_imgs()

        Pokemon.pokemons[pokemon_trainer] = self

    def make_api_request(self, url):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            print(f"Таймаут запроса к {url}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса: {e}")
            return None

    def get_name(self):
        url = f'https://pokeapi.co/api/v2/pokemon/{self.pokemon_number}'
        data = self.make_api_request(url)
        if data:
            return data['forms'][0]['name']
        else:
            return "Pikachu"
        
    def get_img(self):
        """Получение основной картинки покемона"""
        url = f'https://pokeapi.co/api/v2/pokemon/{self.pokemon_number}'
        data = self.make_api_request(url)
        if data:
            return data['sprites']['other']['official-artwork']['front_default']
        else:
            return "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png"
    
    def get_alternative_imgs(self):
        """Получение альтернативных картинок покемона"""
        url = f'https://pokeapi.co/api/v2/pokemon/{self.pokemon_number}'
        data = self.make_api_request(url)
        alternative_imgs = {}
        
        if data:
            sprites = data['sprites']
            
            # Основные варианты
            if sprites.get('front_default'):
                alternative_imgs['default'] = sprites['front_default']
            if sprites.get('back_default'):
                alternative_imgs['back_default'] = sprites['back_default']
            if sprites.get('front_shiny'):
                alternative_imgs['shiny'] = sprites['front_shiny']
            if sprites.get('back_shiny'):
                alternative_imgs['back_shiny'] = sprites['back_shiny']
            
            # Другие арты
            if sprites.get('other', {}).get('dream_world', {}).get('front_default'):
                alternative_imgs['dream_world'] = sprites['other']['dream_world']['front_default']
            if sprites.get('other', {}).get('home', {}).get('front_default'):
                alternative_imgs['home'] = sprites['other']['home']['front_default']
            if sprites.get('other', {}).get('official-artwork', {}).get('front_default'):
                alternative_imgs['official_artwork'] = sprites['other']['official-artwork']['front_default']
        
        # Если альтернативных картинок нет, используем основную
        if not alternative_imgs:
            alternative_imgs['default'] = self.img
            
        return alternative_imgs
        
    def get_stats(self):
        url = f'https://pokeapi.co/api/v2/pokemon/{self.pokemon_number}'
        data = self.make_api_request(url)
        if data:
            stats = {}
            for stat_info in data['stats']:
                stat_name = stat_info['stat']['name']
                base_stat = stat_info['base_stat']
                stats[stat_name] = base_stat
            return stats
        else:
            return {"hp": 50, "attack": 50, "defense": 50}

    def get_abilities(self):
        url = f'https://pokeapi.co/api/v2/pokemon/{self.pokemon_number}'
        data = self.make_api_request(url)
        if data:
            abilities = []
            for ability_info in data['abilities']:
                ability_name = ability_info['ability']['name']
                abilities.append(ability_name)
            return abilities
        else:
            return ["static"]

    def change_image(self, image_type='default'):
        """Изменение картинки покемона"""
        available_types = list(self.alternative_imgs.keys())
        
        if image_type in self.alternative_imgs:
            self.img = self.alternative_imgs[image_type]
            return True, f"Картинка изменена на: {image_type}"
        else:
            return False, f"Тип картинки '{image_type}' не найден. Доступные типы: {', '.join(available_types)}"

    def get_available_images(self):
        """Получение списка доступных картинок"""
        return list(self.alternative_imgs.keys())

    def info(self):
        if isinstance(self.stats, dict):
            stats_text = "\n".join([f"{key}: {value}" for key, value in self.stats.items()])
            image_types = ", ".join(self.get_available_images())
            return f"Имя твоего покемона: {self.name}\nСтатистика:\n{stats_text}\n\nДоступные стили: {image_types}"
        else:
            return f"Имя твоего покемона: {self.name}\nСтатистика: {self.stats}"

    def show_img(self):
        return self.img
    
    def show_stats(self):
        if isinstance(self.stats, dict):
            return "\n".join([f"{key}: {value}" for key, value in self.stats.items()])
        else:
            return self.stats

    def show_abilities(self):
        if isinstance(self.abilities, list):
            return "\n".join([f"• {ability.capitalize()}" for ability in self.abilities])
        else:
            return self.abilities