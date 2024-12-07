import os
import math
import argparse
from enum import Enum
import time

class Instr:
    class Type(Enum):
        move = 0,
        write = 1,

    def __init__(self, *args):
        if len(args) == 1 and type(args[0]) is str:  # args must be a data str
            attributes = args[0].split(' ')
            self.type = Instr.Type.move if attributes[0][1] == '0' else Instr.Type.write
            self.x = float(attributes[1][1:])
            self.y = float(attributes[2][1:])
        elif len(args) == 3 and type(args[0]) is Instr.Type and type(args[1]) is float and type(args[2]) is float:
            self.type, self.x, self.y = args
        else:
            raise TypeError("Instr() takes one (str) or three (Instr.Type, float, float) arguments")

    def __repr__(self):
        return "G%d X%.2f Y%.2f" % (self.type.value[0], self.x, self.y)

    def translated(self, x, y):
        return Instr(self.type, self.x + x, self.y + y + 100)

class Letter:
    def __init__(self, *args):
        if len(args) == 1 and type(args[0]) is str:
            self.instructions = []
            for line in args[0].split('\n'):
                if line != "":
                    self.instructions.append(Instr(line))

            pointsOnX = [instr.x for instr in self.instructions]
            self.width = max(pointsOnX) - min(pointsOnX)
        elif len(args) == 2 and type(args[0]) is list and type(args[1]) is float:
            self.instructions = args[0]
            self.width = args[1]
        else:
            raise TypeError("Letter() takes one (str) or two (list, float) arguments")

    def __repr__(self):
        return "\n".join([repr(instr) for instr in self.instructions]) + "\n"

    def translated(self, x, y):
        return Letter([instr.translated(x, y) for instr in self.instructions], self.width)


def readLetters(directory):
    letters = {
        " ": Letter([], 4.0),
        "\n": Letter([], math.inf)
    }

    # Читаем файлы с GCode для всех букв
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            file_path = os.path.join(root, filename)
            try:
                # Пробуем открыть файл с несколькими кодировками
                for encoding in ['utf-8', 'latin-1', 'cp1252']:  # Пробуем несколько кодировок
                    try:
                        with open(file_path, "r", encoding=encoding) as file:
                            # Читаем первую строку, чтобы получить символ
                            letterRepr = file.readline().strip()
                            if letterRepr:  # Проверка, что строка не пустая
                                letterRepr = letterRepr[1]  # Получаем символ, который представляет этот файл
                            else:
                                continue  # Если первая строка пустая, пропускаем этот файл
                            # Создаем объект Letter из содержимого файла
                            letter = Letter(file.read())
                            letters[letterRepr] = letter
                        break  # Если файл успешно прочитан с этой кодировкой, выходим из цикла
                    except UnicodeDecodeError:
                        continue  # Пробуем следующую кодировку
            except Exception as e:
                print(f"Произошла ошибка при обработке файла {file_path}: {e}")
                continue  # Пропускаем файл при других ошибках

    return letters


def textToGcode(letters, text, lineLength, lineSpacing, padding):
    # используем для быстрой конкатенации строк
    gcodeLettersArray = []
    gcodeLettersArray.append("G0 Z10\n")
    # Опускаем ось Z на 0 в начале печати
    # Опускание Z в начале
    a = False
    offsetX, offsetY = 0, 0
    for char in text:
        if(a):
            gcodeLettersArray.append("G0 Z0\n")
        # Если встречаем пробел, поднимем ось Z
        if char == " ":
            gcodeLettersArray.append("G0 Z10 ")  # Поднятие Z (вверх)

        letter = letters[char].translated(offsetX, offsetY)
        gcodeLettersArray.append(repr(letter))
        a = True
        # Если был пробел, опустим ось Z
        if char == " ":
            gcodeLettersArray.append("G0 Z0")  # Опускание Z (вниз)

        offsetX += letter.width + padding
        if offsetX >= lineLength:
            # Поднимем ось Z дважды перед переходом на новую строку
            gcodeLettersArray.append("\nG0 Z10")  # Поднимем ось Z
            # Переход на новую строку: перемещаемся в нужную точку
            offsetX = 0
            offsetY -= lineSpacing
            gcodeLettersArray.append(f"\nG0 X0 Y{offsetY}")  # Переход к началу новой строки
            gcodeLettersArray.append("\nG0 Z0")  # Опускаем ось Z сразу после перемещения

    # Поднимем ось Z после завершения печати всего текста
    gcodeLettersArray.append("G0 Z10")  # Поднятие Z после завершения печати

    return "".join(gcodeLettersArray)

def parseArgs(namespace):
    # Определяем директорию текущего скрипта
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Путь к папке ascii_gcode
    gcode_directory = os.path.join(script_dir, "ascii_gcode")
    
    # Проверка наличия папки, если она не существует, выводим сообщение об ошибке
    if not os.path.exists(gcode_directory):
        print(f"Ошибка: Папка {gcode_directory} не найдена.")
        time.sleep(10)
        exit(1)  # Завершаем выполнение программы с ошибкой
    
    # Заполняем namespace значениями по умолчанию
    input_file = os.path.join(script_dir, "input.txt")
    output_file = os.path.join(script_dir, "out.gcode")
    
    namespace.input = open(input_file, 'r', encoding='utf-8')
    namespace.output = open(output_file, 'w', encoding='utf-8')
    namespace.gcode_directory = gcode_directory  # Устанавливаем найденную папку
    namespace.line_length = 120
    namespace.line_spacing = 9
    namespace.padding = 1.5

def main():
    class Args: pass
    parseArgs(Args)

    letters = readLetters(Args.gcode_directory)
    data = Args.input.read()
    gcode = textToGcode(letters, data, Args.line_length, Args.line_spacing, Args.padding)
    Args.output.write(gcode)

    # Закрываем файлы после записи
    Args.input.close()
    Args.output.close()

if __name__ == '__main__':
    main()
