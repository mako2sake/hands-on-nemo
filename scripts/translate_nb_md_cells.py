"""ipynbのmarkdown cellのみを翻訳して保存するスクリプト

uvxとplamo-translate-cliを使っているため
それぞれが動作する環境が必須
（後者はmacOSのみに対して最適化されているようです）
"""

import argparse
import json
from pathlib import Path
import subprocess

from tqdm import tqdm


def run_plamo_trans(target: str):
    """plamo-translateを実行して翻訳結果を返す
    """
    result = subprocess.run(
        ["uvx", "plamo-translate"],
        input=target,
        capture_output=True,
        text=True
    )
    return result.stdout.strip()


def exec_translate(input_path: Path):
    """ipynbのmarkdonwセルのみを翻訳する

    出力は入力と同じファイル名に_jaをつけたもの
    """
    with open(input_path, encoding="utf-8") as f_in:
        data = json.load(f_in)
    # tqdmでラップしてやる
    for cell in tqdm(data.get("cells", []), desc="Trasnlating MD Cell"):
        if cell.get('cell_type') == 'markdown':
            cell['source'] = [
                run_plamo_trans(line)
                    if line not in ["\n", "```", "```\n"] else line
                    for line in cell['source']
            ]
    output_path = input_path.parent / input_path.name.replace(".ipynb", "_ja.ipynb")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path, help="入力となるファイルパス")
    args = parser.parse_args()
    exec_translate(args.input)
