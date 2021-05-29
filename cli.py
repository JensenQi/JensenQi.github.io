import sys
import os
from collections import OrderedDict
import datetime
import shutil
import readline

HEADER = '\033[95m'
BLUE = '\033[94m'
CYAN = '\033[96m'
GREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
END = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'


def get_article_list():
    return sorted([article for article in os.listdir("_posts")])


def find_unlinked_assets():
    files = []
    article_assets = [
        os.path.join("assets", d) for d in os.listdir("assets")
        if os.path.isdir(os.path.join("assets", d)) and d not in ("css", "images")
    ]
    for assets in article_assets:
        files += [os.path.join(assets, f) for f in os.listdir(assets)]

    for article in get_article_list():
        article = ''.join(open("_posts" + "/" + article, encoding='utf8').readlines())
        files = [f for f in files if f not in article]

    for file in files:
        print(f"{file}")
    return


def create_article():
    sys.stdout.write("\nArticle title (default draft): ")
    title = sys.stdin.readline().strip() or "draft"

    today = str(datetime.date.today())
    sys.stdout.write(f"\nDate (default {today}): ")
    date = sys.stdin.readline().strip() or today
    date = date[:4] + "-" + date[4:6] + "-" + date[-2:] if len(date) == 8 else date

    file_name = f"{date}-{title.replace(' ', '-')}.md"
    file = open("_posts" + "/" + file_name, "w", encoding='utf8')
    file.writelines('---\n')
    file.writelines(f'title: {title}\n')
    file.writelines('tags: tag1 tag2\n')
    file.writelines('mermaid: false\n')
    file.writelines('chart: false\n')
    file.writelines('mathjax: false\n')
    file.writelines('mathjax_autoNumber: true\n')
    file.writelines('typora-root-url: ..\n')
    file.writelines('typora-copy-images-to: ../assets/${filename}\n')
    file.writelines('---\n\n')
    file.close()


def delete_article():
    articles = get_article_list()
    for idx, article in enumerate(articles):
        sys.stdout.write(f"{idx}) {article}\n")
    sys.stdout.write("\nselect article id or article name to delete: ")
    selected = sys.stdin.readline().strip()
    try:
        article_id = int(selected)
        file_name = articles[article_id]
    except Exception:
        file_name = selected
    os.remove(f"_posts/{file_name}")
    print(f"remove _posts/{file_name}")

    shutil.rmtree(f"assets/{file_name.replace('.md', '')}", ignore_errors=True)
    print(f"remove assets/{file_name.replace('.md', '')}")


def get_input(prompt, prefill=''):
    readline.set_startup_hook(lambda: readline.insert_text(prefill))
    try:
        return input(prompt)
    finally:
        readline.set_startup_hook()


def rename_article():
    articles = get_article_list()
    for idx, article in enumerate(articles):
        sys.stdout.write(f"{idx}) {article.replace('.md', '')}\n")
    sys.stdout.write("\nselect article id or article name to rename: ")
    old_file_name = sys.stdin.readline().strip()
    try:
        old_file_name = articles[int(old_file_name)].replace(".md", "")
    except:
        old_file_name = old_file_name

    sys.stdout.write(f"\nset new file name ({old_file_name}): \n")
    new_file_name = input().strip()
    new_title = new_file_name[11:].replace("-", " ")

    old_file = open(f"_posts/{old_file_name}.md", "r", encoding="utf8")
    new_file = open(f"_posts/{new_file_name}.md", "w", encoding="utf8")

    old_asset = f'assets/{old_file_name}/'
    new_asset = f'assets/{new_file_name}/'

    for line in old_file:
        if line.startswith("title: "):
            new_file.writelines(f"title: {new_title}\n")
        elif old_asset in line:
            new_file.writelines(f"{line.replace(old_asset, new_asset)}")
        else:
            new_file.writelines(f"{line}")
    old_file.close()
    new_file.close()

    if os.path.exists(f"assets/{old_file_name}"):
        shutil.move(f"assets/{old_file_name}", f"assets/{new_file_name}")
    os.remove(f"_posts/{old_file_name}.md")


command_mapping = OrderedDict()
command_mapping["1"] = ("Create article", create_article)
command_mapping["2"] = ("Find unlinked assets", find_unlinked_assets)
command_mapping["3"] = ("Delete article", delete_article)
command_mapping["4"] = ("Rename article", rename_article)

if __name__ == '__main__':
    cmd_list = "\n".join([f"{cmd_id}) {cmd_name}" for cmd_id, (cmd_name, _) in command_mapping.items()])
    sys.stdout.write(f'command:\n{cmd_list}\n')
    sys.stdout.write(f"-------------\n\nSelect command id(default 1): ")

    command_id = sys.stdin.readline().strip() or "1"
    cmd_func = command_mapping.get(command_id)[1]
    cmd_func()

