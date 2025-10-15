import pytest
import tempfile
import os
import csv
from rating import generate_average_rating_report

def create_temp_csv(data_rows):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['name', 'brand', 'price', 'rating'])  # заголовок
        writer.writerows(data_rows)
        return f.name

def create_temp_csv_mis(content: str):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
        f.write(content.strip())
        return f.name

def test_real_files_integration():
    data1 = [
        ['iphone 15 pro', 'apple', 999, 4.9],
        ['galaxy s23 ultra', 'samsung', 1199, 4.8],
        ['redmi note 12', 'xiaomi', 199, 4.6],
        ['iphone 14', 'apple', 799, 4.7],
        ['galaxy a54', 'samsung', 349, 4.2]
    ]
    data2 = [
        ['poco x5 pro', 'xiaomi', 299, 4.4],
        ['iphone se', 'apple', 429, 4.1],
        ['galaxy z flip 5', 'samsung', 999, 4.6],
        ['redmi 10c', 'xiaomi', 149, 4.1],
        ['iphone 13 mini', 'apple', 599, 4.5]
    ]

    f1 = create_temp_csv(data1)
    f2 = create_temp_csv(data2)
    try:
        result, index = generate_average_rating_report([f1, f2])
        expected = [
            ('apple', 4.55),
            ('samsung', 4.53),
            ('xiaomi', 4.37)
        ]
        assert result == expected
        assert index == [1, 2, 3]
    finally:
        os.unlink(f1)
        os.unlink(f2)


@pytest.mark.parametrize("input_data, brands_ratings", [
    ([
        ['phone1','brandA', 100, 4.0],['phone2', 'brandB', 200, 5.0]],
        [('brandB', 5.0), ('brandA', 4.0)]
    ),
    ([
        ['p1', 'apple', 500, 4.0], ['p2', 'apple', 600, 5.0]],
        [('apple', 4.5)]
    ),
        ([], [])
])
def test_input_data(input_data, brands_ratings):
    file_path = create_temp_csv(input_data)
    try:
        result, index = generate_average_rating_report([file_path])
        assert result == brands_ratings
        assert index == list(range(1, len(brands_ratings) + 1))
    finally:
        os.unlink(file_path)

def test_missing_rating_column():
    content = 'name,brand,price\niphone,apple,100'
    f_path = create_temp_csv_mis(content)
    try:
        with pytest.raises(KeyError, match="'rating'"):
            generate_average_rating_report([f_path])
    finally:
        os.unlink(f_path)

def test_non_numeric_rating():
    content = 'name,brand,price,rating\niphone,apple,100,number'
    f_path = create_temp_csv_mis(content)
    try:
        with pytest.raises(ValueError, match="could not convert string to float"):
            generate_average_rating_report([f_path])
    finally:
        os.unlink(f_path)

def test_single_product():
    f_path = create_temp_csv([['iphone', 'apple', 100, '2']])
    try:
        result, index = generate_average_rating_report([f_path])
        assert result == [('apple', 2)]
        assert index == [1]
    finally:
        os.unlink(f_path)

def test_many_files():
    files = []
    try:
        for i in range(10):
            f = create_temp_csv([[f'iphone{i}', 'apple', 100, 3.0 + (i % 2)],[f'redmi{i}', 'xiaomi', 200, 4.0 + (i % 2)] ])
            files.append(f)
        result, index = generate_average_rating_report(files)
        assert len(result) == 2
        assert result[0][0] == 'xiaomi'
        assert abs(result[0][1] - 4.5) < 0.01 and abs(result[1][1] - 3.5) < 0.01
    finally:
        for f in files:
            os.unlink(f)
