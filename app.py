import os
import subprocess
import tempfile
import shutil
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file, after_this_request
from bitward.make_new import new_item_def
from bitward.find_passwd import find_item_by_username_flexible
from bitward.config_items import arc_path

app = Flask(__name__)

TEMP_FOLDER = 'temp'
Path(TEMP_FOLDER).mkdir(exist_ok=True)

SEVEN_ZIP_PATH = arc_path


def create_7z_archive(folder_path, archive_name, password=None):
    """Создает архив командой: 7z a archive.7z folder_path"""
    try:
        if not os.path.exists(folder_path):
            return False, f"Папка не найдена: {folder_path}"
        seven_zip_path = SEVEN_ZIP_PATH
        temp_dir = Path(tempfile.mkdtemp())
        archive_path = temp_dir / archive_name
        if seven_zip_path == "7z":
            cmd = ['7z', 'a', '-t7z', str(archive_path), folder_path, '-mx9']
        else:
            cmd = [seven_zip_path, 'a', '-t7z', str(archive_path), folder_path, '-mx9']
        if password:
            cmd.extend([f'-p{password}', '-mhe=on'])
        
        print(f"Выполняется команда: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', shell=True)
        
        if result.returncode == 0:
            print("Архив успешно создан")
            try:
                new_item_def(archive_name, passwd=password)
            except Exception as e:
                print(f"Предупреждение: Не удалось добавить в bitward: {e}")
            final_path = Path(TEMP_FOLDER) / archive_name
            shutil.move(str(archive_path), str(final_path))
            try:
                shutil.rmtree(temp_dir)
            except:
                pass
                
            return True, str(final_path)
        else:
            print(f"Ошибка 7z: {result.stderr}")
        error_msg = result.stderr or result.stdout
        try:
            shutil.rmtree(temp_dir)
        except:
            pass
        return False, f"Ошибка создания архива: {error_msg}"
        
    except Exception as e:
        try:
            if 'temp_dir' in locals():
                shutil.rmtree(temp_dir)
        except:
            pass
        return False, f"Исключение: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/test-7z', methods=['GET'])
def test_7z():
    seven_zip_path = SEVEN_ZIP_PATH
    
    if seven_zip_path:
        return jsonify({
            'success': True,
            'message': f'7-Zip найден: {seven_zip_path}',
            'path': seven_zip_path
        })
    else:
        return jsonify({
            'success': False,
            'error': '7-Zip не найден. Установите 7-Zip'
        })

@app.route('/api/create-archive', methods=['POST'])
def create_archive():
    try:
        data = request.json
        folder_path = data.get('folderPath', '')
        archive_name = data.get('archiveName', '').strip()
        password = data.get('password', '').strip() or None
        
        if not folder_path:
            return jsonify({'success': False, 'error': 'Выберите папку'}), 400
        
        if not archive_name:
            return jsonify({'success': False, 'error': 'Введите имя архива'}), 400
        
        if not archive_name.endswith('.7z'):
            archive_name += '.7z'
        if not os.path.isdir(folder_path):
            test_folder = os.path.join(TEMP_FOLDER, 'test_folder')
            os.makedirs(test_folder, exist_ok=True)

            test_file = os.path.join(test_folder, 'test.txt')
            with open(test_file, 'w') as f:
                f.write(f'Тестовый архив создан {folder_path}')
            
            folder_path = test_folder
            print(f"Используется тестовая папка: {folder_path}")
        
        success, result = create_7z_archive(folder_path, archive_name, password)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Архив успешно создан',
                'archiveName': archive_name,
                'downloadUrl': f'/api/download/{archive_name}'
            })
        else:
            return jsonify({'success': False, 'error': result}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/download/<filename>')
def download_archive(filename):
    try:
        filename = os.path.basename(filename)
        file_path = Path(TEMP_FOLDER) / filename
        
        if not file_path.exists():
            return jsonify({'success': False, 'error': 'Файл не найден'}), 404
        @after_this_request
        def remove_file(response):
            try:
                os.remove(str(file_path))
            except:
                pass
            return response
        
        return send_file(str(file_path), as_attachment=True, download_name=filename)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
@app.route('/api/password/<filename>')
def get_password(filename):
    return f"<p>{find_item_by_username_flexible(filename)}</p>"

if __name__ == '__main__':
    app.run(debug=True, port=1127)
