def file_to_list(file_name, separator = '\n'):
    """
    Функция для загрузки списков из файлов.
    на входе получаем имя файла. Читаем текст, разбиваем на части по символу "\n"
    Возвращаем полученный список
    """
    with open(file_name, encoding = 'utf-8') as f:
        unsplited = f.read()
    return unsplited.split(separator)