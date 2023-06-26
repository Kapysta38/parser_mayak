from pathlib import Path

import pandas as pd

from client import Client


def get_last_file():
    files = sorted(Path('.').glob('*.xlsx'))
    if files:
        return files[0]
    return None


def parse_file(data):
    client = Client()
    if not client.login():
        print('Неудачная авторизация, обратитесь к разработчику')
        return
    result = pd.DataFrame([], columns=['Остаток', 'Продано'])
    for i, elem in enumerate(data.values):
        print(f'Парсинг {i + 1}/{len(data.values)}')
        url = elem[1] + str(elem[2])
        left, sells = client.parse_url(url)
        result.loc[len(result.index)] = [left, sells]

    client.quit()

    data.update(result)

    return data


def main():
    file = get_last_file()
    if not file:
        print("Excel файл в текущей директории не найден")
        return

    data = pd.read_excel(file)

    result = parse_file(data)

    result.to_excel(file, index=False)
    print('Скрипт успешно завершил работу')


if __name__ == '__main__':
    print('Старт работы скрипта')
    main()
    input('\n\nДля выхода нажмите любую кнопку:')
