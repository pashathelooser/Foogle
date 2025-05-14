import os
import math
import string
from collections import defaultdict


class Foogle:
    def __init__(self, directory):
        self.directory = directory
        self.index = defaultdict(lambda: defaultdict(int))  # Вложенный словарь {word: {filename: count}}
        self.documents = []
        self.idf = {}
        self.build_index()
        self.calculate_idf()

    def clean_text(self, text):
        """Удаляет знаки препинания и приводит к нижнему регистру"""
        text = text.translate(str.maketrans('', '', string.punctuation))
        return text.lower()

    def tokenize(self, text):
        """Разбивает на отдельные слова по пробелу"""
        return text.split()

    def read_file(self, filename):
        """Возвращает содержимое файла в виде строки"""
        try:
            file = open(os.path.join(self.directory, filename), 'r')
            return file.read()
        except Exception as e:
            print(f"Ошибка чтения файла {filename}: {e}")
            return ""

    def build_index(self):
        """Создает индекс слов для каждого файла в директории."""
        print("Индекс файл собирается...")
        for filename in os.listdir(self.directory):
            if not filename.endswith(".txt"):
                continue
            self.documents.append(filename)
            text = self.read_file(filename)
            if not text:
                continue
            cleaned_text = self.clean_text(text)
            tokens = self.tokenize(cleaned_text)
            for term in tokens:
                self.index[term][filename] += 1
        print("Индекс файл готов.")

    def calculate_idf(self):
        """Вычисляет IDF для каждого слова."""
        print("Calculating IDF...")
        N = len(self.documents)
        for term in self.index:
            df = len(self.index[term])
            self.idf[term] = math.log(N / df)
        print("IDF calculated.")

    def tf(self, term, document):
        """Вычисляет TF для заданного слова в документе."""
        if term in self.index and document in self.index[term]:
            # Raw term frequency
            return self.index[term][document]
        else:
            return 0

    def tf_idf(self, term, document):
        """Вычисляет TF-IDF для слова в документе."""
        return self.tf(term, document) * self.idf.get(term, 0)

    def search(self, query):
        """Ищет документы, содержащие запрос, и сортирует их по TF-IDF."""
        cleaned_query = self.clean_text(query)
        query_terms = self.tokenize(cleaned_query)

        document_scores = defaultdict(float)
        for document in self.documents:
            for term in query_terms:
                document_scores[document] += self.tf_idf(term, document)

        ranked_results = sorted(document_scores.items(), key=lambda item: item[1], reverse=True)
        return ranked_results


directory = "search_files"
if not os.path.exists(directory):
    print(f"Директория {directory} не существует")

engine = Foogle(directory)

query = "dogs"
results = engine.search(query)

print(f"\nРезультаты поиска: '{query}'")
for document, score in results:
    print(f"{document}: {score}")
