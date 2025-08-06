import json
import keyboard
import datetime
import csv
import zmq


### String Definitions ###
welcome = """
Welcome to CollectionDB! Please make a selection from the options below:"""

mainMenu = """ --- Main Menu ---
  (V) – View List of Collectables       - Shows only Name and Type
  (W) – View List with Date/Comments    - Shows all information on each item
  (S) - Search for Collectable(s)       - Search for items that match a keyword
  (O) - Sort Collection                 - Sort collection by name or date
  (A) – Add Collectable                 - Enter a new item to be tracked
  (I) - Import Collectable(s) from .csv - Adds item(s) from a .csv file
  (E) - Export Collection to .csv       - Exports collection to a .csv file
  (D) – Delete Collectable              – Removes an item from the list
  (U) – Undo Last Delete                - Restores the last item deleted
  (C) - Collection Management           - Change collection properties
  (Q) - Quit/Exit                       - Exits the collection tracker

Which option would you like?:"""

collectionMenu = """\n --- Collection Menu ---
  (C) – Change Collection Name          - Change name of the current collection
  (V) – View List of Collections        - View list of available collections
  (L) - Load Collection                 - Change to a different collection
  (N) - Create New Collection           - Creates a new blank collection
  (R) - Return to Main Menu             - Exits the collection tracker

Which option would you like?:"""


### Class Definitions and Helper Functions ###
class CollectionList:

    def __init__(self, values: str) -> None:
        data = json.loads(values)
        if len(data) != 0:
            self.name = data[0]
            self.values = data[1]
        else:
            self.name = None
            self.values = dict()
        self.delete_backup = None

    def get_json_str(self) -> str:
        return json.dumps([self.name, self.values])


def save_collection(collection):
    with open("data", 'w') as file:
        file.write(collection.get_json_str())

def start_collection():
    print("\nThere is no currently active collection.\n")
    print("Please provide a name for a new collection:")
    name = input("  ")

    collection.name = name
    save_collection(collection)


### Menu Option Functions ###
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

def search_collection(value_list):
    print("What do you want to search for? (will search name, type, and comment fields)")
    search_term = input("  ")

    context = zmq.Context()
    server = context.socket(zmq.REQ)
    server.connect("tcp://localhost:5363")

    server.send_json([search_term, value_list])
    response = server.recv_json()
    server.close()

    if response != dict():
        print("Found the following items\n")
        display_big_list(response)
    else:
        print("\nNo items found that match your search.")
        print("Press <spacebar> to return to the Main Menu\n")
        keyboard.wait('space')

def sort_collection(collection):
    print("Do you want to sort by (n)ame or (d)ate?")
    column = input("  ").lower()
    print("(A)scending or (d)escending?")
    order = input("  ").lower()

    if column == "n" or column == "name":
        column = "name"
    elif column == "d" or column == "date":
        column = "date"
    else:
        print("Column name not recognized!")
        return

    if order in ("a", "asc", "ascending"):
        order = "asc"
    elif order in ("d", "dsc", "desc", "descending"):
        order = "dsc"
    else:
        print("Sort order not recognized!")
        return

    context = zmq.Context()
    server = context.socket(zmq.REQ)
    server.connect("tcp://localhost:5362")

    request_data = [column, order, collection.values]
    server.send_json(request_data)
    response = server.recv_json()
    server.close()

    if response[0]:
        collection.values = response[1]
        save_collection(collection)

        print(f"Collection sorted by {column} in {order} order!")
        view = input("Would you like to view the collection now? ").lower().strip()
        if view == "y" or view == "yes":
            display_big_list(collection.values)

    else:
        print(f"Error: {response[1]}")


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
        save_collection(collection)
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
        save_collection(collection)
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
            save_collection(collection)
            print("*** " + name + " deleted! ***")
        else:
            print("*** " + name + " NOT deleted! ***")

    else:
        print(name + " not found in the collection list.")

def export_collection(values):
    print("What should the csv file be named?")
    filename = input("  ")

    if filename[-4:].lower() != ".csv":
        filename += ".csv"
    filename = "../exports/" + filename
    export_data = [filename, values]

    context = zmq.Context()
    server = context.socket(zmq.REQ)
    server.connect("tcp://localhost:5361")

    server.send_json(export_data)
    response = server.recv_string()
    print(response)

    server.close()

def undo_delete(collection):
    if collection.delete_backup is not None:
        print("Restore this item?")
        display_big_list(collection.delete_backup, False)
        print("Yes/(No)?")
        verify = input("  ").lower().strip()
        name = set(collection.delete_backup).pop()[0]

        if verify == "y" or verify == "yes":
            collection.values.update(collection.delete_backup)
            save_collection(collection)
            collection.delete_backup = None
            print("*** " + name + " restored! ***")
        else:
            print("*** " + name + " NOT restored! ***")
    else:
        print("No deleted item was found to restore.")

def manage_collection(collection):

    context = zmq.Context()
    server = context.socket(zmq.REQ)
    server.connect("tcp://localhost:5364")

    user_input = ""

    while user_input != "r":
        print(f"\n            === Collection Menu For: {collection.name} ===")
        print(collectionMenu)
        user_input = input(" ").lower().strip()

        if user_input == "c":
            print("What is the new name for this collection?")
            print(f"Current name is {collection.name}.")
            name = input("  ")

            collection.name = name
            save_collection(collection)

        elif user_input == "v":
            server.send_json(["list"])
            response = server.recv_json()
            print("The list of available collections is below:")

            if response[0]:
                if response[1] == []:
                    print("No collections avialable")
                else:
                    for item in response[1]:
                        print(f" - {item}")
                print("\nPress <spacebar> to return to the Collection Menu\n")
                keyboard.wait('space')
            else:
                print("Error: " + response[1])

        elif user_input == "l":
            print("What is the name for the collection you want to load?")
            name = input("  ")

            server.send_json(["load", name, [collection.name, collection.values]])
            response = server.recv_json()

            if response[0]:
                collection = CollectionList(json.dumps(response[1]))
                save_collection(collection)
                print(f"Loaded {response[0]} collection")
            else:
                print(f"Collection {name} not found")

        elif user_input == "n":
            print("What is the name the new collection?")
            name = input("  ")
            server.send_json(["save", collection.name, collection.values])
            response = server.recv_json()

            if response[0]:
                collection = CollectionList("[\"" + name + "\", { }]")
                save_collection(collection)
                server.send_json(["save", name, collection.values])
                response = server.recv_json()
                if response[0]:
                    print(f"\nNew collection, {name}, created.  {name} is now the active collection.")

    server.close()


### Main Function ###
if __name__ == '__main__':

    with open("data", 'r') as file:
        file_content = file.read()
    collection = CollectionList(file_content)

    if collection.name is None:
        start_collection()

    print(welcome)
    user_input = ""

    while user_input != "q":
        print(f"\n            === Viewing Collection: {collection.name} ===\n")
        print(mainMenu)
        user_input = input(" ").lower().strip()

        if user_input == "v":
            display_small_list(collection.values)
        elif user_input == "w":
            display_big_list(collection.values)
        elif user_input == "s":
            search_collection(collection.values)
        elif user_input == "o":
            sort_collection(collection)
        elif user_input == "a":
            add_collectable(collection)
        elif user_input == "i":
            import_collectables(collection)
        elif user_input == "e":
            export_collection(collection.values)
        elif user_input == "d":
            delete_collectable(collection)
        elif user_input == "u":
            undo_delete(collection)
        elif user_input == "c":
            manage_collection(collection)
            with open("data", 'r') as file:
                file_content = file.read()
            collection = CollectionList(file_content)

    print("\nThank you for using CollectionDB!")