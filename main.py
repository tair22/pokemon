import telebot 
from config import token
from logic import Pokemon, Wizard, Fighter
import time
from random import randint

bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start', 'help'])
def start(message):
    help_text = """
🤖 Бот Покемонов 

Доступные команды:
/go - Создать своего покемона
/info - Информация о покемоне  
/images - Доступные стили картинок
/change_image <тип> - Изменить картинку покемона
/attack - Атаковать другого игрока (ответом на сообщение)

🎮 КОМАНДЫ:
/feed - Покормить покемона
/status - Статус покемона
/heal - Восстановить здоровье

⚔️ ТИПЫ ПОКЕМОНОВ:
• 🔮 Волшебники - больше HP, магический щит
• 💪 Бойцы - больше силы, супер-атаки
• 🎯 Обычные - сбалансированные характеристики
    """
    bot.send_message(message.chat.id, help_text)
            

@bot.message_handler(commands=['go'])
def go(message):
    try:
        if message.from_user.username not in Pokemon.pokemons.keys():
            bot.send_message(message.chat.id, "🎮 Создаю твоего покемона...")
            
            
            chance = randint(1, 8)
            if chance == 1:
                pokemon = Wizard(message.from_user.username)
                type_message = "🔮 Поздравляю! Ты получил редкого покемона-волшебника!"
            elif chance == 2:
                pokemon = Fighter(message.from_user.username)
                type_message = "💪 Поздравляю! Ты получил редкого покемона-бойца!"
            else:
                pokemon = Pokemon(message.from_user.username)
                type_message = "🎯 Ты получил обычного покемона!"
            
            
            bot.send_message(message.chat.id, pokemon.info())
            bot.send_photo(message.chat.id, pokemon.show_img())
            
        else:
            bot.reply_to(message, "❌ Ты уже создал себе покемона!")
    except Exception as e:
        bot.reply_to(message, f"⚠️ Извините, произошла ошибка при создании покемона: {e}")

@bot.message_handler(commands=['feed'])
def feed_pokemon(message):
    try:
        if message.from_user.username not in Pokemon.pokemons.keys():
            bot.reply_to(message, "❌ Сначала создай покемона командой /go")
            return
            
        pokemon = Pokemon.pokemons[message.from_user.username]
        bot.send_message(message.chat.id, pokemon.feed())
        
            
    except Exception as e:
        bot.reply_to(message, f"⚠️ Ошибка при кормлении покемона: {e}")

@bot.message_handler(commands=['status'])
def show_status(message):
    try:
        if message.from_user.username not in Pokemon.pokemons.keys():
            bot.reply_to(message, "❌ Сначала создай покемона командой /go")
            return
            
        pokemon = Pokemon.pokemons[message.from_user.username]
        pokemon.update_hunger()
        
         
        pokemon_type = "🎯 Обычный"
        if isinstance(pokemon, Wizard):
            pokemon_type = "🔮 Волшебник"
        elif isinstance(pokemon, Fighter):
            pokemon_type = "💪 Боец"
        
       
        base_hp = pokemon.stats.get('hp', 'N/A') if isinstance(pokemon.stats, dict) else 'N/A'
        base_attack = pokemon.stats.get('attack', 'N/A') if isinstance(pokemon.stats, dict) else 'N/A'
        
        status_text = f"""
📊 Статус {pokemon.name.capitalize()} ({pokemon_type}):

🎯 Уровень: {pokemon.level}
📈 Опыт: {pokemon.experience}/{(pokemon.level * 100)}
❤️ Здоровье: {pokemon.hp}/{pokemon.max_hp} (база: {base_hp})
💪 Сила: {pokemon.power} (база: {base_attack})
🍎 Голод: {pokemon.hunger}/100
🏆 Побед: {pokemon.wins}
🍽️ Кормлений: {pokemon.feed_count}
⏰ Последнее кормление: {pokemon.last_feed_time}
"""
        
        if pokemon.hunger > 70:
            status_text += "\n⚠️ Покемон очень голоден! Покорми его командой /feed"
        elif pokemon.hunger > 40:
            status_text += "\n🍎 Покемон проголодался. Можешь покормить его."
        else:
            status_text += "\n😊 Покемон сыт и доволен!"
            
        
        status_text += f"\n\n💡 Советы по повышению уровня:"
        status_text += f"\n• Атакуйте других покемонов (/attack)"
        status_text += f"\n• Кормите покемона (/feed)"
        status_text += f"\n• Каждое 5-е кормление дает бонусный опыт"
        
        bot.send_message(message.chat.id, status_text)
        
    except Exception as e:
        bot.reply_to(message, f"⚠️ Ошибка при получении статуса: {e}")


@bot.message_handler(commands=['images'])
def show_images(message):
    try:
        if message.from_user.username in Pokemon.pokemons.keys():
            pokemon = Pokemon.pokemons[message.from_user.username]
            available_images = pokemon.get_available_images()
            
            images_text = "🎨 Доступные стили картинок:\n\n"
            for img_type in available_images:
                images_text += f"• {img_type}\n"
            
            images_text += "\nИспользуй /change_image <тип> чтобы изменить картинку\nНапример: /change_image shiny"
            
            bot.send_message(message.chat.id, images_text)
        else:
            bot.reply_to(message, "❌ Сначала создай покемона командой /go")
    except Exception as e:
        bot.reply_to(message, f"⚠️ Ошибка при получении списка картинок: {e}")

@bot.message_handler(commands=['change_image'])
def change_image(message):
    try:
        if message.from_user.username not in Pokemon.pokemons.keys():
            bot.reply_to(message, "❌ Сначала создай покемона командой /go")
            return
            
        pokemon = Pokemon.pokemons[message.from_user.username]
        
        command_parts = message.text.split()
        if len(command_parts) < 2:
            available_images = pokemon.get_available_images()
            bot.reply_to(message, f"⚠️ Укажи тип картинки. Доступные типы: {', '.join(available_images)}\nПример: /change_image shiny")
            return
            
        image_type = command_parts[1].lower()
        success, result_message = pokemon.change_image(image_type)
        
        if success:
            bot.send_message(message.chat.id, f"✅ {result_message}")
            bot.send_photo(message.chat.id, pokemon.show_img())
        else:
            bot.reply_to(message, f"❌ {result_message}")
            
    except Exception as e:
        bot.reply_to(message, f"⚠️ Ошибка при смене картинки: {e}")

@bot.message_handler(commands=['info'])
def full_info(message):
    try:
        if message.from_user.username in Pokemon.pokemons.keys():
            pokemon = Pokemon.pokemons[message.from_user.username]
            
            
            pokemon_type = "🎯 Обычный"
            if isinstance(pokemon, Wizard):
                pokemon_type = "🔮 Волшебник"
            elif isinstance(pokemon, Fighter):
                pokemon_type = "💪 Боец"
            
            info_text = f"📊 Информация о {pokemon.name.capitalize()} ({pokemon_type}):\n\n"
            info_text += pokemon.info()
            
            bot.send_message(message.chat.id, info_text)
            bot.send_photo(message.chat.id, pokemon.show_img())
        else:
            bot.reply_to(message, "❌ Сначала создай покемона командой /go")
    except Exception as e:
        bot.reply_to(message, f"⚠️ Ошибка при получении информации: {e}")

@bot.message_handler(commands=['abilities'])
def show_abilities(message):
    try:
        if message.from_user.username in Pokemon.pokemons.keys():
            pokemon = Pokemon.pokemons[message.from_user.username]
            abilities_text = pokemon.show_abilities()
            
            
            if isinstance(pokemon, Wizard):
                abilities_text += f"\n\n✨ Специальная способность:\n• Магический щит (шанс уклонения от атаки)\n• Усиление магией (случайное увеличение силы)"
            elif isinstance(pokemon, Fighter):
                abilities_text += f"\n\n💪 Специальная способность:\n• Супер-удар (дополнительная сила при атаке)"
            
            bot.send_message(message.chat.id, f"✨ Способности {pokemon.name.capitalize()}:\n{abilities_text}")
        else:
            bot.reply_to(message, "❌ Сначала создай покемона командой /go")
    except Exception as e:
        bot.reply_to(message, f"⚠️ Ошибка при получении способностей: {e}")

@bot.message_handler(commands=['attack'])
def attack(message):
    try:
        if message.reply_to_message:
            attacker_username = message.from_user.username
            defender_username = message.reply_to_message.from_user.username
            
            pokemon_attacker = Pokemon.pokemons.get(attacker_username)
            if not pokemon_attacker:
                bot.send_message(message.chat.id, f"@{attacker_username}, у вас нет покемона! Сначала создайте его командой /go")
                return
            
            pokemon_defender = Pokemon.pokemons.get(defender_username)
            if not pokemon_defender:
                bot.send_message(message.chat.id, f"У @{defender_username} нет покемона для атаки!")
                return
            
            if attacker_username == defender_username:
                bot.send_message(message.chat.id, "Нельзя атаковать своего же покемона!")
                return
            
            if pokemon_defender.hp <= 0:
                bot.send_message(message.chat.id, f"Покемон @{defender_username} уже повержен!")
                return
            
            if pokemon_attacker.hp <= 0:
                bot.send_message(message.chat.id, f"Ваш покемон повержен! Вы не можете атаковать.")
                return
            
            
            attack_result = pokemon_attacker.attack(pokemon_defender)
            bot.send_message(message.chat.id, attack_result)
            
    
            status_message = f"\n📊 Текущее состояние:\n"
            status_message += f"@{attacker_username}: {pokemon_attacker.hp} HP\n"
            status_message += f"@{defender_username}: {pokemon_defender.hp} HP"
            
            bot.send_message(message.chat.id, status_message)
            
            
            if pokemon_defender.hp <= 0:
                victory_message = f"🎉 @{attacker_username} одержал победу над @{defender_username}!"
                bot.send_message(message.chat.id, victory_message)
        
        else:
            bot.send_message(message.chat.id, "❌ Нужно отправить /attack в ответ на сообщение пользователя, которого хотите атаковать.")
    
    except Exception as e:
        bot.reply_to(message, f"⚠️ Ошибка при атаке: {e}")

@bot.message_handler(commands=['heal'])
def heal_pokemon(message):
    try:
        if message.from_user.username not in Pokemon.pokemons.keys():
            bot.reply_to(message, "❌ Сначала создай покемона командой /go")
            return
            
        pokemon = Pokemon.pokemons[message.from_user.username]
        
        old_hp = pokemon.hp
        pokemon.hp = min(100, pokemon.hp + 50)
        
        heal_message = f"❤️ {pokemon.name} восстановил здоровье: {old_hp} → {pokemon.hp} HP"
        bot.send_message(message.chat.id, heal_message)
        
    except Exception as e:
        bot.reply_to(message, f"⚠️ Ошибка при лечении покемона: {e}")

if __name__ == "__main__":
    try:
        bot.infinity_polling(none_stop=True, timeout=60, long_polling_timeout=30)
    except Exception as e:
        print(f"❌ Ошибка при запуске бота: {e}")