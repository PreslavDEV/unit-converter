import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Относителен път към HTML файла
html_file_path = "index.html"  # Тук трябва да поставите името на вашия HTML файл

# Настройка на опции за Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")  # Стартиране на браузъра без графичен интерфейс

# Път до драйвера
driver_path = "chromedriver.exe"  # Път към драйвера
service = Service(driver_path)

# Създаване на инстанция на драйвера
driver = webdriver.Chrome(service=service, options=chrome_options)

# Отваряме HTML файла с относителен път
driver.get(f"file:///{os.path.abspath(html_file_path)}")

# Функция за извличане на резултата и преобразуване на стойността в правилната единица
def convert_and_get_result(driver, from_unit, to_unit):
    # Изчакваме резултата да се появи
    try:
        result_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "result"))
        )
    except:
        return "Грешка: невалиден резултат"

    result = result_element.text.strip()

    # Проверка за съобщения за грешка
    if "Моля, въведете число!" in result or "невалиден" in result:
        return "Грешка: невалиден вход"  # Обработваме това съобщение като грешка

    # Проверка дали резултатът съдържа текста 'Резултат:'
    if 'Резултат:' in result:
        result = result.replace("Резултат:", "").strip()  # Премахваме 'Резултат:' и водещи/следващи интервали
    else:
        return "Грешка: невалиден резултат"  # Ако няма резултат, връщаме грешка

    # Опитваме се да извлечем число от резултата
    try:
        result_value = float(result.split()[0])  # Вземаме само числото (ако има единица след числото)
    except ValueError:
        return "Грешка: невалиден резултат"

    # Дефинираме таблица с коефициенти за конвертиране между различни мерни единици
    conversion_rates = {
        'km': {'km': 1, 'm': 1000, 'cm': 100000, 'mm': 1000000, 'mile': 0.621371, 'yard': 1093.61, 'foot': 3280.84, 'inch': 39370.1},
        'm': {'km': 0.001, 'm': 1, 'cm': 100, 'mm': 1000, 'mile': 0.000621371, 'yard': 1.09361, 'foot': 3.28084, 'inch': 39.3701},
        'cm': {'km': 0.00001, 'm': 0.01, 'cm': 1, 'mm': 10, 'mile': 0.0000062137, 'yard': 0.0109361, 'foot': 0.0328084, 'inch': 0.393701},
        'mm': {'km': 0.000001, 'm': 0.001, 'cm': 0.1, 'mm': 1, 'mile': 0.00000062137, 'yard': 0.00109361, 'foot': 0.00328084, 'inch': 0.0393701},
        'mile': {'km': 1.60934, 'm': 1609.34, 'cm': 160934, 'mm': 1609340, 'mile': 1, 'yard': 1760, 'foot': 5280, 'inch': 63360},
        'yard': {'km': 0.0009144, 'm': 0.9144, 'cm': 91.44, 'mm': 914.4, 'mile': 0.000568182, 'yard': 1, 'foot': 3, 'inch': 36},
        'foot': {'km': 0.0003048, 'm': 0.3048, 'cm': 30.48, 'mm': 304.8, 'mile': 0.000189394, 'yard': 0.333333, 'foot': 1, 'inch': 12},
        'inch': {'km': 0.0000254, 'm': 0.0254, 'cm': 2.54, 'mm': 25.4, 'mile': 0.0000157828, 'yard': 0.0277778, 'foot': 0.0833333, 'inch': 1}
    }

    # Извеждаме резултата според конверсията
    if from_unit == to_unit:
        return f"{result_value} {to_unit}"  # Ако входната и изходната единица са еднакви, не правим конверсия

    # Конвертиране на стойността според таблицата
    if from_unit in conversion_rates and to_unit in conversion_rates[from_unit]:
        conversion_factor = conversion_rates[from_unit][to_unit]
        converted_value = result_value * conversion_factor

        # Ограничаваме до 4 десетични места или премахваме десетичните знаци, ако числото е цяло
        if converted_value.is_integer():
            converted_value = int(converted_value)
        else:
            converted_value = round(converted_value, 5)

        return f"{converted_value} {to_unit}"
    else:
        return "Грешка: невалиден резултат"  # Ако няма такава конверсия, връщаме грешка


# Тестови сценарии
test_cases = [
    {"input": "1", "unit_from": "km", "unit_to": "m", "expected_result": "1000 m"},
    {"input": "1", "unit_from": "m", "unit_to": "cm", "expected_result": "100 cm"},
    {"input": "1", "unit_from": "mile", "unit_to": "km", "expected_result": "1.60934 km"},
    {"input": "-5", "unit_from": "km", "unit_to": "m", "expected_result": "-5000 m"},
    {"input": "0", "unit_from": "m", "unit_to": "km", "expected_result": "0 km"},
    {"input": "abc", "unit_from": "km", "unit_to": "m", "expected_result": "Грешка: невалиден вход"},
    {"input": "", "unit_from": "", "unit_to": "m", "expected_result": "Грешка: невалиден вход"},
    {"input": "1000000", "unit_from": "m", "unit_to": "km", "expected_result": "1000 km"},
    {"input": "1.5", "unit_from": "km", "unit_to": "m", "expected_result": "1500 m"},
    {"input": "10", "unit_from": "inch", "unit_to": "cm", "expected_result": "25.4 cm"}
]

# Изпълняваме тестовете
for test in test_cases:
    input_value = test["input"]
    unit_from = test["unit_from"]
    unit_to = test["unit_to"]
    expected_result = test["expected_result"]

    # Изчакваме полето за въвеждане да стане налично
    try:
        input_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "inputValue"))
        )
    except:
        print(f"Не може да се намери полето за въвеждане с ID 'inputValue'.")
        driver.quit()
        break

    # Намерете полето за въвеждане и въведете стойността
    input_field.clear()
    input_field.send_keys(f"{input_value}")  # Попълваме само числото

    # Избираме единицата за от
    from_unit_select = driver.find_element(By.ID, "fromUnit")
    from_unit_select.send_keys(unit_from)

    # Избираме единицата за до
    to_unit_select = driver.find_element(By.ID, "toUnit")
    to_unit_select.send_keys(unit_to)

    # Изпълняваме действието
    convert_button = driver.find_element(By.ID, "convertButton")
    convert_button.click()

    # Изчакваме резултата да се появи
    time.sleep(2)

    # Вземаме резултата от страницата
    result = convert_and_get_result(driver, unit_from, unit_to)

    # Проверяваме дали резултатът съвпада с очаквания
    if result == expected_result:
        print(f"Тест с {input_value} {unit_from} -> {unit_to} премина успешно!")
    else:
        print(f"Тест с {input_value} {unit_from} -> {unit_to} не успя. Очакван резултат: {expected_result}, получен резултат: {result}")

# Затваряне на браузъра
driver.quit()
