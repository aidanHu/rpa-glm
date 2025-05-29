import os
import glob

def delete_non_topaz_images(directory):
    # 遍历目录及其子目录
    for root, dirs, files in os.walk(directory):
        for file in files:
            # 检查文件是否为图片
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                # 检查文件名中是否包含“-topaz-upscale-4x”
                if '-upscale-4x' not in file:
                    file_path = os.path.join(root, file)
                    try:
                        os.remove(file_path)
                        print(f'已删除: {file_path}')
                    except Exception as e:
                        print(f'删除失败: {file_path}, 错误: {e}')

if __name__ == '__main__':
    # 用户输入文件夹路径
    user_directory = input('请输入要处理的文件夹路径: ')
    delete_non_topaz_images(user_directory)
    print('处理完成！') 