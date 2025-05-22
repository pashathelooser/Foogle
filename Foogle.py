import os
import math
import string
from collections import defaultdict


class Foogle:
    def __init__(self, directory):
        self.start_directory = directory
        self.index = defaultdict(lambda: defaultdict(int))  # Вложенный словарь {word: {filename: count}}
        self.documents = []
        self.idf = {}
        self.build_index(directory)
        self.calculate_idf()

    def clean_text(self, text):
        """Удаляет знаки препинания и приводит к нижнему регистру"""
        text = text.translate(str.maketrans('', '', string.punctuation))
        return text.lower()

    def tokenize(self, text):
        """Разбивает на отдельные слова по пробелу"""
        return text.split()

    def read_file(self, filename, dir):
        """Возвращает содержимое файла в виде строки"""
        try:
            file = open(os.path.join(dir, filename), 'r')
            return file.read()
        except Exception as e:
            print(f"Ошибка чтения файла {filename}: {e}")
            return ""

    def build_index(self, directory_name):
        """Создает индекс слов для каждого файла в директории."""
        for filename in os.listdir(directory_name):
            if not filename.endswith(".txt"):
                possible_directory = os.path.join(directory_name, filename)
                if os.path.isdir(possible_directory):
                    self.build_index(possible_directory)
                continue
            self.documents.append(filename
                                  if directory_name == self.start_directory
                                  else os.path.join(directory_name, filename))
            text = self.read_file(filename, directory_name)
            if not text:
                continue
            cleaned_text = self.clean_text(text)
            tokens = self.tokenize(cleaned_text)
            for term in tokens:
                self.index[term][os.path.abspath(os.path.join(directory_name, filename))] += 1

    def calculate_idf(self):
        """Вычисляет IDF для каждого слова."""
        N = len(self.documents)
        for term in self.index:
            df = len(self.index[term])
            self.idf[term] = math.log(N / df)

    def get_tf(self, term, document):
        """Вычисляет TF для заданного слова в документе."""
        if term in self.index and document in self.index[term]:
            return self.index[term][document]
        return 0

    def tf_idf(self, term, document):
        """Вычисляет TF-IDF для слова в документе."""
        return self.get_tf(term, document) * self.idf[term]

    def search(self, query):
        """Ищет документы, содержащие запрос и сортирует их по TF-IDF."""
        query = query[6:]
        cleaned_query = self.clean_text(query)
        query_terms = self.tokenize(cleaned_query)

        document_score = defaultdict(tuple)
        for document in self.documents:
            for term in query_terms:
                tf = self.get_tf(term, document)
                if tf:
                    document_score[document] = (tf, self.tf_idf(term, document))

        result = sorted(document_score.items(), key=lambda item: item[1][1], reverse=True)
        return result


class Console:
    @staticmethod
    def help_command():
        print("To move between directories use standart cd:")
        print("    cd directory_name")
        print("To search in directory files use ")
        print("    search request_name")
        print("To exit app type 'exit'")

    def cd_command(self, cur_directory):
        """Обрабатывает введенную команду и возвращает новый путь"""
        parts = command.split()
        if len(parts) == 1:
            print("Select directory")
            return

        trg_directory = parts[1]

        if trg_directory == "..":
            new_directory = os.path.dirname(cur_directory)
        elif trg_directory == ".":
            new_directory = cur_directory
        elif trg_directory.startswith("/"):
            new_directory = trg_directory
        else:
            new_directory = os.path.join(cur_directory, trg_directory)

        if os.path.exists(new_directory) and os.path.isdir(new_directory):
            cur_directory = new_directory
            return cur_directory
        else:
            print(f"Directory '{trg_directory}' is not found")
        return cur_directory


current_directory = str(os.getcwd())
engine = Foogle(current_directory)
new_console = Console()
print("Welcome to Foogle")
new_console.help_command()
print("type 'help' for help ")
while True:
    try:
        command = input(f"[{current_directory}]> ")

        if command == "exit":
            print("Exiting application")
            break

        elif command.startswith("cd"):
            new_directory = new_console.cd_command(current_directory)
            if new_directory != current_directory:
                current_directory = new_directory
                engine = Foogle(current_directory)

        elif command.startswith("search"):
            if len(command.split()) == 1:
                print("Type what you want to search")
                continue
            finded_files = engine.search(command)
            if not len(finded_files):
                print("There is no files to your query")
            else:
                print("<-----------------Finded some files:---------------->")
            for file in finded_files:
                print(file[0] + ":  ", file[1][0])
            print()

        elif command.startswith("help"):
            Console.help_command()

        elif command:
            print(f"Undefined command: '{command}'")

    except KeyboardInterrupt:
        print("\nInterrupted by User.")
        break

    #except Exception as e:
    #    print(f"Exception occured: {e}")
