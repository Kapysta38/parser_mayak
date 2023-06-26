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
    data_result = []
    for i, sheet in enumerate(data):
        print(f"Парсинг листа {i + 1}/{len(data)}")
        result = pd.DataFrame([], columns=['Остаток', 'Продано'])
        for j, elem in enumerate(sheet.values):
            print(f'Парсинг {j + 1}/{len(sheet.values)}')
            url = elem[1] + str(elem[2])
            left, sells = client.parse_url(url)
            result.loc[len(result.index)] = [left, sells]
            break

        sheet.update(result)
        data_result.append(sheet)

    client.quit()

    return data_result


def get_data(file):
    data = []
    sheet_names = pd.ExcelFile(file).sheet_names
    for sheet_name in sheet_names:
        data.append(pd.read_excel(file, sheet_name=sheet_name))
    return data, sheet_names


def main():
    file = get_last_file()
    if not file:
        print("Excel файл в текущей директории не найден")
        return

    data, sheet_names = get_data(file)

    result = parse_file(data)

    with pd.ExcelWriter(file) as writer:
        for i, elem in enumerate(result):
            elem.to_excel(writer, sheet_name=sheet_names[i], index=False)

    print('Скрипт успешно завершил работу')


if __name__ == '__main__':
    print('Старт работы скрипта')
    main()
    input('\n\nДля выхода нажмите любую кнопку:')
