import os
import time
import subprocess
import re
import json
import datetime
import shutil
import configparser

from tqdm import tqdm
from ffmpeg_progress_yield import FfmpegProgress

from videoprops import get_audio_properties
from videoprops import get_video_properties

#Получение списка настроек
def getConfig(sConfigFile):
    if os.path.isfile(sConfigFile):
        try:
            config = configparser.ConfigParser()
            config.read(sConfigFile, encoding="utf-8")

            srcList = []
            srcList_items = config.items("srcList")
            for key, path in srcList_items:
                srcList.append(path)

            extList = json.loads(config.get("extList", "extList"))
            poolSize = config.get("poolSize", "poolSize")

            return {
                "poolSize": int(poolSize),
                "extList": extList,
                "srcList": srcList
            }

        except Exception as e:
            print("Ошибка чтения файла " + sConfigFile + ", проверьте наличие файла и правильность его заполнения.")
            print(e)
            os.system("pause")
            exit()

    else:
        shutil.copyfile(sConfigFile + ".example", sConfigFile)
        print("Похоже это первый запуск, файл " + sConfigFile + " не найден.")
        print("Файл " + sConfigFile + " создан, отредактируйте его в соответствии с вашими требованиями.")
        os.system("pause")
        exit()

# Функция анализа громкости
def get_gain_info(input_file_path):
    print("Start analyze: audio gain...")
    # Команда выполнение, вывод ffmpeg в переменную
    cmd = ['ffmpeg', '-i', str(input_file_path), '-af', 'volumedetect', '-vn', '-sn', '-dn', '-f', 'null', '-']
    output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)

    # Чистим вывод, ищем max_volume
    s_analyze_result = output.decode('utf-8')
    s_analyze_result = re.sub(r'[\t\n\r]', ' ', s_analyze_result)
    analyze_result_matches = re.search(r"max_volume:(.*)dB", s_analyze_result)

    # Если найден конвертируем в массив данных
    if analyze_result_matches:
        s_analyze_result = analyze_result_matches.group(1)
        f_analyze_result = float(s_analyze_result)

        if f_analyze_result != 0:
            f_analyze_result = f_analyze_result * -1

        return f_analyze_result

    else:
        exit('Cant find json data')


def rebuild_gain(input_file_path, gain_info, replace=True):
    # Получаем свойства аудио из файла
    inputaudioprops = get_audio_properties(input_file_path)
    inputaudioprops['bit_rate'] = inputaudioprops.get('bit_rate', '384000')  # Получаем или выдаём default занчение
    inputaudioprops['sample_rate'] = inputaudioprops.get('sample_rate', '48000')  # Получаем или выдаём default занчение
    inputaudioprops['codec_name'] = inputaudioprops.get('codec_name', 'ac3')  # Получаем или выдаём default занчение

    # Получение имён и путей
    s_time_marker = str(time.time())
    fullfilename = os.path.basename(input_file_path)
    filepathdir = os.path.dirname(input_file_path)
    fname, fextension = os.path.splitext(fullfilename)
    s_output_file = filepathdir + '\\' + '.' + s_time_marker + '.' + fullfilename

    # Непосредственная конвертация с выводом статус бара
    print('Start rebuild gain...' + ' volume=' + str(gain_info) + 'dB')
    cmd = ['ffmpeg', '-i', str(input_file_path), '-af',
           'volume=' + str(gain_info) + 'dB', '-c:v', 'copy',
           '-b:a', str(inputaudioprops['bit_rate']), '-ar', str(inputaudioprops['sample_rate']), s_output_file
            ]
    ff = FfmpegProgress(cmd)
    with tqdm(total=100, desc="[Progress]") as pbar:
        for progress in ff.run_command_with_progress():
            pbar.update(progress - pbar.n)
        pbar.close()

    if replace:
        # Подмена старого файла новым
        print("Start rename file...")
        if os.path.isfile(s_output_file):
            os.remove(input_file_path)
            os.rename(s_output_file, input_file_path)
        else:
            print("Cant find output file")


def rebuild_gain_lib(input_file_path, replace=True):
    # Получаем свойства аудио из файла
    inputaudioprops = get_audio_properties(input_file_path)
    inputaudioprops['bit_rate'] = inputaudioprops.get('bit_rate', '384000')  # Получаем или выдаём default занчение
    inputaudioprops['sample_rate'] = inputaudioprops.get('sample_rate', '48000')  # Получаем или выдаём default занчение
    inputaudioprops['codec_name'] = inputaudioprops.get('codec_name', 'acc')  # Получаем или выдаём default занчение

    # Получение имён и путей
    s_time_marker = str(time.time())
    fullfilename = os.path.basename(input_file_path)
    filepathdir = os.path.dirname(input_file_path)
    fname, fextension = os.path.splitext(fullfilename)
    s_output_file = filepathdir + '\\' + '.' + s_time_marker + '.' + fullfilename

    # Непосредственная конвертация с выводом статус бара
    print("Start rebuild gain LIB...")
    cmd = ['ffmpeg-normalize', str(input_file_path), '-o', s_output_file,
           '-t', '-16', '-tp', '-2', '-lrt', '9', '-q',
           '-c:a', str(inputaudioprops['codec_name']),
           '-b:a', str(inputaudioprops['bit_rate']),
           '-ar', str(inputaudioprops['sample_rate'])
    ]
    subprocess.call(cmd)

    if replace:
        if os.path.isfile(s_output_file):
            os.remove(input_file_path)
            os.rename(s_output_file, input_file_path)
        else:
            print("Cant find output file")


# Функция логирования
def logtofile(message):
    now = datetime.datetime.now()
    date_time_str = now.strftime("%d.%m.%Y %H:%M:%S")

    f = open('log.txt', 'a', encoding="utf-8")
    f.write(date_time_str + ': ' + str(message) + '\n')
    f.close()