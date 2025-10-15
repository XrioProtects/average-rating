import  csv
import argparse
from collections import defaultdict
from tabulate import tabulate
import sys

def generate_average_rating_report(path):
    brand_ratings = defaultdict(list)
    for i in path:
        try:
            with open(i, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for k in reader:
                    brand_ratings[k['brand']].append(float(k['rating']))
        except FileNotFoundError:
            print(f"Файл не найден: {i}")
            sys.exit(1)
    avg_rating = {brand: round(sum(ratings) / len(ratings), 2) for brand, ratings in brand_ratings.items()}
    sorted_rating = sorted(avg_rating.items(), key=lambda x: x[1], reverse=True)
    index = list(range(1, len(sorted_rating) + 1))
    return sorted_rating, index


def main():
    reports = {
        'average-rating': generate_average_rating_report,
    }
    parser = argparse.ArgumentParser(description='Скрипт для обработки CSV-файлов и формирования отчетов.')
    parser.add_argument('--files', nargs="+", required= True, type=str,  help='Пути к файлам')
    parser.add_argument('--report', default='average-rating', type=str, help='Название отчета')
    args = parser.parse_args()
    if args.report in reports:
        columns = ['brand','rating']
        tab = reports[args.report](args.files)
        print(tabulate(tab[0], headers=columns, tablefmt="grid",showindex=tab[1]))
    else:
        print(f"Неизвестный отчет: {args.report}")

if __name__ == '__main__':
    main()
