"""
Переименовывает Excel-файлы, перемещая номер заказа (№XXX) в начало имени.
"""

import re
import sys
from pathlib import Path


ORDER_PATTERN = re.compile(r'^№\d+$')


def find_order_number(parts: list[str]) -> tuple[str, int] | tuple[None, None]:
    """Ищет часть вида №123 в списке частей имени файла."""
    for i, part in enumerate(parts):
        if ORDER_PATTERN.match(part):
            return part, i
    return None, None


def build_new_name(stem: str, suffix: str) -> str | None:
    """Возвращает новое имя файла или None, если шаблон не найден."""
    parts = stem.split('_')
    order_num, idx = find_order_number(parts)
    if order_num is None:
        return None
    # Если номер уже в начале — ничего делать не нужно
    if idx == 0:
        return None
    remaining = parts[:idx] + parts[idx + 1:]
    new_stem = order_num + '_' + '_'.join(remaining)
    return new_stem + suffix


def scan_folder(folder: Path) -> list[tuple[Path, Path]]:
    """Возвращает список (старый путь, новый путь) для файлов, требующих переименования."""
    renames = []
    for f in sorted(folder.iterdir()):
        if not f.is_file():
            continue
        if f.suffix.lower() not in ('.xlsx', '.xls', '.xlsm', '.xlsb'):
            continue
        new_name = build_new_name(f.stem, f.suffix)
        if new_name:
            renames.append((f, f.parent / new_name))
    return renames


def print_plan(renames: list[tuple[Path, Path]]) -> None:
    col = max(len(src.name) for src, _ in renames) + 2
    print(f"\n{'БЫЛО':<{col}}  →  СТАНЕТ")
    print('-' * (col + 4 + col))
    for src, dst in renames:
        conflict = ' ⚠ УЖЕ СУЩЕСТВУЕТ' if dst.exists() else ''
        print(f"{src.name:<{col}}  →  {dst.name}{conflict}")
    print()


def main() -> None:
    if len(sys.argv) > 1:
        folder = Path(sys.argv[1])
    else:
        raw = input("Введите путь к папке с файлами (Enter = текущая): ").strip()
        folder = Path(raw) if raw else Path('.')

    if not folder.is_dir():
        print(f"Ошибка: папка не найдена — {folder}")
        sys.exit(1)

    print(f"\nСканирую: {folder.resolve()}")
    renames = scan_folder(folder)

    if not renames:
        print("Файлов для переименования не найдено.")
        return

    print(f"Найдено файлов для переименования: {len(renames)}")
    print_plan(renames)

    conflicts = [dst for _, dst in renames if dst.exists()]
    if conflicts:
        print(f"⚠  Обнаружено конфликтов (файл уже существует): {len(conflicts)}")
        print("   Такие файлы будут пропущены.\n")

    answer = input("Выполнить переименование? [y/N]: ").strip().lower()
    if answer != 'y':
        print("Отменено.")
        return

    ok = skipped = 0
    for src, dst in renames:
        if dst.exists():
            print(f"  ПРОПУСК (конфликт): {src.name}")
            skipped += 1
            continue
        try:
            src.rename(dst)
            print(f"  ОК: {src.name}  →  {dst.name}")
            ok += 1
        except OSError as e:
            print(f"  ОШИБКА: {src.name} — {e}")
            skipped += 1

    print(f"\nГотово: переименовано {ok}, пропущено {skipped}.")


if __name__ == '__main__':
    main()
