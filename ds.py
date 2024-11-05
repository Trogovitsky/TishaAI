import speech_recognition as sr
import pyttsx3
import datetime
import random
import webbrowser
import os
import sys
import wikipedia
import requests
import json
from pathlib import Path
from playsound import playsound
from googletrans import Translator
import pygetwindow as gw
import subprocess
import threading
import time
import ctypes

class TishaAssistant:
    def __init__(self):
        self.engine = pyttsx3.init()
        # Получаем список доступных голосов
        voices = self.engine.getProperty('voices')
        # Ищем русский голос по имени
        for voice in voices:
            if "russian" in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break
        self.r = sr.Recognizer()
        self.name = "Тиша"
        # Список ключевых слов для активации
        self.activation_words = ["тиша", "тише"]
        # Путь к звуковому файлу (положите его в ту же папку, что и скрипт)
        self.activation_sound = os.path.join(os.path.dirname(__file__), "activate.mp3")
        # Настройка голоса
        self.engine.setProperty('rate', 150)    # Скорость речи
        self.engine.setProperty('volume', 0.9)  # Громкость (0.0 to 1.0)
        self.translator = Translator()
        self.history = []  # Список для хранения истории действий
        
    def speak(self, text):
        print(f"{self.name}: {text}")
        self.engine.say(text)
        self.engine.runAndWait()
    
    def listen(self):
        with sr.Microphone() as source:
            print("Слушаю...")
            audio = self.r.listen(source)
            try:
                text = self.r.recognize_google(audio, language="ru-RU")
                print(f"Вы сказали: {text}")
                return text.lower()
            except:
                return ""

    def create_folder(self, command):
        try:
            # Получаем имя папки из команды
            folder_name = command.split("папку")[-1].strip()
            if not folder_name:
                self.speak("Пожалуйста, укажите имя папки")
                return

            # Определяем путь к рабочему столу
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            
            # Если в команде указан "рабочий стол" или "desktop"
            if "рабочий стол" in command.lower() or "desktop" in command.lower():
                path = os.path.join(desktop, folder_name)
            else:
                # Иначе создаем в текущей директории
                path = os.path.join(os.getcwd(), folder_name)

            # Создаем папку
            os.makedirs(path, exist_ok=True)
            self.history.append(f"Создана папка: {folder_name}")  # Сохраняем действие
            self.speak(f"Папка {folder_name} успешно создана")
        except Exception as e:
            self.speak(f"Извините, не удалось создать папку. Ошибка: {str(e)}")

    def get_russian_time(self, hours, minutes):
        # Словари для преобразования чисел в слова
        hours_dict = {
            0: 'двенадцать', 1: 'один', 2: 'два', 3: 'три', 4: 'четыре',
            5: 'пять', 6: 'шесть', 7: 'семь', 8: 'восемь', 9: 'девять',
            10: 'десять', 11: 'одиннадцать', 12: 'двенадцать',
            13: 'один', 14: 'два', 15: 'три', 16: 'четыре',
            17: 'пять', 18: 'шесть', 19: 'семь', 20: 'восемь',
            21: 'девять', 22: 'десять', 23: 'одиннадцать'
        }
        
        minutes_dict = {
            0: '', 1: 'одна', 2: 'две', 3: 'три', 4: 'четыре',
            5: 'пять', 6: 'шесть', 7: 'семь', 8: 'восемь', 9: 'девять',
            10: 'десять', 11: 'одиннадцать', 12: 'двенадцать',
            13: 'тринадцать', 14: 'четырнадцать', 15: 'пятнадцать',
            16: 'шестнадцать', 17: 'семнадцать', 18: 'восемнадцать',
            19: 'девятнадцат', 20: 'двадцать', 30: 'тридцать',
            40: 'сорок', 50: 'пятьдесят'
        }

        # Склонение часов
        hours_form = {
            'один': 'час',
            'два': 'часа',
            'три': 'часа',
            'четыре': 'часа'
        }
        
        # Получаем строку для часов
        hour_str = hours_dict[hours]
        hour_word = hours_form.get(hour_str, 'часов')

        # Формируем строку для минут
        if minutes == 0:
            return f"{hour_str} {hour_word} ровно"
        
        if minutes < 20:
            min_str = minutes_dict[minutes]
        else:
            tens = (minutes // 10) * 10
            ones = minutes % 10
            min_str = minutes_dict[tens]
            if ones > 0:
                min_str += f" {minutes_dict[ones]}"

        # Склонение минут
        if minutes == 1:
            min_word = "минута"
        elif minutes in [2, 3, 4]:
            min_word = "минуты"
        else:
            min_word = "минут"

        return f"{hour_str} {hour_word} {min_str} {min_word}"

    def translate_text(self, text, target_lang='en', source_lang='ru'):
        """
        Переводит текст с одного языка на другой
        text: текст для перевода
        target_lang: язык, на который переводим (по умолчанию английский)
        source_lang: язык исходного текста (по умолчанию русский)
        """
        try:
            result = self.translator.translate(text, dest=target_lang, src=source_lang)
            return result.text
        except Exception as e:
            print(f"Ошибка перевода: {e}")
            return "Ошибка перевода"

    def chat(self, user_input):
        # Здесь вы можете добавить логику для обработки пользовательского ввода
        # Например, простая логика ответов
        responses = {
            "как дела": "У меня всё хорошо, спасибо!",
            "что ты умеешь": "Я могу выполнять команды, такие как создание папок, поиск информации и многое другое.",
            "расскажи анекдот": "Почему программисты не любят природу? Потому что в ней слишком много ошибок."
        }
        return responses.get(user_input, "Извините, я не понимаю.")

    def minimize_all_windows(self):
        """Скрывает все открытые окна."""
        try:
            for window in gw.getAllWindows():
                if window.isMinimized == False:  # Проверяем, не свернуто ли окно
                    window.minimize()
            self.speak("Все окна свернуты.")
        except Exception as e:
            self.speak(f"Не удалось свернуть окна. Ошибка: {str(e)}")

    def open_application(self, app_name):
        """Открывает указанное приложение."""
        try:
            if app_name.lower() == "блокнот":
                subprocess.Popen(["notepad.exe"])
                self.speak("Открываю Блокнот.")
            elif app_name.lower() == "калькулятор":
                subprocess.Popen(["calc.exe"])
                self.speak("Открываю Калькулятор.")
            elif app_name.lower() == "проводник":
                subprocess.Popen(["explorer.exe"])
                self.speak("Открываю Проводник.")
            else:
                self.speak("Извините, я не знаю, как открыть это приложение.")
        except Exception as e:
            self.speak(f"Не удалось открыть приложение. Ошибка: {str(e)}")

    def close_application(self, app_name):
        """Закрывает указанное приложение."""
        try:
            if app_name.lower() == "блокнот":
                subprocess.Popen(["taskkill", "/F", "/IM", "notepad.exe"])
                self.speak("Закрываю Блокнот.")
            elif app_name.lower() == "калькулятор":
                subprocess.Popen(["taskkill", "/F", "/IM", "calc.exe"])
                self.speak("Закрываю Калькулятор.")
            elif app_name.lower() == "проводник":
                subprocess.Popen(["taskkill", "/F", "/IM", "explorer.exe"])
                self.speak("Закрываю Проводник.")
            else:
                self.speak("Извините, я не знаю, как закрыть это приложение.")
        except Exception as e:
            self.speak(f"Не удалось закрыть приложение. Ошибка: {str(e)}")

    def set_timer(self, seconds):
        """Устанавливает таймер на указанное количество секунд."""
        def timer():
            time.sleep(seconds)
            self.speak(f"Время вышло! {seconds} секунд прошло.")

        timer_thread = threading.Thread(target=timer)
        timer_thread.start()

    def change_wallpaper(self, image_path):
        """Сменяет обои рабочего стола на указанное изображение."""
        try:
            # Убедитесь, что файл существует
            if os.path.isfile(image_path):
                ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 3)
                self.speak("Обои успешно изменены.")
            else:
                self.speak("Указанный файл не найден.")
        except Exception as e:
            self.speak(f"Не удалось изменить обои. Ошибка: {str(e)}")

    def get_random_wallpaper(self, folder_path):
        """Возвращает случайное изображение из указанной папки."""
        try:
            images = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
            if images:
                return os.path.join(folder_path, random.choice(images))
            else:
                self.speak("В папке нет изображений.")
                return None
        except Exception as e:
            self.speak(f"Не удалось получить случайное изображение. Ошибка: {str(e)}")
            return None

    def cycle_wallpapers(self, folder_path, interval):
        """Циклически меняет обои на случайные изображения из указанной папки."""
        while True:
            random_image_path = self.get_random_wallpaper(folder_path)
            if random_image_path:
                self.change_wallpaper(random_image_path)
            time.sleep(interval)  # Задержка между сменами обоев

    def undo_last_action(self):
        """Возвращает последнее действие."""
        if self.history:
            last_action = self.history.pop()
            self.speak(f"Последнее действие '{last_action}' отменено.")
        else:
            self.speak("Нет действий для отмены.")

    def restore_all_windows(self):
        """Восстанавливает все свернутые окна."""
        try:
            for window in gw.getAllWindows():
                if window.isMinimized:  # Проверяем, свернуто ли окно
                    window.restore()  # Восстанаввиваем окно
            self.speak("Все окна развернуты.")
        except Exception as e:
            self.speak(f"Не удалось развернуть окна. Ошибка: {str(e)}")

    def sleep_computer(self):
        """Переводит компьютер в спящий режим."""
        try:
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")  # Перевод в спящий режим
            self.speak("Компьютер переводится в спящий режим.")
        except Exception as e:
            self.speak(f"Не удалось перевести компьютер в спящий режим. Ошибка: {str(e)}")

    def set_sleep_timer(self, minutes):
        """Устанавливает таймер для перевода компьютера в спящий режим через указанное количество минут."""
        seconds = minutes * 60  # Преобразуем минуты в секунды
        def timer():
            time.sleep(seconds)
            self.sleep_computer()  # Вызываем метод перевода в спящий режим

        timer_thread = threading.Thread(target=timer)
        timer_thread.start()
        self.speak(f"Таймер установлен на {minutes} минут. Компьютер будет переведен в спящий режим.")

    def process_command(self, command):
        # Проверяем наличие любого из ключевых слов
        if not any(word in command for word in self.activation_words):
            return True
            
        # Воспроизводим звук при активации
        try:
            playsound(self.activation_sound)
        except Exception as e:
            print(f"Не удалось воспроизвести звук: {e}")
            
        # Определяем, какое ключевое слово было использовано
        used_keyword = next((word for word in self.activation_words if word in command), None)
        
        # Меняем имя ассистента в зависимости от использованного ключевого слова
        self.name = "Тиша" if used_keyword == "Тиша" else "Тишак"
        
        if "погода" in command:
            try:
                api_key = "9d2680cbd68b3777ee7faa9cae65e72e"  # Нужно получить API ключ с OpenWeatherMap
                city = "Москва"  # Можно доработать для определения города из команды
                url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=ru"
                response = requests.get(url)
                data = json.loads(response.text)
                temp = data['main']['temp']
                description = data['weather'][0]['description']
                self.speak(f"В городе {city} сейчас {description}, температура {temp}°C")
            except:
                self.speak("Извините, не могу получить информацию о погоде")

        elif "найди" in command or "поиск" in command:
            search_term = command.split("найди")[-1] if "найди" in command else command.split("поиск")[-1]
            try:
                wikipedia.set_lang("ru")
                result = wikipedia.summary(search_term, sentences=2)
                self.speak(f"Вот что я нашел: {result}")
            except:
                self.speak("Извините, не могу найти информацию по вашему запросу")

        elif "открой" in command:
            app_name = command.split("открой")[-1].strip()
            self.open_application(app_name)

        elif "системная информация" in command:
            self.speak(f"Операционная систма: {sys.platform}")
            self.speak(f"Текущая директория: {os.getcwd()}")
            
        elif "калькулятор" in command:
            try:
                expression = command.split("посчитай")[-1]
                result = eval(expression)
                self.speak(f"Результат: {result}")
            except:
                self.speak("Извините, не могу выполнить вычисление")

        # Оставляем существующие команды
        elif "время" in command:
            current_time = datetime.datetime.now()
            hours = current_time.hour
            minutes = current_time.minute
            time_str = self.get_russian_time(hours, minutes)
            self.speak(f"Сейчас {time_str}")
            
        elif "привет" in command:
            greetings = ["Здравтвуйте, сэр", "Рад вас видеть", "К вашим услугам"]
            self.speak(random.choice(greetings))
            
        elif "пока" in command:
            self.speak("До свидания, сэр")
            return False
            
        elif "создай папку" in command:
            self.create_folder(command)

        # Добавляем новые команды для перевода
        elif "перведи" in command:
            # Извлекаем текст для перевода
            if "на английский" in command:
                text_to_translate = command.split("на английский")[0].split("переведи")[-1].strip()
                translated = self.translate_text(text_to_translate, 'en', 'ru')
                self.speak(translated)
            
            elif "на русский" in command:
                text_to_translate = command.split("на русский")[0].split("переведи")[-1].strip()
                translated = self.translate_text(text_to_translate, 'ru', 'en')
                self.speak(translated)
            
            elif "на испанский" in command:
                text_to_translate = command.split("на испанский")[0].split("переведи")[-1].strip()
                translated = self.translate_text(text_to_translate, 'es', 'ru')
                self.speak(translated)
            
            elif "на немецкий" in command:
                text_to_translate = command.split("на немецкий")[0].split("переведи")[-1].strip()
                translated = self.translate_text(text_to_translate, 'de', 'ru')
                self.speak(translated)
            
            elif "на французский" in command:
                text_to_translate = command.split("на французский")[0].split("переведи")[-1].strip()
                translated = self.translate_text(text_to_translate, 'fr', 'ru')
                self.speak(translated)
            
            else:
                self.speak("Пожалуйста, укажите язык для перевода")
        
        elif "поговори" in command:
            self.speak("О чем вы хотите поговорить?")
            user_input = self.listen()
            if user_input:
                response = self.chat(user_input)
                self.speak(response)
        
        elif "сверни все окна" in command:
            self.minimize_all_windows()
        
        elif "закрой" in command:
            app_name = command.split("закрой")[-1].strip()
            self.close_application(app_name)
        
        elif "установи таймер на" in command:
            try:
                seconds = int(command.split("на")[-1].strip().split()[0])  # Извлекаем количество секунд
                self.set_timer(seconds)
                self.speak(f"Таймер установлен на {seconds} секунд.")
            except ValueError:
                self.speak("Пожалуйста, укажите корректное количество секунд.")
        
        elif "поменяй обои на случайные" in command:
            folder_path = "H:\TishaAIbot\Wallpeper"  # Укажите путь к папке с изображениями
            random_image_path = self.get_random_wallpaper(folder_path)
            if random_image_path:
                self.change_wallpaper(random_image_path)

        elif "начать смену обоев" in command:
            folder_path = "H:\TishaAIbot\Wallpeper"  # Укажите путь к папке с изображениями
            interval = 10  # Интервал в секундах (например, 60 секунд)
            threading.Thread(target=self.cycle_wallpapers, args=(folder_path, interval), daemon=True).start()
            self.speak("Циклическая смена обоев начата.")

        elif "вернуть обратно" in command:
            self.undo_last_action()

        elif "разверни все окна" in command:
            self.restore_all_windows()

        elif "сон" in command:
            self.sleep_computer()

        elif "перейди в спящий режим через" in command:
            try:
                minutes = int(command.split("через")[-1].strip().split()[0])  # Извлекаем количество минут
                self.set_sleep_timer(minutes)
            except ValueError:
                self.speak("Пожалуйста, укажите корректное количество минут.")

        return True

def main():
    assistant = TishaAssistant()
    assistant.speak(f"Система активирована. Скажит '{assistant.activation_words[0]}' и вашу команду")
    
    running = True
    while running:
        command = assistant.listen()
        if command:
            running = assistant.process_command(command)

if __name__ == "__main__":
    main()
