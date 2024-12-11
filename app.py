import sys
import os
import socket
import webbrowser
from flask import Flask, render_template, request, send_from_directory, redirect, url_for
from werkzeug.utils import secure_filename

# 确定资源文件路径
if getattr(sys, 'frozen', False):
    # 如果是打包后的可执行文件
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    UPLOAD_FOLDER = os.path.join(os.path.dirname(sys.executable), 'uploads')
else:
    # 如果是开发环境
    template_folder = 'templates'
    UPLOAD_FOLDER = 'uploads'

# 创建Flask应用
app = Flask(__name__, template_folder=template_folder)

# 确保上传文件夹存在
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 限制文件大小为16MB

def get_ip():
    """获取本机IP地址"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def format_size(size):
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"

@app.route('/')
def index():
    files = []
    try:
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.isfile(file_path):  # 只显示文件，不显示文件夹
                size = os.path.getsize(file_path)
                modified_time = os.path.getmtime(file_path)
                
                files.append({
                    'name': filename,
                    'size': format_size(size),
                    'modified': modified_time
                })
    except Exception as e:
        print(f"Error reading files: {e}")
    
    # 获取本机IP地址
    ip_address = get_ip()
    return render_template('index.html', files=files, ip_address=ip_address)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        filename = secure_filename(file.filename)
        try:
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        except Exception as e:
            print(f"Error saving file: {e}")
    return redirect(url_for('index'))

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/delete/<filename>')
def delete_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"Error deleting file: {e}")
    return redirect(url_for('index'))

def open_browser():
    """在默认浏览器中打开应用"""
    webbrowser.open('http://localhost:5000')

def main():
    host = '0.0.0.0'
    port = 5000
    
    # 显示启动信息
    print(f"\n{'='*50}")
    print(f"文件共享服务器已启动！")
    print(f"在本机访问：http://localhost:{port}")
    print(f"在局域网内访问：http://{get_ip()}:{port}")
    print(f"文件保存位置：{UPLOAD_FOLDER}")
    print(f"{'='*50}\n")
    
    # 自动打开浏览器
    webbrowser.open(f'http://localhost:{port}')
    
    # 启动Flask应用
    app.run(host=host, port=port, debug=False)

if __name__ == '__main__':
    main()
