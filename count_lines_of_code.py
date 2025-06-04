import os

def count_lines_in_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return sum(1 for line in f if line.strip())
    except Exception as e:
        print(f"Ошибка при чтении {filepath}: {e}")
        return 0

def count_lines_in_directory(root_dir):
    total_lines = 0
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Удаляем из dirnames все папки, которые начинаются с точек — os.walk не зайдет в них
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]
        for filename in filenames:
            if filename.endswith('.py'):
                filepath = os.path.join(dirpath, filename)
                line_count = count_lines_in_file(filepath)
                print(f"{filepath}: {line_count} строк")
                total_lines += line_count
    return total_lines

if __name__ == "__main__":
    current_directory = os.path.dirname(os.path.abspath(__file__))
    total = count_lines_in_directory(current_directory)
    print(f"\nОбщее количество строк кода в .py файлах: {total}")
