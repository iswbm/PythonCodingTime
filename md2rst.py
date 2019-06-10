# coding:utf-8
import os
import commands
import subprocess


blog_path = 'F:\MyGit\PythonCodingTime/source'

file_list = os.listdir(blog_path)

dir_list = []
for item in file_list:
    abs_path = os.path.join(blog_path, item)
    if os.path.isdir(abs_path):
        dir_list.append(abs_path)

for folder in dir_list:
    os.chdir(folder)
    print('==== Processing folder {}'.format(folder))
    all_file = os.listdir(folder)
    all_md_file = [file for file in all_file if file.endswith('md')]
    for file in all_md_file:
        (filename, extension) = os.path.splitext(file)
        convert_cmd = 'pandoc -V mainfont="SimSun" -f markdown -t rst {md_file} -o {rst_file}'.format(
            md_file=filename+'.md', rst_file=filename+'.rst'
        )
        # status, output = commands.getstatusoutput(convert_cmd)
        retcode = subprocess.call(convert_cmd)
        # if status != 0:
        #     print(output)
        if retcode == 0:
            print(file + ' 处理完成')
        else:
            print(file + '处理失败')

