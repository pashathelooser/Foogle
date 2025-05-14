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
                possible_directory = directory_name + "/" + filename
                if os.path.isdir(possible_directory):
                    self.build_index(possible_directory)
                continue
            self.documents.append(filename
                                  if directory_name == self.start_directory
                                  else directory_name + "/" + filename)
            text = self.read_file(filename, directory_name)
            if not text:
                continue
            cleaned_text = self.clean_text(text)
            tokens = self.tokenize(cleaned_text)
            for term in tokens:
                self.index[term][filename] += 1

    def calculate_idf(self):
        """Вычисляет IDF для каждого слова."""
        print("Вычисляется IDF...")
        N = len(self.documents)
        for term in self.index:
            df = len(self.index[term])
            self.idf[term] = math.log(N / df)
        print("IDF вычислен")

    def get_tf(self, term, document):
        """Вычисляет TF для заданного слова в документе."""
        if term in self.index and document in self.index[term]:
            return self.index[term][document]
        return 0

    def tf_idf(self, term, document):
        """Вычисляет TF-IDF для слова в документе."""
        return self.get_tf(term, document) * self.idf.get(term, 0)

    def search(self, query):
        """Ищет документы, содержащие запрос и сортирует их по TF-IDF."""
        cleaned_query = self.clean_text(query)
        query_terms = self.tokenize(cleaned_query)

        document_score = defaultdict(float)
        for document in self.documents:
            for term in query_terms:
                document_score[document] += self.tf_idf(term, document)

        result = sorted(document_score.items(), key=lambda item: item[1], reverse=True)
        return result


print("Введите директорию для поиска:")
directory = input()
if not os.path.exists(directory):
    print(f"Директория {directory} не существует")

engine = Foogle(directory)

query = "dogs"
results = engine.search(query)

print(f"\nРезультаты поиска: '{query}'")
for document, score in results:
    print(f"{document}: {score}")
