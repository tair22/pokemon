from random import randint
import random
import requests
import time
import json
import os
import datetime
from datetime import timedelta

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
        
        
        self.hp = self.get_hp_from_stats()
        self.max_hp = self.hp  
        self.power = self.get_power_from_stats()
        self.level = 1
        self.experience = 0
        self.hunger = 0
        self.last_feed_time = datetime.datetime.now()  
        self.is_shiny = self.check_shiny()
        self.is_legendary = self.check_legendary()
        self.wins = 0
        self.feed_count = 0  
        
        Pokemon.pokemons[pokemon_trainer] = self
    
    def get_hp_from_stats(self):
        if isinstance(self.stats, dict) and 'hp' in self.stats:
            api_hp = self.stats['hp']
            normalized_hp = max(50, min(150, api_hp))
            return normalized_hp
        else:
            return random.randint(70, 100)  
    
    def get_power_from_stats(self):
        if isinstance(self.stats, dict):
           
            attack = self.stats.get('attack', 50)
            special_attack = self.stats.get('special-attack', 50)
            
            
            total_attack = max(attack, special_attack)
            normalized_power = max(10, min(30, total_attack // 5))
            return normalized_power
        else:
            return random.randint(10, 20) 

    def info(self):
        self.update_hunger()
        
        pokemon_type = "🎯 Обычный"
        if isinstance(self, Wizard):
            pokemon_type = "🔮 Волшебник"
        elif isinstance(self, Fighter):
            pokemon_type = "💪 Боец"
        
        if isinstance(self.stats, dict):
            stats_text = "\n".join([f"{key}: {value}" for key, value in self.stats.items()])
            
            status_text = f"""
📊 Информация о {self.name.capitalize()} ({pokemon_type}):

🎯 Уровень: {self.level}
📈 Опыт: {self.experience}/{(self.level * 100)}
❤️ Здоровье: {self.hp}/{self.max_hp} (база: {self.stats.get('hp', 'N/A')})
💪 Сила: {self.power} (база: {self.stats.get('attack', 'N/A')})
🍎 Голод: {self.hunger}/100
🏆 Побед: {self.wins}
🍽️ Кормлений: {self.feed_count}
{'✨ ШИНИ ПОКЕМОН!' if self.is_shiny else ''}
{'👑 ЛЕГЕНДАРНЫЙ ПОКЕМОН!' if self.is_legendary else ''}
"""
            
            image_types = ", ".join(self.get_available_images())
            return f"{status_text}\n🎨 Доступные стили картинок: {image_types}"
        else:
            return f"Имя твоего покемона: {self.name} ({pokemon_type})"

    def attack(self, enemy):
        heal_chance = random.randint(1, 5)
        heal_message = ""
        
        if heal_chance == 1 and self.hp < self.max_hp:
            heal_amount = random.randint(60, 100)
            old_hp = self.hp
            self.hp = min(self.max_hp, self.hp + heal_amount)
            heal_message = f"\n💚 {self.name} восстановил {heal_amount} HP во время атаки! ({old_hp} → {self.hp})"
        
        if isinstance(enemy, Wizard):
            chance = random.randint(1, 5)
            if chance == 1:
                return f"🌀 Покемон-волшебник {enemy.name} применил магический щит и уклонился от атаки!{heal_message}"
        
      
        damage = self.power
        
        if enemy.hp > damage:
            enemy.hp -= damage
            result = f"⚔️ Сражение @{self.pokemon_trainer} с @{enemy.pokemon_trainer}\n{enemy.name} получает урон: {damage}{heal_message}"
            
            
            exp_gained = damage // 2
            level_up_message = self.add_experience(exp_gained)
            if level_up_message:
                result += f"\n{level_up_message}"
                
        else:
            enemy.hp = 0
            self.wins += 1
            result = f"🎉 Победа @{self.pokemon_trainer} над @{enemy.pokemon_trainer}! {enemy.name} повержен!{heal_message}"
            
          
            exp_gained = 50
            level_up_message = self.add_experience(exp_gained)
            if level_up_message:
                result += f"\n{level_up_message}"
        
        return result

    def level_up(self):
        self.level += 1
        self.experience = 0
        self.max_hp += 15 
        self.hp = self.max_hp  
        self.power += 5
        
        return f"🎉 {self.name} повысил уровень! Теперь уровень {self.level} (❤️ +15, 💪 +5)"

    def add_experience(self, exp):
        self.experience += exp
        exp_for_next_level = self.level * 100
        
        if self.experience >= exp_for_next_level:
            return self.level_up()
        return None

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
        url = f'https://pokeapi.co/api/v2/pokemon/{self.pokemon_number}'
        data = self.make_api_request(url)
        if data:
            return data['sprites']['other']['official-artwork']['front_default']
        else:
            return "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png"
    
    def get_alternative_imgs(self):
        url = f'https://pokeapi.co/api/v2/pokemon/{self.pokemon_number}'
        data = self.make_api_request(url)
        alternative_imgs = {}
        
        if data:
            sprites = data['sprites']
            
            if sprites.get('front_default'):
                alternative_imgs['default'] = sprites['front_default']
            if sprites.get('back_default'):
                alternative_imgs['back_default'] = sprites['back_default']
            if sprites.get('front_shiny'):
                alternative_imgs['shiny'] = sprites['front_shiny']
            if sprites.get('back_shiny'):
                alternative_imgs['back_shiny'] = sprites['back_shiny']
            
            if sprites.get('other', {}).get('dream_world', {}).get('front_default'):
                alternative_imgs['dream_world'] = sprites['other']['dream_world']['front_default']
            if sprites.get('other', {}).get('home', {}).get('front_default'):
                alternative_imgs['home'] = sprites['other']['home']['front_default']
            if sprites.get('other', {}).get('official-artwork', {}).get('front_default'):
                alternative_imgs['official_artwork'] = sprites['other']['official-artwork']['front_default']
        
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
            return {"hp": 50, "attack": 50, "defense": 50, "special-attack": 50}

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

    def check_shiny(self):
        return randint(1, 4096) == 1

    def check_legendary(self):
        legendary_ids = [
            144, 145, 146, 150, 151,  
            243, 244, 245, 249, 250, 251, 
            377, 378, 379, 380, 381, 382, 383, 384, 385, 386,  
        ]
        return self.pokemon_number in legendary_ids

    
    def feed(self, feed_interval=20, hp_increase=10):
        current_time = datetime.datetime.now()
        delta_time = timedelta(seconds=feed_interval)
        
        if (current_time - self.last_feed_time) > delta_time:
            old_hp = self.hp
            self.hp = min(self.max_hp, self.hp + hp_increase)
            self.last_feed_time = current_time
            self.feed_count += 1
            self.hunger = max(0, self.hunger - 30) 
            
            result_message = f"🍎 {self.name} покормлен! Здоровье: {old_hp} → {self.hp} HP"
            
            exp_gained = 10
            level_up_message = self.add_experience(exp_gained)
            if level_up_message:
                result_message += f"\n{level_up_message}"
            
            
            if self.feed_count % 5 == 0: 
                bonus_level_up = self.add_experience(25)
                if bonus_level_up:
                    result_message += f"\n{bonus_level_up}"

            return result_message
        else:
            next_feed_time = self.last_feed_time + delta_time
            return f"⏰ Следующее кормление доступно в: {next_feed_time}"

    def update_hunger(self):
        current_time = datetime.datetime.now()
        if hasattr(self, 'last_feed_time'):
            hours_passed = (current_time - self.last_feed_time).total_seconds() / 3600
            self.hunger = min(100, int(hours_passed * 20))
        else:
            self.hunger = 0

    def change_image(self, image_type='default'):
        available_types = list(self.alternative_imgs.keys())
        
        if image_type in self.alternative_imgs:
            self.img = self.alternative_imgs[image_type]
            return True, f"Картинка изменена на: {image_type}"
        else:
            return False, f"Тип картинки '{image_type}' не найден. Доступные типы: {', '.join(available_types)}"

    def get_available_images(self):
        return list(self.alternative_imgs.keys())

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


class Wizard(Pokemon):
    def __init__(self, pokemon_trainer):
        super().__init__(pokemon_trainer)

        base_hp = self.get_hp_from_stats()
        base_power = self.get_power_from_stats()
        
        self.hp = int(base_hp * 1.2) 
        self.max_hp = self.hp
        self.power = int(base_power * 0.9)  
        self.magic_power = int(base_power * 1.3) 
    
    def info(self):
        base_info = super().info()
        return f"🔮 У тебя покемон-волшебник!\n{base_info}\n✨ Магическая сила: {self.magic_power}\nСпособность: Магический щит (шанс уклонения)"
    
    def attack(self, enemy):
        heal_chance = random.randint(1, 5)
        heal_message = ""
        
        if heal_chance == 1 and self.hp < self.max_hp:
            heal_amount = random.randint(10, 20)
            old_hp = self.hp
            self.hp = min(self.max_hp, self.hp + heal_amount)
            heal_message = f"\n✨ Магическое восстановление! {self.name} восстановил {heal_amount} HP! ({old_hp} → {self.hp})"
        
       
        damage = self.magic_power
        
        
        if isinstance(enemy, Wizard):
            chance = random.randint(1, 3)
            if chance == 1:
                return f"🌀 Покемон-волшебник {enemy.name} применил магический щит и уклонился от атаки!{heal_message}"
        
        if enemy.hp > damage:
            enemy.hp -= damage
            result = f"🔮 Магическая атака @{self.pokemon_trainer} с @{enemy.pokemon_trainer}\n{enemy.name} получает магический урон: {damage}{heal_message}"
            
           
            exp_gained = damage // 2
            level_up_message = self.add_experience(exp_gained)
            if level_up_message:
                result += f"\n{level_up_message}"
                
        else:
            enemy.hp = 0
            self.wins += 1
            result = f"🎉 Победа @{self.pokemon_trainer} над @{enemy.pokemon_trainer}! {enemy.name} повержен магией!{heal_message}"
            
           
            exp_gained = 50
            level_up_message = self.add_experience(exp_gained)
            if level_up_message:
                result += f"\n{level_up_message}"
        
        return result
    
    def feed(self, feed_interval=20, hp_increase=10):
        """Кормление покемона-волшебника с бонусом"""
        result = super().feed(feed_interval, hp_increase)
        if "покормлен" in result:
            bonus_hp = 5
            old_hp = self.hp
            self.hp = min(self.max_hp, self.hp + bonus_hp)
            return result + f"\n✨ Магическая энергия! Дополнительно +{bonus_hp} к здоровью! ({old_hp} → {self.hp})"
        return result


class Fighter(Pokemon):
    def __init__(self, pokemon_trainer):
        super().__init__(pokemon_trainer)
        
        base_hp = self.get_hp_from_stats()
        base_power = self.get_power_from_stats()
        
        self.hp = int(base_hp * 0.9)  
        self.max_hp = self.hp
        self.power = int(base_power * 1.3) 
        self.fight_skill = int(base_power * 1.2) 
    
    def info(self):
        base_info = super().info()
        return f"💪 У тебя покемон-боец!\n{base_info}\n🔥 Боевое мастерство: {self.fight_skill}\nСпособность: Супер-удар (увеличение силы)"
    
    def attack(self, enemy):
        damage = self.power
        critical_chance = random.randint(1, 5)
        heal_chance = random.randint(1, 7)
        
        heal_message = ""
        if heal_chance == 1 and self.hp < self.max_hp:
            heal_amount = random.randint(5, 10)
            old_hp = self.hp
            self.hp = min(self.max_hp, self.hp + heal_amount)
            heal_message = f"\n💪 Боевой дух! {self.name} восстановил {heal_amount} HP! ({old_hp} → {self.hp})"
        
        if critical_chance == 1:
            damage = int(damage * 100)
            critical_text = " 💥 КРИТИЧЕСКИЙ УДАР!"
        else:
            critical_text = ""
        

        if isinstance(enemy, Wizard):
            chance = random.randint(1, 5)
            if chance == 1:
                return f"🌀 Покемон-волшебник {enemy.name} применил магический щит и уклонился от атаки!{heal_message}"
        
        if enemy.hp > damage:
            enemy.hp -= damage
            result = f"💪 Боевая атака @{self.pokemon_trainer} с @{enemy.pokemon_trainer}\n{enemy.name} получает урон: {damage}{critical_text}{heal_message}"
            
           
            exp_gained = damage // 2
            level_up_message = self.add_experience(exp_gained)
            if level_up_message:
                result += f"\n{level_up_message}"
                
        else:
            enemy.hp = 0
            self.wins += 1
            result = f"🎉 Победа @{self.pokemon_trainer} над @{enemy.pokemon_trainer}! {enemy.name} повержен в бою!{critical_text}{heal_message}"
            
          
            exp_gained = 50
            level_up_message = self.add_experience(exp_gained)
            if level_up_message:
                result += f"\n{level_up_message}"
        
        return result
    
    def feed(self, feed_interval=20, hp_increase=10):
        result = super().feed(feed_interval, hp_increase)
        if "покормлен" in result:
            bonus_power = 2
            old_power = self.power
            self.power += bonus_power
            return result + f"\n💪 Боевой дух! Дополнительно +{bonus_power} к силе! ({old_power} → {self.power})"
        return result