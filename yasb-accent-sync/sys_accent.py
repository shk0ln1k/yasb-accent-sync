import os
import re
import time
import subprocess
import winreg
import json
import yaml
import shutil

CSS_PATH = os.path.expanduser(r'~\.config\yasb\styles.css')
CSS_BACKUP = CSS_PATH + ".bak"
YASB_CONFIG_PATH = os.path.expanduser(r'~\.config\yasb\config.yaml')

def get_accent_color():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\DWM')
        accent, _ = winreg.QueryValueEx(key, 'AccentColor')
        b = (accent >> 16) & 0xFF
        g = (accent >> 8) & 0xFF
        r = accent & 0xFF
        return f"#{r:02x}{g:02x}{b:02x}"
    except:
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\DWM')
            color, _ = winreg.QueryValueEx(key, 'ColorizationColor')
            r = (color >> 16) & 0xFF
            g = (color >> 8) & 0xFF
            b = color & 0xFF
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return "#0078D4"

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(r, g, b):
    return f"#{r:02x}{g:02x}{b:02x}"

def mix_colors(hex_color, mix_color, percent):
    r1, g1, b1 = hex_to_rgb(hex_color)
    r2, g2, b2 = hex_to_rgb(mix_color)
    r = int(r1 + (r2 - r1) * percent)
    g = int(g1 + (g2 - g1) * percent)
    b = int(b1 + (b2 - b1) * percent)
    return rgb_to_hex(r, g, b)

def rgba_to_css(r, g, b, alpha):
    return f"rgba({r}, {g}, {b}, {alpha})"

# ------------------------------------------------------------
# Определение пути к komorebi.json (универсальное)
# ------------------------------------------------------------
def get_komorebi_config_path():
    # 1. Проверяем переменную окружения
    env_path = os.environ.get('KOMOREBI_CONFIG_PATH')
    if env_path and os.path.exists(env_path):
        return env_path

    # 2. Используем komorebic configuration
    try:
        result = subprocess.run(["komorebic", "configuration"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            path = result.stdout.strip()
            if os.path.exists(path):
                return path
    except:
        pass

    # 3. Стандартный путь (как у большинства пользователей)
    fallback = os.path.expanduser(r'~\.config\komorebi\komorebi.json')
    if os.path.exists(fallback):
        return fallback

    # 4. Путь в домашней папке (для совместимости)
    fallback2 = os.path.expanduser(r'~\komorebi.json')
    if os.path.exists(fallback2):
        return fallback2

    return None

# ------------------------------------------------------------
# Обновление границ Komorebi
# ------------------------------------------------------------
def update_komorebi_border(accent_light):
    komorebi_path = get_komorebi_config_path()
    if not komorebi_path:
        print("⚠️ Не удалось найти komorebi.json, пропускаем обновление границ.")
        return

    try:
        with open(komorebi_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        data["border"] = True
        data["border_width"] = 4
        data["border_offset"] = -1
        data["border_style"] = "Rounded"
        data["border_colours"] = {
            "single": accent_light,
            "stack": accent_light,
            "monocle": accent_light,
            "unfocused": accent_light
        }

        with open(komorebi_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        print(f"🖌️ Границы Komorebi обновлены на {accent_light}")
        subprocess.run(["komorebic", "reload-configuration"], capture_output=True, timeout=5)
        print("🔄 Konfiguration Komorebi neu geladen")
    except Exception as e:
        print(f"⚠️ Ошибка обновления границ Komorebi: {e}")
        try:
            print("🔄 Пытаемся перезапустить Komorebi через stop/start...")
            subprocess.run(["komorebic", "stop"], capture_output=True, timeout=5)
            subprocess.run(["komorebic", "start", "--whkd"], capture_output=True, timeout=5)
            print("✅ Komorebi перезапущен")
        except Exception as e2:
            print(f"⚠️ Не удалось перезапустить Komorebi: {e2}")

# ------------------------------------------------------------
# Обновление CAVA в config.yaml (без перезагрузки YASB)
# ------------------------------------------------------------
def update_cava_config(accent_color, accent_light, accent_dark):
    if not os.path.exists(YASB_CONFIG_PATH):
        print("⚠️ config.yaml не найден, пропускаем обновление CAVA.")
        return

    try:
        with open(YASB_CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        if 'widgets' in config and 'cava' in config['widgets']:
            cava = config['widgets']['cava']
            if 'options' in cava:
                cava['options']['foreground'] = accent_color
                cava['options']['gradient_color_1'] = accent_light
                cava['options']['gradient_color_2'] = accent_color
                cava['options']['gradient_color_3'] = accent_dark
                print(f"🎵 Цвета CAVA обновлены: fg={accent_color}, grad1={accent_light}, grad2={accent_color}, grad3={accent_dark}")
            else:
                print("⚠️ В виджете cava нет секции options")
        else:
            print("⚠️ Виджет cava не найден в config.yaml")

        with open(YASB_CONFIG_PATH, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    except Exception as e:
        print(f"⚠️ Ошибка обновления CAVA: {e}")

# ------------------------------------------------------------
# Обновление CSS YASB (с адаптацией под светлый/тёмный акцент)
# ------------------------------------------------------------
def update_css_with_accent(accent_color):
    if not os.path.exists(CSS_PATH):
        print(f"❌ Файл {CSS_PATH} не найден.")
        return

    r, g, b = hex_to_rgb(accent_color)
    accent_rgb = f"{r}, {g}, {b}"

    luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
    is_light = luminance > 128

    if is_light:
        accent_light = mix_colors(accent_color, "#000000", 0.2)
        accent_dark = mix_colors(accent_color, "#000000", 0.5)
        accent_bg = mix_colors(accent_color, "#ffffff", 0.1)
        accent_text = mix_colors(accent_color, "#000000", 0.8)
        accent_bg_soft = mix_colors(accent_color, "#ffffff", 0.2)
        accent_border = mix_colors(accent_color, "#000000", 0.3)
        accent_hover = mix_colors(accent_color, "#000000", 0.25)
        accent_disabled = mix_colors(accent_color, "#888888", 0.5)
        surface = mix_colors(accent_color, "#ffffff", 0.85)
        mantle = rgba_to_css(r, g, b, 0.3)
        subtext = mix_colors(accent_color, "#000000", 0.6)
        overlay = mix_colors(accent_color, "#000000", 0.4)
        text_color = mix_colors(accent_color, "#000000", 0.9)
        surface_transparent = rgba_to_css(r, g, b, 0.15)
        mantle_transparent = rgba_to_css(r, g, b, 0.3)
        accent_transparent = rgba_to_css(r, g, b, 0.2)
    else:
        accent_light = mix_colors(accent_color, "#ffffff", 0.4)
        accent_dark = mix_colors(accent_color, "#000000", 0.3)
        accent_bg = mix_colors(accent_color, "#ffffff", 0.8)
        accent_text = mix_colors(accent_color, "#ffffff", 0.9)
        accent_bg_soft = mix_colors(accent_color, "#ffffff", 0.7)
        accent_border = mix_colors(accent_color, "#ffffff", 0.5)
        accent_hover = mix_colors(accent_color, "#ffffff", 0.3)
        accent_disabled = mix_colors(accent_color, "#888888", 0.4)
        surface = mix_colors(accent_color, "#000000", 0.85)
        mantle = rgba_to_css(r, g, b, 0.5)
        subtext = mix_colors(accent_color, "#000000", 0.7)
        overlay = mix_colors(accent_color, "#000000", 0.6)
        text_color = accent_text
        surface_transparent = rgba_to_css(r, g, b, 0.15)
        mantle_transparent = rgba_to_css(r, g, b, 0.3)
        accent_transparent = rgba_to_css(r, g, b, 0.2)

    var_map = {
        '--system-accent': accent_color,
        '--system-accent-rgb': accent_rgb,
        '--system-accent-light': accent_light,
        '--system-accent-dark': accent_dark,
        '--system-accent-bg': accent_bg,
        '--system-accent-text': accent_text,
        '--system-accent-bg-soft': accent_bg_soft,
        '--system-accent-border': accent_border,
        '--system-accent-hover': accent_hover,
        '--system-accent-disabled': accent_disabled,
        '--system-text': text_color,
        '--system-subtext': subtext,
        '--system-overlay': overlay,
        '--system-surface': surface,
        '--system-mantle': mantle,
        '--system-surface-transparent': surface_transparent,
        '--system-mantle-transparent': mantle_transparent,
        '--system-accent-transparent': accent_transparent,
    }

    with open(CSS_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    in_root = False
    root_start = -1
    root_end = -1
    for i, line in enumerate(lines):
        if re.match(r':root\s*\{', line):
            in_root = True
            root_start = i
        if in_root and line.strip() == '}':
            root_end = i
            break

    if root_start == -1 or root_end == -1:
        print("❌ Блок :root не найден. Создаём новый в начале.")
        new_lines = []
        new_lines.append(":root {\n")
        for var, val in var_map.items():
            new_lines.append(f"    {var}: {val};\n")
        new_lines.append("}\n")
        new_lines.extend(lines)
    else:
        new_lines = []
        for i, line in enumerate(lines):
            if root_start < i < root_end:
                stripped = line.lstrip()
                if stripped.startswith('--system-'):
                    continue
            new_lines.append(line)

        new_root_start = -1
        new_root_end = -1
        for i, line in enumerate(new_lines):
            if re.match(r':root\s*\{', line):
                new_root_start = i
            if new_root_start != -1 and line.strip() == '}':
                new_root_end = i
                break

        if new_root_start == -1 or new_root_end == -1:
            print("❌ Ошибка: не удалось найти границы блока :root после очистки.")
            return

        insert_index = new_root_end
        for var, val in var_map.items():
            new_lines.insert(insert_index, f"    {var}: {val};\n")
            insert_index += 1

    new_content = ''.join(new_lines)

    if '--system-accent' not in new_content:
        print("⚠️ Ошибка: новый CSS не содержит системных переменных. Откат к предыдущей версии.")
        if os.path.exists(CSS_BACKUP):
            shutil.copy(CSS_BACKUP, CSS_PATH)
        return

    if os.path.exists(CSS_PATH):
        shutil.copy(CSS_PATH, CSS_BACKUP)

    try:
        with open(CSS_PATH, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✅ Акцентный цвет обновлён на {accent_color}")
    except Exception as e:
        print(f"❌ Ошибка записи CSS: {e}. Восстанавливаем бэкап.")
        if os.path.exists(CSS_BACKUP):
            shutil.copy(CSS_BACKUP, CSS_PATH)
        return

    # ===== ИСПРАВЛЕННЫЙ ПОРЯДОК =====
    # 1. Сначала обновляем CAVA (записываем цвета в config.yaml)
    update_cava_config(accent_color, accent_light, accent_dark)
    # 2. Затем обновляем границы Komorebi
    update_komorebi_border(accent_light)
    # 3. И только потом перезагружаем YASB
    reload_yasb()

# ------------------------------------------------------------
# Перезагрузка YASB
# ------------------------------------------------------------
def reload_yasb():
    try:
        result = subprocess.run(["yasbc", "reload"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("🔄 YASB перезагружен через yasbc")
            return
    except:
        pass

    try:
        subprocess.run(["taskkill", "/F", "/IM", "yasb.exe"], capture_output=True, timeout=5)
        time.sleep(0.5)
        subprocess.Popen(["yasb"], creationflags=subprocess.CREATE_NO_WINDOW)
        print("🔄 YASB перезапущен через taskkill/Popen")
    except Exception as e:
        print(f"⚠️ Не удалось перезагрузить YASB автоматически: {e}")
        print("👉 Перезапустите YASB вручную (или нажмите Reload в трее).")

# ------------------------------------------------------------
# Мониторинг (с двойным чтением цвета для устранения задержки)
# ------------------------------------------------------------
def monitor_accent_color():
    last_color = None
    while True:
        current_color = get_accent_color()
        if current_color != last_color:
            time.sleep(0.3)
            current_color = get_accent_color()
            if current_color != last_color:
                print(f"🔄 Обнаружено изменение цвета: {last_color} -> {current_color}")
                update_css_with_accent(current_color)
                last_color = current_color
        time.sleep(5)

if __name__ == "__main__":
    initial = get_accent_color()
    update_css_with_accent(initial)
    print(f"🔄 Мониторинг цвета (текущий: {initial})...")
    monitor_accent_color()