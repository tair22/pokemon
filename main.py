import telebot 
from config import token
from logic import Pokemon

bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start', 'help'])
def start(message):
    help_text = """
🤖 Бот Покемонов

Доступные команды:
/go - Создать своего покемона
/info - Информация о покемоне
/abilities - Способности покемона  
/images - Доступные стили картинок
/change_image <тип> - Изменить картинку покемона
    """
    bot.send_message(message.chat.id, help_text)

@bot.message_handler(commands=['go'])
def go(message):
    try:
        if message.from_user.username not in Pokemon.pokemons.keys():
            bot.send_message(message.chat.id, "🎮 Создаю твоего покемона...")
            pokemon = Pokemon(message.from_user.username)
            
            # Показываем информацию
            bot.send_message(message.chat.id, pokemon.info())
            bot.send_photo(message.chat.id, pokemon.show_img())
            
            # Показываем доступные команды
            help_text = """
✨ Теперь у тебя есть покемон! ✨

Доступные команды:
/abilities - Показать способности
/images - Доступные стили картинок
/change_image <тип> - Изменить картинку
            """
            bot.send_message(message.chat.id, help_text)
        else:
            bot.reply_to(message, "❌ Ты уже создал себе покемона!")
    except Exception as e:
        bot.reply_to(message, "⚠️ Извините, произошла ошибка при создании покемона. Попробуйте позже.")

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
        bot.reply_to(message, "⚠️ Ошибка при получении списка картинок")

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
        bot.reply_to(message, "⚠️ Ошибка при смене картинки")

@bot.message_handler(commands=['info'])
def full_info(message):
    try:
        if message.from_user.username in Pokemon.pokemons.keys():
            pokemon = Pokemon.pokemons[message.from_user.username]
            
            info_text = f"📊 Информация о {pokemon.name.capitalize()}:\n\n"
            
            # Статистика
            if isinstance(pokemon.stats, dict):
                stats_text = "\n".join([f"• {key}: {value}" for key, value in pokemon.stats.items()])
                info_text += f"📈 Статистика:\n{stats_text}\n\n"
            
            # Способности
            abilities_text = "\n".join([f"• {ability.capitalize()}" for ability in pokemon.abilities])
            info_text += f"✨ Способности:\n{abilities_text}\n\n"
            
            # Доступные картинки
            available_images = pokemon.get_available_images()
            images_text = ", ".join(available_images)
            info_text += f"🎨 Доступные стили: {images_text}"
            
            bot.send_message(message.chat.id, info_text)
            bot.send_photo(message.chat.id, pokemon.show_img())
        else:
            bot.reply_to(message, "❌ Сначала создай покемона командой /go")
    except Exception as e:
        bot.reply_to(message, "⚠️ Ошибка при получении информации")

@bot.message_handler(commands=['abilities'])
def show_abilities(message):
    try:
        if message.from_user.username in Pokemon.pokemons.keys():
            pokemon = Pokemon.pokemons[message.from_user.username]
            abilities_text = pokemon.show_abilities()
            bot.send_message(message.chat.id, f"✨ Способности {pokemon.name.capitalize()}:\n{abilities_text}")
        else:
            bot.reply_to(message, "❌ Сначала создай покемона командой /go")
    except Exception as e:
        bot.reply_to(message, "⚠️ Ошибка при получении способностей")

if __name__ == "__main__":
    print("🤖 Запуск бота покемонов...")
    try:
        bot.infinity_polling(none_stop=True, timeout=60, long_polling_timeout=30)
    except Exception as e:
        print(f"❌ Ошибка при запуске бота: {e}")