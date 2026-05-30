from random import randint
import requests
import time

class Pokemon:
    pokemons = {}
    
    def __init__(self, pokemon_trainer, pokemon_id=None):
        self.pokemon_trainer = pokemon_trainer
        if pokemon_id is None:
            self.pokemon_number = randint(1, 151)
        else:
            self.pokemon_number = pokemon_id
            
        self.img = self.get_img()
        self.name = self.get_name()
        self.species_data = self.get_species_data()

        self.rarity = self.get_rarity()

        if self.rarity == "legendary":
            temp_hp = randint(200, 400)
            temp_power = randint(50, 90)
            self.rarity_bonus = " legendary power +20"
        elif self.rarity == "mythical":
            temp_hp = randint(180, 350)
            temp_power = randint(45, 85)
            self.rarity_bonus = " mythical power +15"
        elif self.rarity == "rare":
            temp_hp = randint(130, 300)
            temp_power = randint(35, 70)
            self.rarity_bonus = " rare power +10"
        else:
            temp_hp = randint(100, 250)
            temp_power = randint(30, 60)
            self.rarity_bonus = ""
        
        self.level = 1
        self.exp = 0
        self.exp_to_next = 100
        
        self.max_hp = temp_hp
        self.hp = temp_hp
        self.power = temp_power
        self.wins = 0
        self.feeds = 0  
        self.last_feed_time = 0  
        
        Pokemon.pokemons[pokemon_trainer] = self

    def get_img(self):
        url = f'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{self.pokemon_number}.png'
        return url
    
    def get_name(self):
        url = f'https://pokeapi.co/api/v2/pokemon/{self.pokemon_number}'
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                return data['forms'][0]['name']
            else:
                return "Pikachu"
        except:
            return "Pikachu"
    
    def get_species_data(self):
        """Получаем данные о виде покемона (легендарный, мифический и т.д.)"""
        url = f'https://pokeapi.co/api/v2/pokemon-species/{self.pokemon_number}'
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            return None
        except:
            return None
    
    def get_rarity(self):
        """Определяем редкость покемона"""
        if self.species_data:
            if self.species_data.get('is_legendary', False):
                return "legendary"
            elif self.species_data.get('is_mythical', False):
                return "mythical"
            elif self.species_data.get('is_baby', False):
                return "rare"

        chance = randint(1, 100)
        if chance <= 5:
            return "rare"
        return "common"

    def info(self):
        rarity_text = ""
        if self.rarity == "legendary":
            rarity_text = " [ЛЕГЕНДАРНЫЙ]"
        elif self.rarity == "mythical":
            rarity_text = " [МИФИЧЕСКИЙ]"
        elif self.rarity == "rare":
            rarity_text = " [РЕДКИЙ]"
        
        return f"Имя: {self.name.capitalize()}{rarity_text}\nУровень: {self.level}\nОпыт: {self.exp}/{self.exp_to_next}\nHP: {self.hp}/{self.max_hp}\nСила: {self.power}\nПобед: {self.wins}\nПокормлен: {self.feeds} раз"

    def show_img(self):
        return self.img
    
    def add_exp(self, amount):
        """Добавляем опыт и повышаем уровень"""
        self.exp += amount
        leveled_up = False
        
        while self.exp >= self.exp_to_next:
            self.exp -= self.exp_to_next
            self.level += 1
            self.exp_to_next = int(self.exp_to_next * 1.2)
            leveled_up = True
            

            self.max_hp = int(self.max_hp * 1.1)
            self.hp = self.max_hp
            self.power = int(self.power * 1.05)
        
        return leveled_up

    def attack(self, enemy):
        if isinstance(enemy, Wizard):
            chance = randint(1, 5)
            if chance == 1:
                return "Волшебник применил щит и уклонился от атаки!"

        power_bonus = 0
        if self.rarity == "legendary":
            power_bonus = 20
        elif self.rarity == "mythical":
            power_bonus = 15
        elif self.rarity == "rare":
            power_bonus = 10
        
        total_power = self.power + power_bonus
        
        if enemy.hp > total_power:
            enemy.hp -= total_power
            result = f"{self.pokemon_trainer} атакует {enemy.pokemon_trainer} и наносит {total_power} урона{self.rarity_bonus}"
        else:
            enemy.hp = 0
            self.wins += 1

            exp_gain = 50 + (enemy.level * 10)
            leveled = self.add_exp(exp_gain)
            
            result = f"{self.pokemon_trainer} победил {enemy.pokemon_trainer}! Получено {exp_gain} опыта"
            
            if leveled:
                result += f"\nПОЗДРАВЛЯЮ! {self.name} повысил уровень до {self.level}!"
        
        return result
    
    def feed(self):
        """Кормление покемона"""
        current_time = time.time()
        

        if current_time - self.last_feed_time < 30:
            remaining = 30 - int(current_time - self.last_feed_time)
            return f"Нужно подождать {remaining} секунд до следующего кормления"
        
        self.feeds += 1
        self.last_feed_time = current_time
        
 
        heal_amount = randint(20, 60)
        self.hp += heal_amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp
        

        exp_gain = randint(5, 15)
        leveled = self.add_exp(exp_gain)
        
        result = f"Ты покормил {self.name}! Восстановлено {heal_amount} HP. Получено {exp_gain} опыта"
        
        if leveled:
            result += f"\nПОЗДРАВЛЯЮ! {self.name} повысил уровень до {self.level}!"
        
        if self.feeds == 5:
            result += "\n[ДОСТИЖЕНИЕ] Ты покормил покемона 5 раз!"
        elif self.feeds == 10:
            result += "\n[ДОСТИЖЕНИЕ] Ты покормил покемона 10 раз! Настоящий друг!"
        elif self.feeds == 20:
            result += "\n[ДОСТИЖЕНИЕ] Ты покормил покемона 20 раз! Питомец года!"
        
        return result


class Wizard(Pokemon):
    def __init__(self, pokemon_trainer, pokemon_id=None):
        super().__init__(pokemon_trainer, pokemon_id)
        
        self.max_hp = randint(150, 350)
        self.hp = self.max_hp
        self.power = randint(20, 50)
        self.magic = randint(40, 100)
        Pokemon.pokemons[pokemon_trainer] = self
    
    def info(self):
        parent_info = super().info()
        return "У тебя покемон-волшебник\n" + parent_info + f"\nМагия: {self.magic}"
    
    def attack(self, enemy):
        super_power = randint(5, 15)
        self.power += super_power
        result = super().attack(enemy)
        self.power -= super_power
        
        if "уклонился" not in result and "победил" not in result and "щит" not in result:
            return result + f"\nВолшебник применил усиление силой:{super_power}"
        return result


class Fighter(Pokemon):
    def __init__(self, pokemon_trainer, pokemon_id=None):
        super().__init__(pokemon_trainer, pokemon_id)
        
        self.max_hp = randint(80, 200)
        self.hp = self.max_hp
        self.power = randint(50, 90)
        self.endurance = randint(30, 80)
        Pokemon.pokemons[pokemon_trainer] = self
    
    def info(self):
        parent_info = super().info()
        return "У тебя покемон-боец\n" + parent_info + f"\nВыносливость: {self.endurance}"
    
    def attack(self, enemy):
        super_power = randint(5, 15)
        self.power += super_power
        result = super().attack(enemy)
        self.power -= super_power
        
        if "уклонился" not in result and "победил" not in result and "щит" not in result:
            return result + f"\nБоец применил супер-атаку силой:{super_power}"
        return result