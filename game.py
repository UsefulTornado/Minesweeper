import os
import sys
import random
import pickle


class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.mine = False
        self.flagged = False
        self.opened = False
        self.border_mines = 0


class GameGrid:
    def __init__(self, height, width, mines_number):
        self.height = height
        self.width = width
        self.cells_number = height * width
        self.mines_number = mines_number
        self.opened_cells_number = 0
        self.flagged_cells_number = 0
        self.game_grid = [[Cell(i, j) for j in range(width)] for i in range(height)]
        self.locate_mines()


    def locate_mines(self):
        mines_locations = random.sample(range(0, self.cells_number), self.mines_number)

        for loc in mines_locations:
            self.set_mine(loc // self.width, loc % self.width)


    def set_mine(self, row, col):
        self.game_grid[row][col].mine = True

        for i in range(row - 1, row + 2):
            for j in range(col - 1, col + 2):
                if (i < 0 or i >= self.height or j < 0 or j >= self.width):
                    continue
                self.game_grid[i][j].border_mines += 1


    def open_cell(self, i, j):
        if (self.game_grid[i][j].mine):
            return True
        else:
            self.game_grid[i][j].opened = True
            self.opened_cells_number += 1
            if (self.game_grid[i][j].border_mines == 0):
                self.open_contiguous_cells(i, j)
            return False


    def open_contiguous_cells(self, row, col):
        for i in range(row - 1, row + 2):
            for j in range(col - 1, col + 2):
                if (i < 0 or i >= self.height or
                    j < 0 or j >= self.width or
                    self.game_grid[i][j].opened):
                    continue
                self.game_grid[i][j].opened = True
                self.opened_cells_number += 1
                if (self.game_grid[i][j].border_mines == 0):
                    self.open_contiguous_cells(i, j)


    def set_flag(self, row, col):
        cell = self.game_grid[row][col]

        if (cell.opened):
            return

        if (cell.flagged):
            cell.flagged = False
            self.flagged_cells_number -= 1
        else:
            cell.flagged = True
            self.flagged_cells_number += 1


    def create_output_image(self, game_over=False):
        game_grid = []
        first_line = []

        first_line.append("     |")
        for i in range(self.width):
            first_line.append("  {:^2d} |".format(i))

        game_grid.append(first_line)

        for row in range(2*self.height + 1):
            line = []

            if row % 2 == 0:
                line = ["-----+"] * (self.width + 1)
            else:
                line.append("  {:^2d} |".format(row // 2))

                for col in range(self.width):
                    if (self.game_grid[row // 2][col].opened):
                        line.append("  {}  |".format(self.game_grid[row // 2][col].border_mines))
                    elif (game_over and self.game_grid[row // 2][col].mine):
                        line.append("  *  |")
                    elif (self.game_grid[row // 2][col].flagged):
                        line.append("  ?  |")
                    else:
                        line.append("  .  |")

            game_grid.append(line)

        return game_grid


class Game:
    def __init__(self):
        self.game_over = False


    def print_commands(self):
        print(
            "В игре есть следующие команды:\n\n"

            "new      - начать новую игру\n"
            "help     - вывести список доступных команд\n"
            "menu     - вернуться в меню\n"
            "save     - сохранить текущую игру\n"
            "load     - загрузить сохранённую игру\n"
            "quit     - выйти из игры\n"
            "open i j - раскрыть содержимое клетки в строке i, столбце j\n"
            "flag i j - установить флажок на клетку в строке i, столбце j\n\n"

            "Команды new, load и quit доступны только в меню\n"
        )


    def start_game(self, greeting=True):
        if (greeting):
            os.system("cls||clear")
            print("Привет! Добро пожаловать в игру Сапёр!\n")

        self.print_commands()

        command = input("Что вы хотите сделать?\n")

        if (command == "new"):
            height, width = self.get_size(message="Для началы игры введите размеры поля: ")
            mines_number = self.get_mines_number(height, width, message="А также количество мин: ")
            self.game_grid = GameGrid(height, width, mines_number)
            self.play()
        elif (command == "load"):
            self.load_game()
        elif (command == "quit"):
            os.system("cls||clear")
            sys.exit()
        else:
            os.system("cls||clear")
            print("Неверная команда. Попробуйте ещё раз\n")
            self.start_game(greeting=False)


    def get_size(self, message):
        size = input(message).split()
        default_message = "Введите размеры (2 числа через пробел) ещё раз: "

        while True:
            try:
                height, width = int(size[0]), int(size[1])
            except:
                print("Некорректный ввод данных")
                size = input(default_message).split()
            else:
                break

        if (height < 4 or width < 4):
            print("На таком поле вряд ли получится поиграть :)")
            return self.get_size(message=default_message)

        return height, width


    def get_mines_number(self, height, width, message):
        mines_number = input(message)
        default_message = "Введите количество мин ещё раз: "

        while True:
            try:
                mines_number = int(mines_number)
            except:
                print("Это не число!")
                mines_number = input(default_message)
            else:
                break

        if (mines_number < 1 or mines_number >= height * width):
            print("Неподходящее количество")
            return self.get_mines_number(height, width, message=default_message)

        return mines_number


    def load_game(self):
        name = input("Введите название сохранённой игры:\n")

        try:
            with open(name + '.pkl', 'rb') as f:
                self = pickle.load(f)
                print("Игра под названием {} успешно загружена".format(name))
                _ = input("Нажмите Enter для начала игры")
                self.play()
        except:
            os.system("cls||clear")
            print(
                "Загрузить игру не удалось.\n"
                "Возможно, нет такого сохранения.\n"
            )
            self.start_game(greeting=False)


    def save_game(self):
        name = input("Введите название для сохранения:\n")

        with open(name + '.pkl', 'wb') as f:
            pickle.dump(self, f)
            print("Игра под названием {} успешно сохранена".format(name))
            _ = input("Нажмите Enter для продолжения игры")
            self.play()


    def play(self):
        while True:
            os.system("cls||clear")

            output_image = self.game_grid.create_output_image(self.game_over)
            self.draw_game_grid(output_image)

            if (self.game_over):
                print("Поражение :(\n")
                _ = input("Нажмите Enter, чтобы вернуться в меню")
                self.start_game()

            if (self.game_grid.flagged_cells_number == self.game_grid.mines_number and
                    self.game_grid.opened_cells_number + self.game_grid.mines_number ==
                    self.game_grid.cells_number):
                print("Победа!\n")
                _ = input("Нажмите Enter, чтобы вернуться в меню")
                self.start_game()

            self.process_command()


    def process_command(self):
        command = input("Введите команду:\n").split()

        if (command[0] == "open"):
            try:
                row, col = int(command[1]), int(command[2])
            except:
                print("Некорректный ввод")
                self.process_command()
            else:
                self.game_over = self.game_grid.open_cell(row, col)
        elif (command[0] == "flag"):
            try:
                row, col = int(command[1]), int(command[2])
            except:
                print("Некорректный ввод")
                self.process_command()
            else:
                self.game_grid.set_flag(row, col)
        elif (command[0] == "save"):
            self.save_game()
        elif (command[0] == "menu"):
            s = input("Если вы не сохранили текущую игру, её прогресс сбросится. Продолжить? [Y/n]\n")
            s = s.strip().lower()
            if (s == "y" or s == "yes"):
                os.system("cls||clear")
                self.start_game(greeting=False)
            else:
                self.process_command()
        elif (command[0] == "help"):
            self.print_commands()
            self.process_command()
        else:
            print("Неизвестная команда. Попробуйте ещё раз")
            self.process_command()


    def draw_game_grid(self, output_image):
        for line in output_image:
            for col in line:
                print(col, end="")
            print()
        print()


game = Game()
game.start_game()
