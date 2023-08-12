import os
import scriptFn
import time

# Получение настроек
oConfig = scriptFn.getConfig('config.ini')

start_total_time = time.time()
i_total_files_success_count = 0
i_total_files_error_count = 0
i_total_files_skip_count = 0

os.remove('log.txt')

# Проход по всем элементам srcList
for src in oConfig['srcList']:
    # Чтение папки
    for root, dirs, filenames in os.walk(src, topdown=False):
        # Проход по полученным файлам
        for filename in filenames:
            scriptFn.logtofile('###### Start trying file ' + filename + ' ######')
            # Непосредственная попытка конвертирпования

            input_file_path = os.path.join(root, filename)
            fname, fextension = os.path.splitext(filename)

            print('\n')
            print('[FILE INPUT] ', input_file_path)

            # Проверка расширения
            if fextension.lower() in oConfig['extList']:
                start_time = time.time()

                try:
                    # Получаем инфо о громкости и ребилд если ок
                    # gain_info = scriptFn.get_gain_info(input_file_path)
                    # print(gain_info)
                    # if gain_info < 0 or gain_info > 0:
                    #    scriptFn.rebuild_gain(input_file_path, gain_info)
                    #    print(scriptFn.get_gain_info(input_file_path))
                    # else:
                    #    print('[SKIP] ' + ' Gain equal 0\n' + input_file_path)
                    #    scriptFn.logtofile('[SKIP] ' + ' Gain equal 0' + input_file_path)

                    scriptFn.rebuild_gain_lib(input_file_path)
                    i_total_files_success_count += 1

                except Exception as e:
                    print('Error in Try: ' + str(e))
                    print(str(e))
                    scriptFn.logtofile('Error in Try')
                    scriptFn.logtofile(str(e))
                    i_total_files_error_count += 1

                # Вывод отчёта о времени
                print("Operation time %s minutes" % round((time.time() - start_time) / 60, 2))
                scriptFn.logtofile("Operation time %s minutes" % round((time.time() - start_time) / 60, 2))
            else:
                print('[SKIP] ' + '(' + fextension + ') ' + input_file_path)
                scriptFn.logtofile('[SKIP] ' + '(' + fextension + ') ' + input_file_path)
                i_total_files_skip_count += 1

            print('---------------\n')
            scriptFn.logtofile('---------------\n')

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
