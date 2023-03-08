from itertools import cycle
import random
from collections import Counter
from tkinter import *
from tkinter import messagebox
import tkinter.filedialog as fd


# Предупреждение о том, что файл не выбран
def exception(param):
    messagebox.showwarning("Предупреждение", param)


# Выбираем файл
def choose_file():
    global filename
    try:
        filetype = (("Текстовый файл", '*.txt'), ("All files", '*.*'))
        filename = fd.askopenfilename(title="Открыть файл", initialdir="/", filetypes=filetype)
        if filename == "":
            raise Exception("Файл не выбран")
    except Exception as e:
        exception(e)
        return False
    return True


# Подсчитываем общее количество букв
def count_letters():
    count = 0
    for i in range(len(letters)):
        count += counter[letters[i]]
    return count


# Находим частоту каждой буквы
def frequency(count):
    arr_my_frequency = []
    for i in range(len(letters)):
        frequency = counter[letters[i]] / count * 100
        arr_my_frequency.append(frequency)
    return arr_my_frequency


# Функция шифрования
def vijn():
    global counter
    global freq
    with open(filename, encoding='utf-8', newline='') as file:
        arr = []
        text_for_encrypt = file.read().lower()
        # генерируем рандомный ключ рандомного размера
        key = list(random.choice(letters) for i in range(random.randint(2, 10)))
        print(key)
        # избавимся от лишних символов для простоты работы со текстом
        for i in text_for_encrypt:
            if letters.find(i) != -1:
                only_letters.append(i)
        counter = Counter(only_letters)
        # на месте этой частоты может быть обычная частота букв в русском языке, взятая из Википедии
        freq = dict(sorted(dict(zip(letters, frequency(count_letters()))).items(), key=lambda item: item[1])).keys()
        # шифруем текст шифром Виженера
        for i, j in zip(only_letters, cycle(key)):
            step = letters.find(j)
            arr.append(letters[(letters.find(i) + step) % len(letters)])
        arr_text = ''.join(arr)
        return arr_text


# Поиск индексов совпадений (для нахождения длины ключа)
def match_index(X, L):
    arr = []
    for i in range(len(X)):
        if i % L == 0:
            arr.append(X[i])
    someCounter = Counter(arr)
    I = 0
    for i in range(len(letters)):
        count = someCounter[letters[i]]
        I += (count * (count - 1) / (len(arr) * (len(arr) - 1)))
    return I


# Поиск взаимных индекс совпадений (для нахождения сдвигов относительно первой строки)
def mutual_match_index(X, Y, s):
    counter1 = Counter(list(X))
    counter2 = Counter(list(letters[(letters.find(i) + s) % len(letters)] for i in Y))
    I = 0
    for i in range(len(letters)):
        count = counter1[letters[i]]
        count2 = counter2[letters[i]]
        I += (count * count2 / (len(X) * len(Y)))
    return I, s


# Находим длину ключа и запускаем частотный анализ
def decrypt_text(text_for_decrypt):
    longs = [(i, match_index(text_for_decrypt, i)) for i in range(1, 10)]
    long = max(longs, key=lambda x: x[1])
    i = 0
    while long[1] >= 1.06 * longs[i][1]:
        i += 1
    long = longs[i]
    print(f"Key long: {long}\n")
    # формируем пары строк для нахождения взаимного индекса
    pairs = []
    for i in range(1, long[0]):
        pairs.append((text_for_decrypt[0::long[0]], text_for_decrypt[i::long[0]]))
    # считаем сдвиги относительно первой строки
    shifts = []
    for pair in pairs:
        indexes = [mutual_match_index(pair[0], pair[1], s) for s in range(len(letters))]
        shifts.append(33 - max(indexes, key=lambda i: i[0])[1])
    print(f"Shifts:{shifts}\n")
    return freq_analysis(list(text_for_decrypt), shifts, long[0])


# Частотный анализ по всем столбцам
def freq_analysis(text_for_decrypt, shifts, long):
    global counter
    arr_encrypt_text = []
    pos = 0
    # убираем сдвиги
    for shift in shifts:
        pos += 1
        text_for_decrypt = shifting(text_for_decrypt, shift, pos, long)
    # частотный анализ
    counter = Counter(text_for_decrypt)
    another_freq = dict(sorted(dict(zip(letters, frequency(count_letters()))).items(), key=lambda item: item[1])).keys()
    dictionary = dict(zip(another_freq, freq))
    for i in text_for_decrypt:
        arr_encrypt_text.append(dictionary.get(i))
    text_for_decrypt = ''.join(arr_encrypt_text)
    letter = letters[33-letters.find(dictionary.get('а'))]
    key = [letters[(letters.find(letter) + shift) % len(letters)] for shift in shifts]
    key.insert(0, letter)
    return text_for_decrypt, key


def shifting(text, shift, pos, long):
    for i in range(pos, len(text), long):
        text[i] = letters[(letters.find(text[i]) - shift) % len(letters)]
    return text


# Функция запуска взлома
def hack():
    if choose_file():
        text = vijn()
        result, key = decrypt_text(text)
        encrypted.insert(1.0, text)
        decrypted.insert(1.0, result)
        messagebox.showinfo("Ключ", f"Ключ: {key}")


# расположение файла
filename = ""
# алфавит
letters = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
only_letters = []

# окно
window = Tk()
window.title('Взлом Виженера')
window.geometry('600x600')
window.resizable(0, 0)
window['bg'] = "#efefef"
font = ("Century Gothic", 16)

# поле вывода зашифрованного текста
encryptLabel = Label(window, text='Зашифрованный текст:', font=font)
encryptLabel.place(x=20, y=15)
encrypted = Text(width=47, height=10, font=font)
encrypted.place(x=20, y=45)
scroll = Scrollbar(command=encrypted.yview)
scroll.place(x=0, y=15)
encrypted.config(yscrollcommand=scroll.set)

# поле вывода
decryptLabel = Label(window, text='Расшифрованный текст:', font=font)
decryptLabel.place(x=20, y=315)
decrypted = Text(width=47, height=8, font=font)
decrypted.place(x=20, y=345)
scroll2 = Scrollbar(command=decrypted.yview)
scroll2.place(x=0, y=320)
decrypted.config(yscrollcommand=scroll2.set)

button = Button(window, text="Взлом", font=font, command=hack)
button.place(x=30, y=550)

window.mainloop()


