import os
import scriptFn
import time
from multiprocessing.pool import ThreadPool
from time import sleep

# Получение настроек
oConfig = scriptFn.getConfig('config.ini')

start_total_time = time.time()
i_total_files_success_count = 0
i_total_files_error_count = 0
i_total_files_skip_count = 0
i_total_files_action = 0
l_files_list = []

# define worker function before a Pool is instantiated
def worker(input_file_path):
    global i_total_files_action, i_total_files_error_count, i_total_files_skip_count, i_total_files_success_count

    try:
        scriptFn.logtofile('###### Start trying file ' + filename + ' ######')
        i_total_files_action += 1
        fullfilename = os.path.basename(input_file_path)
        fname, fextension = os.path.splitext(fullfilename)

        print('\n')
        print('[FILE INPUT] (' + str(i_total_files_action) + ' of ' + str(len(l_files_list)) + ')', input_file_path)

        # Проверка расширения
        if fextension.lower() in oConfig['extList']:
            start_time = time.time()

            try:
                scriptFn.rebuild_gain_lib(input_file_path)
                i_total_files_success_count += 1

            except Exception as e:
                print('Error in Try: ' + str(e))
                print(str(e))
                scriptFn.logtofile('Error in Try')
                scriptFn.logtofile(str(e))
                i_total_files_error_count += 1

            # Вывод отчёта о времени
            #print("Operation time %s minutes" % round((time.time() - start_time) / 60, 2))
            #scriptFn.logtofile("Operation time %s minutes" % round((time.time() - start_time) / 60, 2))
        else:
            print('[SKIP] ' + '(' + fextension + ') ' + input_file_path)
            scriptFn.logtofile('[SKIP] ' + '(' + fextension + ') ' + input_file_path)
            i_total_files_skip_count += 1

    except:
        print('error with item')


# Зачистка лога
if os.path.isfile('log.txt'):
    os.remove('log.txt')

# Проход по всем элементам srcList
for src in oConfig['srcList']:
    # Чтение папки
    for root, dirs, filenames in os.walk(src, topdown=False):
        # Проход по полученным файлам
        for filename in filenames:
            input_file_path = os.path.join(root, filename)
            l_files_list.append(input_file_path)

# Если файлы найдены то запускаем в мультиворкер
if len(l_files_list) > 0:

    l_files_list.sort()
    pool = ThreadPool(oConfig['poolSize'])

    for input_file_path in l_files_list:
        pool.apply_async(worker, (input_file_path,))
        sleep(1)

    pool.close()
    pool.join()


# Вывод отчёта
print("Total success files " + str(i_total_files_success_count))
scriptFn.logtofile("Total success files " + str(i_total_files_success_count))

print("Total skip files " + str(i_total_files_skip_count))
scriptFn.logtofile("Total skip files " + str(i_total_files_skip_count))

print("Total error files " + str(i_total_files_error_count))
scriptFn.logtofile("Total error files " + str(i_total_files_error_count))


print("Operation total time %s minutes" % round((time.time() - start_total_time) / 60, 2))
scriptFn.logtofile("Operation total time %s minutes" % round((time.time() - start_total_time) / 60, 2))

os.system("pause")
