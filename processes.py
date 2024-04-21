from multiprocessing import Process, Lock, Manager
import time
import os

def search_keywords_process(file_list, keywords, result_queue):
    local_result = {}
    for file in file_list:
        directory_path = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(directory_path, file)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().lower()
            for keyword in keywords:
                count = content.count(keyword)
                if count > 0:
                    if keyword not in local_result:
                        local_result[keyword] = {}
                    local_result[keyword][file] = count
        except Exception as e:
            print(f"Помилка при читанні {file}: {e}")
    
    # Отправляем результат в очередь
    result_queue.put(local_result)

def main_multiprocessing(files, keywords):
    start_time = time.time()
    num_processes = 3
    processes = []
    manager = Manager()
    result_queue = manager.Queue()
    files_per_process = len(files) // num_processes  # Делим файлы на процессы

    for i in range(num_processes):
        start = i * files_per_process
        if i == num_processes - 1:
            end = len(files)  # В последнем процессе обрабатываем все оставшиеся файлы
        else:
            end = start + files_per_process
        process = Process(target=search_keywords_process, args=(files[start:end], keywords, result_queue))
        processes.append(process)
        process.start()
    
    for process in processes:
        process.join()
    
    # Агрегируем результаты
    final_result = {}
    while not result_queue.empty():
        local_result = result_queue.get()
        for key, value in local_result.items():
            if key not in final_result:
                final_result[key] = {}
            for file, count in value.items():
                if file not in final_result[key]:
                    final_result[key][file] = count
                else:
                    final_result[key][file] += count

    end_time = time.time()
    print(f"Версия с процессами выполнена за {end_time - start_time} секунды")
    return final_result

if __name__ == '__main__':
    files = ['file1.txt', 'file2.txt', 'file3.txt']
    keywords = ['lorem', 'ipsum']
    result = main_multiprocessing(files, keywords)
    print(result)
