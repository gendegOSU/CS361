import json
import keyboard
import datetime
import csv

welcome = """
Welcome to CollectionDB! Please make a selection from the options below:"""

mainMenu = """\n === Main Menu ===
  (V) – View List of Collectables       - Shows only Name and Type
  (W) – View List with Date/Comments    - Shows all information on each item
  (A) – Add Collectable                 - Enter a new item to be tracked
  (C) - Add Collectable(s) from .csv    - Adds item(s) from a .csv file
  (D) – Delete Collectable              – Removes an item from the list
  (U) – Undo Last Delete                - Restores the last item deleted
  (Q) - Quit/Exit                       - Exits the collection tracker

Which option would you like?:"""


class CollectionList:

    def __init__(self, values: str) -> None:
        self.values = json.loads(values)
        self.delete_backup = None

    def get_str(self) -> str:
        return json.dumps(self.values)


def display_small_list(value_list):
    name_width = 10
    type_width = 10
    for key, values in value_list.items():
        if len(key) > name_width:
            name_width = len(key)
        if len(values["type"]) > type_width:
            type_width = len(values["type"])
    name_width += 2
    type_width += 2
    full_width = name_width + type_width + 3

    output = "\n" + "=" * full_width + "\n"
    output += "║ Name" + " " * (name_width - 5) + "║ Type" + " " * (type_width - 5) + "║\n"
    output += "=" * (3 + name_width + type_width) + "\n"

    first = True
    for key, values in value_list.items():
        if not first:
            output += "-" * full_width + "\n"
        first = False
        name_pad = (name_width - len(key) - 1)
        type_pad = (type_width - len(values["type"]) - 1)
        output += "║ " + key + " " * name_pad + "| " + values["type"] + " " * type_pad + "║\n"

    output += "=" * full_width + "\n\n"
    output += "Press <spacebar> to return to the Main Menu\n"

    print(output)
    keyboard.wait('space')

def display_big_list(value_list, wait = True):
    name_width = 10
    type_width = 10
    for key, values in value_list.items():
        if len(key) > name_width:
            name_width = len(key)
        if len(values["type"]) > type_width:
            type_width = len(values["type"])
    name_width += 2
    type_width += 2
    date_width = 13
    comment_width = (80 - name_width - type_width - date_width)
    if comment_width < 25:
        comment_width = 25
    full_width = name_width + type_width + date_width + comment_width + 5

    output = "\n" + "=" * full_width + "\n"
    output += "║ Name" + " " * (name_width - 5) + "║ Type" + " " * (type_width - 5) + "║"
    output += " Added" + " " * (date_width - 6) + "║ Comments" + " " * (comment_width - 9) + "║\n"
    output += "=" * full_width + "\n"

    first = True
    for key, values in value_list.items():
        if not first:
            output += "-" * full_width + "\n"
        first = False
        name_pad = (name_width - len(key) - 1)
        type_pad = (type_width - len(values["type"]) - 1)
        date_pad = (date_width - len(values["added"]) - 1)

        comments = values["comment"]
        comment_pad = (comment_width - len(comments) - 1)
        more_comments = False

        output += "║ " + key + " " * name_pad + "| " + values["type"] + " " * type_pad + "| "

        if len(comments) > comment_width - 2:
            more_comments = True
            comments = comments[:comment_width - 2]
            row = 1
            comment_pad = 1

        output += values["added"] + " " * date_pad + "| " + comments + " " * comment_pad + "║\n"

        while more_comments:
            output += "║" + " " * name_width + "|" + " " * type_width + "|" + " " * date_width + "| "

            start = row * (comment_width - 2)
            if len(values["comment"]) - start <= comment_width - 2:
                more_comments = False
                comment_pad = (comment_width - (len(values["comment"]) - start) - 1)
                comments = values["comment"][start:]
            else:
                comments = values["comment"][start:start + comment_width - 2]
                row += 1
            output += comments + " " * comment_pad + "║\n"

    output += "=" * full_width + "\n\n"
    if wait:
        output += "Press <spacebar> to return to the Main Menu\n"

    print(output)
    if wait:
        keyboard.wait('space')

def add_collectable(collection):
    print("Please enter your new collectable’s name and type (you can add general comments at the end).")
    print("What is the collectable’s name? (Question 1 of 3)")
    name = input("  ")
    print("What is the collectable’s type? (Question 2 of 3)")
    type = input("  ")
    print("Please enter any additional comments for this collectable: (Question 3 of 3)")
    comments = input("  ")

    date = datetime.datetime.today()
    today = date.strftime("%d %b %Y")
    if today[0] == "0":
        today = today[1:]
    new_item = {name: {"type": type, "added": today, "comment": comments}}

    print("\nAdd this collectable?")
    display_big_list(new_item, False)
    print("Yes/(No)?")
    verify = input("  ").lower().strip()

    if verify == "y" or verify == "yes":
        collection.values.update(new_item)
        with open("data", 'w') as file:
            file.write(collection.get_str())
        print("*** " + name + " added! ***")
    else:
        print("*** " + name + " NOT added! ***")

def import_collectables(collection):
    print("What is the name of the file you want to import?")
    file_name = input("  ")

    with open(file_name, "r", newline="") as csv_file:
        new_items = dict()
        csv_data = csv.reader(csv_file)

        for row in csv_data:
            new_item = {row[0]: {"type": row[1], "added": row[2], "comment": row[3]}}
            new_items.update(new_item)

    print("Add the following items?")
    display_big_list(new_items, False)
    print("Yes/(No)?")
    verify = input("  ").lower().strip()

    if verify == "y" or verify == "yes":
        collection.values.update(new_items)
        with open("data", 'w') as file:
            file.write(collection.get_str())
        print("*** New items were imported! ***")
    else:
        print("*** New items were NOT imported! ***")

def delete_collectable(collection):
    print("What is the name of the item you would like to delete?")
    name = input("  ")

    if name in collection.values:
        item = {name: collection.values[name]}

        print("Delete this item?")
        display_big_list(item, False)
        print("Yes/(No)?")
        verify = input("  ").lower().strip()

        if verify == "y" or verify == "yes":
            collection.delete_backup = item
            del collection.values[name]
            with open("data", 'w') as file:
                file.write(collection.get_str())
            print("*** " + name + " deleted! ***")
        else:
            print("*** " + name + " NOT deleted! ***")

    else:
        print(name + " not found in the collection list.")

def undo_delete(collection):
    if collection.delete_backup is not None:
        print("Restore this item?")
        display_big_list(collection.delete_backup, False)
        print("Yes/(No)?")
        verify = input("  ").lower().strip()
        name = set(collection.delete_backup).pop()[0]

        if verify == "y" or verify == "yes":
            collection.values.update(collection.delete_backup)
            with open("data", 'w') as file:
                file.write(collection.get_str())
            collection.delete_backup = None
            print("*** " + name + " restored! ***")
        else:
            print("*** " + name + " NOT restored! ***")
    else:
        print("No deleted item was found to restore.")


if __name__ == '__main__':

    with open("data", 'r') as file:
        file_content = file.read()
    collection = CollectionList(file_content)

    print(welcome)
    userInput = ""

    while userInput != "q":
        print(mainMenu)
        userInput = input(" ").lower().strip()

        if userInput == "v":
            display_small_list(collection.values)
        elif userInput == "w":
            display_big_list(collection.values)
        elif userInput == "a":
            add_collectable(collection)
        elif userInput == "c":
            import_collectables(collection)
        elif userInput == "d":
            delete_collectable(collection)
        elif userInput == "u":
            undo_delete(collection)

