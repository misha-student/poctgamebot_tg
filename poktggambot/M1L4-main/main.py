import telebot
import random
import time
from config import token
from logic import Pokemon, Wizard, Fighter

bot = telebot.TeleBot(token)

last_heal_time = {}

@bot.message_handler(commands=['go'])
def go(message):
    username = message.from_user.username
    
    if username not in Pokemon.pokemons.keys():
        class_choice = random.randint(1, 3)
        
        # Показываем информацию о редкости
        rarity_info = ""
        if class_choice == 1:
            pokemon = Pokemon(username)
            class_name = "обычный"
        elif class_choice == 2:
            pokemon = Wizard(username)
            class_name = "волшебник"
        else:
            pokemon = Fighter(username)
            class_name = "боец"
        
        if pokemon.rarity == "legendary":
            rarity_info = "\n[ВНИМАНИЕ] Тебе выпал ЛЕГЕНДАРНЫЙ покемон! Он получает бонус +20 к силе!"
        elif pokemon.rarity == "mythical":
            rarity_info = "\n[ВНИМАНИЕ] Тебе выпал МИФИЧЕСКИЙ покемон! Он получает бонус +15 к силе!"
        elif pokemon.rarity == "rare":
            rarity_info = "\n[ВНИМАНИЕ] Тебе выпал РЕДКИЙ покемон! Он получает бонус +10 к силе!"
        
        bot.send_message(message.chat.id, f"Твой покемон ({class_name}):\n{pokemon.info()}{rarity_info}")
        bot.send_photo(message.chat.id, pokemon.show_img())
    else:
        bot.reply_to(message, "У тебя уже есть покемон. Используй /new")

@bot.message_handler(commands=['new'])
def new_pokemon(message):
    username = message.from_user.username
    class_choice = random.randint(1, 3)
    
    if class_choice == 1:
        pokemon = Pokemon(username)
        class_name = "обычный"
    elif class_choice == 2:
        pokemon = Wizard(username)
        class_name = "волшебник"
    else:
        pokemon = Fighter(username)
        class_name = "боец"
    
    rarity_info = ""
    if pokemon.rarity == "legendary":
        rarity_info = "\n[ВНИМАНИЕ] Тебе выпал ЛЕГЕНДАРНЫЙ покемон! Он получает бонус +20 к силе!"
    elif pokemon.rarity == "mythical":
        rarity_info = "\n[ВНИМАНИЕ] Тебе выпал МИФИЧЕСКИЙ покемон! Он получает бонус +15 к силе!"
    elif pokemon.rarity == "rare":
        rarity_info = "\n[ВНИМАНИЕ] Тебе выпал РЕДКИЙ покемон! Он получает бонус +10 к силе!"
    
    bot.send_message(message.chat.id, f"Новый покемон ({class_name}):\n{pokemon.info()}{rarity_info}")
    bot.send_photo(message.chat.id, pokemon.show_img())
    
    if username in last_heal_time:
        del last_heal_time[username]

@bot.message_handler(commands=['info'])
def info(message):
    username = message.from_user.username
    
    if username in Pokemon.pokemons.keys():
        pokemon = Pokemon.pokemons[username]
        bot.send_message(message.chat.id, pokemon.info())
        bot.send_photo(message.chat.id, pokemon.show_img())
    else:
        bot.reply_to(message, "У тебя нет покемона. Используй /go")

@bot.message_handler(commands=['feed'])
def feed_pokemon(message):
    """Команда для кормления покемона"""
    username = message.from_user.username
    
    if username not in Pokemon.pokemons.keys():
        bot.reply_to(message, "У тебя нет покемона. Используй /go")
        return
    
    pokemon = Pokemon.pokemons[username]
    result = pokemon.feed()
    bot.send_message(message.chat.id, result)

@bot.message_handler(commands=['heal'])
def heal_pokemon(message):
    username = message.from_user.username
    
    if username not in Pokemon.pokemons.keys():
        bot.reply_to(message, "У тебя нет покемона. Используй /go")
        return
    
    current_time = time.time()
    
    if username in last_heal_time:
        time_passed = current_time - last_heal_time[username]
        if time_passed < 10:
            remaining = 10 - int(time_passed)
            bot.reply_to(message, f"Нужно подождать {remaining} секунд до следующего лечения")
            return
    
    pokemon = Pokemon.pokemons[username]
    
    if pokemon.hp >= pokemon.max_hp:
        bot.reply_to(message, f"У твоего покемона полное здоровье ({pokemon.hp}/{pokemon.max_hp}), лечение не нужно")
        return
    
    old_hp = pokemon.hp
    missing_hp = pokemon.max_hp - pokemon.hp
    min_heal = max(10, missing_hp // 10)
    max_heal = missing_hp
    
    if min_heal > max_heal:
        min_heal = max_heal
    
    heal_amount = random.randint(min_heal, max_heal)
    pokemon.hp += heal_amount
    
    if pokemon.hp > pokemon.max_hp:
        pokemon.hp = pokemon.max_hp
    
    last_heal_time[username] = current_time
    
    bot.send_message(message.chat.id, f"Твой покемон восстановил {heal_amount} HP\nБыло: {old_hp}/{pokemon.max_hp}\nСтало: {pokemon.hp}/{pokemon.max_hp}")

@bot.message_handler(commands=['attack'])
def attack_pokemon(message):
    username = message.from_user.username
    
    if username not in Pokemon.pokemons.keys():
        bot.reply_to(message, "У тебя нет покемона. Используй /go")
        return
    
    try:
        parts = message.text.split()
        target_username = parts[1].replace('@', '')
    except:
        bot.reply_to(message, "Укажи соперника. Пример: /attack @username")
        return
    
    if target_username not in Pokemon.pokemons.keys():
        bot.reply_to(message, f"У пользователя {target_username} нет покемона")
        return
    
    if target_username == username:
        bot.reply_to(message, "Нельзя атаковать себя")
        return
    
    attacker = Pokemon.pokemons[username]
    enemy = Pokemon.pokemons[target_username]
    
    result = attacker.attack(enemy)
    bot.send_message(message.chat.id, result)
    
    if enemy.hp <= 0:
        del Pokemon.pokemons[target_username]
        bot.send_message(message.chat.id, f"Покемон {target_username} побежден")
        
        if target_username in last_heal_time:
            del last_heal_time[target_username]

@bot.message_handler(commands=['top'])
def top_players(message):
    if not Pokemon.pokemons:
        bot.send_message(message.chat.id, "Нет активных игроков")
        return
    
    players_list = "Активные игроки:\n"
    for username, pokemon in Pokemon.pokemons.items():
        rarity_mark = ""
        if pokemon.rarity == "legendary":
            rarity_mark = " [L]"
        elif pokemon.rarity == "mythical":
            rarity_mark = " [M]"
        elif pokemon.rarity == "rare":
            rarity_mark = " [R]"
        
        players_list += f"{username} - {pokemon.name}{rarity_mark} (ур.{pokemon.level} HP:{pokemon.hp}/{pokemon.max_hp} побед:{pokemon.wins})\n"
    
    bot.send_message(message.chat.id, players_list)

@bot.message_handler(commands=['new10'])
def new_ten_pokemons(message):
    bot.send_message(message.chat.id, "Генерирую 10 покемонов...")
    
    pokemon_ids = random.sample(range(1, 152), 10)
    
    pokemons = []
    for p_id in pokemon_ids:
        pokemon = Pokemon(message.from_user.username, p_id)
        pokemons.append(pokemon)
    
    info_text = "10 покемонов:\n"
    for i, p in enumerate(pokemons, 1):
        rarity_text = ""
        if p.rarity == "legendary":
            rarity_text = " [ЛЕГЕНДАРНЫЙ]"
        elif p.rarity == "mythical":
            rarity_text = " [МИФИЧЕСКИЙ]"
        elif p.rarity == "rare":
            rarity_text = " [РЕДКИЙ]"
        info_text += f"{i}. {p.name}{rarity_text}\n"
    
    bot.send_message(message.chat.id, info_text)
    
    for i, p in enumerate(pokemons, 1):
        try:
            rarity_caption = ""
            if p.rarity == "legendary":
                rarity_caption = " [ЛЕГЕНДАРНЫЙ]"
            elif p.rarity == "mythical":
                rarity_caption = " [МИФИЧЕСКИЙ]"
            elif p.rarity == "rare":
                rarity_caption = " [РЕДКИЙ]"
            bot.send_photo(message.chat.id, p.show_img(), caption=f"{i}. {p.name}{rarity_caption}")
        except:
            bot.send_message(message.chat.id, f"Не удалось загрузить {p.name}")

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = "Команды бота:\n"
    help_text += "/go - создать покемона\n"
    help_text += "/new - создать нового покемона\n"
    help_text += "/info - информация о покемоне\n"
    help_text += "/feed - покормить покемона (восстанавливает HP и дает опыт, задержка 30 сек)\n"
    help_text += "/heal - лечение покемона (задержка 10 сек)\n"
    help_text += "/attack @username - атаковать другого игрока\n"
    help_text += "/top - список игроков\n"
    help_text += "/new10 - показать 10 случайных покемонов\n"
    help_text += "\nО редкости покемонов:\n"
    help_text += "[ЛЕГЕНДАРНЫЙ] - +20 к силе, очень редкий\n"
    help_text += "[МИФИЧЕСКИЙ] - +15 к силе, редкий\n"
    help_text += "[РЕДКИЙ] - +10 к силе, необычный\n"
    help_text += "\nДостижения:\n"
    help_text += "Покорми покемона 5, 10 и 20 раз чтобы получить достижения!"
    bot.send_message(message.chat.id, help_text)

bot.infinity_polling(none_stop=True)