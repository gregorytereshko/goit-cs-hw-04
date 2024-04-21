import threading
import os
import time

def search_keywords(file_list, keywords, result_dict, lock):
    # Створюємо локальний результат для зберігання вхідних даних
    local_result = {}
    for file in file_list:
        directory_path = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(directory_path, file)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().lower()
            # Перевіряємо кожне ключове слово в контенті
            for keyword in keywords:
                count = content.count(keyword)
                if count > 0:
                    if keyword not in local_result:
                        local_result[keyword] = {}
                    local_result[keyword][file] = count
        except Exception as e:
            print(f"Помилка при читанні {file}: {e}")
    
    # Використовуємо блокування для синхронізації запису результатів
    with lock:
        for key, files in local_result.items():
            if key not in result_dict:
                result_dict[key] = {}
            result_dict[key].update(files)

def main_threading(files, keywords):
    start_time = time.time()
    num_threads = 3
    threads = []
    result_dict = {}
    lock = threading.Lock()
    files_per_thread = len(files) // num_threads
    
    for i in range(num_threads):
        start = i * files_per_thread
        if i == num_threads - 1:
            end = len(files)  # Забезпечуємо, що останній потік обробляє всі залишені файли
        else:
            end = start + files_per_thread
        thread = threading.Thread(target=search_keywords, args=(files[start:end], keywords, result_dict, lock))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    end_time = time.time()
    print(f"Версія з потоками виконалася за {end_time - start_time} секунд")
    return result_dict

if __name__ == '__main__':
    files = ['file1.txt', 'file2.txt', 'file3.txt']
    keywords = ['lorem', 'ipsum']
    result = main_threading(files, keywords)
    print(result)
