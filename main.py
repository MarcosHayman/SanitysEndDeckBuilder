import sqlite3
from prettytable import from_db_cursor, TableStyle, HRuleStyle, PrettyTable
from menuManager import createMenu

import repository

CARD_TYPES = ["creature", "event", "permanent"]
REGIONS = ["dungeon", "graveyard", "academy", "fishing hamlet", "church", "town", "forest"]
DB_FILE_NAME = repository.DB_FILE_NAME

def create_main_menu():
    print("Welcome to Insight Apparatus, the Sanity's End Deck Builder!\n")
    createMenu("What would you like to do?", 
        {
            "View your decks": view_decks_menu,
            "List the cards": list_cards,
            "Create a deck": create_deck_menu,
            "Import deck (from file in untap deck format)": import_from_untap,
            "Exit": lambda: print("Exiting program")
        })

def view_decks_menu() -> str:
    createMenu(deck_viewing_intro, {
        "View a deck": view_deck,
        "Edit a deck": edit_deck,
        "Delete a deck": delete_deck,
        "Create a new deck": create_deck_menu,
        "Return to the Main Menu": no_op
    })
    return "Returning to main menu"

def deck_viewing_intro() -> str:
    repository.print_all_decks()
    return "Would you like to:"

def view_deck() -> str:
    chosen_deck = input("Which deck do you want to view?\n")
    try:
        id = int(chosen_deck)
    except TypeError as e:
        id = int(repository.find_deck_id_by_name(chosen_deck))
    deck = {"id": id}
    createMenu(single_deck_view_intro,{
        "Register Win": register_win,
        "Register Loss": register_loss,
        "Edit deck": edit_deck_menu,
        "Delete deck": delete_deck_with_id,
        "Return to previous menu": lambda _: no_op()
    }, intro_arg=deck, option_func_arg=deck)
    return "Returning to previous menu"

# Mutates deck input arg
def single_deck_view_intro(deck) -> str:
    deck_id: int = deck["id"]
    analysis = repository.get_deck_analysis_by_id(deck_id)
    deck["analysis"] = analysis
    stats = analysis["stats"]
    print(stats["name"] + ":")
    repository.print_deck_cards_by_id(deck_id)
    if stats["games"] != 0:
        print(f'Wins: {stats["wins"]}\tGames: {stats["games"]}\tWin rate: {100*stats["wins"]/stats["games"]} %')

    print("------------------------")
    print("Regions")
    for region in analysis["regions"]:
        print(f"{region}: {stats[region]} ({100*stats[region]/stats['total']} %)")
        
    print("------------------------")
    print("Card Types")
    for card_type in CARD_TYPES:
        if stats[card_type] is not None:
            print(f"{card_type}: {stats[card_type]} ({100*stats[card_type]/stats["total"]} %)")

    print("------------------------")
    print("Madness Curve")
    for i in range(6):
        collumn_name = f"mad_{i}"
        madness = 0 if stats[collumn_name] is None else stats[collumn_name] 
        print(f"{i}: {madness} {'-'*madness} ({100*madness/stats["total"]} %)")

    input("Press Enter to continue\n")
    return "What do you want to do with this Deck?"

def create_deck_menu() -> str:
    name = input("Enter the name of the deck: ")
    deck = {
        "name": name,
        "total": 0,
        "cards": [],
        "regions": [],
        "madness": [],
        "types": [
            {"name": "creature", "quantity": 0},
            {"name": "event", "quantity": 0},
            {"name": "permanent", "quantity": 0}
        ],
    }
    for i in range(6):
        deck["madness"].append(0)
    createMenu(create_deck_intro,{
        "Add a card": add_card_to_deck,
        "Remove a card": remove_card_from_deck,
        "List cards": lambda _: list_cards(),
        "Save deck": save_deck,
        "Print deck (to file, in untap format)": export_to_untap,
        "Close (without saving)": lambda _: print("Closing without saving...")
    }, intro_arg=deck, option_func_arg=deck)
    return "Returning to previous menu"

def create_deck_intro(deck) -> str:
    generate_partial_deck_view(deck)
    return "What do you want to do?"

def generate_partial_deck_view(deck) -> None:
    if deck["total"] == 0:
        return
    print(f"\n\nYour current deck: {deck['name']}")
    print("-------------------------------")
    print("Cards per region:")
    for region in deck["regions"]:
        print(f"{region['quantity']} - {region['name']}")
    print('\nCards per type:')
    for type in deck["types"]:
        print(f"{type['quantity']} - {type['name']}")
    print("\nMadness Curve:")
    for i in range(6):
        mad = deck["madness"][i]
        print(f"{i}: {mad} {'-'*mad} ")

    print(f"\nCards in deck ({deck['total']}):")
    for card in deck["cards"]:
        print(f"{card['quantity']}x {card['name']} - {card['region']} {card['type']}")

def edit_deck_menu(deck_analysis) -> str:
    print(deck_analysis)
    deck = create_in_memory_deck_from_analysis(deck_analysis)
    createMenu(create_deck_intro,{
        "Add a card": add_card_to_deck,
        "Remove a card": remove_card_from_deck,
        "List cards": lambda _: list_cards(),
        "Save deck": save_deck,
        "Print deck (to file, in untap format)": export_to_untap,
        "Close (without saving)": lambda _: print("Closing without saving...")
    }, intro_arg=deck, option_func_arg=deck)
    return "Returning to previous menu"

def create_in_memory_deck_from_analysis(deck_view) -> dict:
    deck_anlysis = deck_view["analysis"]
    deck = {
        "id": deck_view["id"],
        "name": deck_anlysis["stats"]["name"],
        "total": deck_anlysis["stats"]["total"],
        "regions": [],
        "cards": [],
        "madness": [],
        "types": [
            {"name": "creature", "quantity": deck_anlysis["stats"]["creature"]},
            {"name": "event", "quantity": deck_anlysis["stats"]["event"]},
            {"name": "permanent", "quantity": deck_anlysis["stats"]["permanent"]}
        ],
    }
    for i in range(6):
        madness = deck_anlysis["stats"][f"mad_{i}"]
        deck["madness"].append(madness if madness is not None else 0)
    cards = repository.get_cards_for_deck_id(deck_view["id"])
    for card in cards:
        deck["cards"].append({
            "id": card["id"],
            "name": card["name"],
            "region": card["region"],
            "type": card["type"],
            "madness": card["madness"],
            "quantity": card["quantity"]
        })
    for region in deck_anlysis["regions"]:
        deck["regions"].append({
            "name": region,
            "quantity": deck_anlysis["stats"][region]
        })
    return deck

def register_win(deck) -> str:
    deck_id = deck["id"]
    repository.register_win_for_deck(deck_id)
    return "Registered a Win for the Deck!"

def register_loss(deck) -> str:
    deck_id = deck["id"]
    repository.register_loss_for_deck(deck_id)
    return "Registered a Loss for the Deck"

def delete_deck() -> str:
    deck = input("Which deck do you wish to delete?\n")
    try:
        deck_id = int(deck)
    except TypeError:
        deck_id = repository.find_deck_id_by_name(deck)
    return delete_deck_with_id(deck_id)

def delete_deck_with_id(deck) -> str:
    deck_id = deck["id"] if isinstance(deck, dict) else deck
    repository.delete_deck_by_id(deck_id)
    return f"Deck with id {deck_id} deleted"

def add_card_to_deck(deck) -> str:
    with sqlite3.connect(DB_FILE_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        card_name = input("Enter the name of the card: ")
        cursor.execute('SELECT * FROM cards where lower(name) = ? limit 1', (card_name.lower().strip(),))
        card = cursor.fetchone()
        if not card:
            return f"Card '{card_name}' not found"
        else:
            card_region = card["region"]
            card_type = card["type"]
            card_quantity = int(input(f"How many copies of {card_name} do you want to add?\n"))
            card_exists = False
            add_quantity = 0
            for existing_card in deck["cards"]:
                if existing_card["name"] == card_name:
                    add_quantity = min(card_quantity + existing_card["quantity"], 2)
                    existing_card["quantity"] = add_quantity
                    deck["total"] += add_quantity - existing_card["quantity"]
                    card_exists = True
                    break
            if not card_exists:
                add_quantity= min(card_quantity, 2)
                deck["cards"].append({
                    "id": card["id"],
                    "name": card["name"],
                    "region": card_region,
                    "type": card_type,
                    "madness": card["madness"],
                    "quantity": add_quantity
                })
                deck["total"] += add_quantity
            deck["madness"][card["madness"]] += add_quantity
            region_exists = False
            for region in deck["regions"]:
                if region["name"] == card_region:
                    region["quantity"] += add_quantity
                    region_exists = True
                    break
            if not region_exists:
                deck["regions"].append({
                    "name": card_region,
                    "quantity": add_quantity
                })
            for type in deck["types"]:
                if type["name"] == card_type:
                    type["quantity"] += add_quantity
                    break
            return f"Added {add_quantity} {card['name']} to Deck" 

def remove_card_from_deck(deck) -> str:
    card_name = input("Enter the name of the card: ")
    for existing_card in deck["cards"]:
        if existing_card["name"].lower() == card_name.lower().strip():
            card_region = existing_card["region"]
            card_type = existing_card["type"]
            card_quantity = int(input(f"How many copies of {existing_card['name']} do you want to remove?\n"))
            if card_quantity > existing_card["quantity"]:
                card_quantity = existing_card["quantity"]
            deck["total"] -= card_quantity
            existing_card["quantity"] -= card_quantity
            if existing_card["quantity"] == 0:
                deck["cards"].remove(existing_card)
            deck["madness"][existing_card["madness"]] -= card_quantity
            for region in deck["regions"]:
                if region["name"] == card_region:
                    region["quantity"] -= card_quantity
                    if region["quantity"] == 0:
                        deck["regions"].remove(region)
                    break
            for type in deck["types"]:
                if type["name"] == card_type:
                    type["quantity"] -= card_quantity
                    break
            return f"{card_quantity} '{existing_card['name']}' were removed from the Deck"
    return f"Card '{card_name}' not found in your deck."

def save_deck(deck) -> str:
    with sqlite3.connect(DB_FILE_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM decks where name = ? limit 1', (deck["name"],))
        existing_deck = cursor.fetchone()
        if existing_deck:
            deck_id = existing_deck["id"]
        else:
            cursor.execute('INSERT INTO decks (name) VALUES (?)', (deck["name"],))
            conn.commit()
            cursor.execute('SELECT id FROM decks where name = ? limit 1', (deck["name"],))
            deck_id = cursor.fetchone()["id"]
        cursor.execute('DELETE FROM deck_cards WHERE deck_id = ?', (deck_id,))
        for card in deck["cards"]:
            cursor.execute('INSERT INTO deck_cards (deck_id, card_id, quantity) VALUES (?, ?, ?)', (deck_id, card["id"], card["quantity"]))
        conn.commit()
        return "Deck saved successfully!"

def export_to_untap(deck) -> str:
    file_name = input("Enter the name for the file to save to:")
    with open(file_name + ".txt", "w") as file:
        file.write(f'//{deck["name"]}\n')
        for card in deck["cards"]:
            file.write(f"{card["quantity"]} {card["name"]} (se1)\n")
    return f'Saved to file {file_name}.txt'

def import_from_untap():
    file_name = input("Enter the name of the file to import: ")
    with open(file_name, "r") as file:
        lines = file.readlines()
        deck_name = lines[0].replace("//", "").strip()
        deck = {
            "name": deck_name,
            "total": 0,
            "cards": [],
            "regions": [],
            "types": [
                {"name": "creature", "quantity": 0},
                {"name": "event", "quantity": 0},
                {"name": "permanent", "quantity": 0}
            ],
        }
        skipped = []
        for line in lines[1:]:
            quantity = int(line.split(" ")[0])
            card_name = " ".join(line.split(" ")[1:]).split("(")[0]
            with sqlite3.connect(DB_FILE_NAME) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM cards where lower(name) = ? limit 1', (card_name.lower().strip(),))
                card = cursor.fetchone()
                if not card:
                    skipped.append(f"Card '{card_name}' not found, skipping...")
                else:
                    card_region = card["region"]
                    card_type = card["type"]
                    card_id = card["id"]
                    card_exists = False
                    for existing_card in deck["cards"]:
                        if existing_card["name"] == card_name:
                            add_quantity = max(existing_card["quantity"], quantity)
                            existing_card["quantity"] = add_quantity
                            deck["total"] += add_quantity - existing_card["quantity"]
                            card_exists = True
                            break
                    if not card_exists:
                        add_quantity= min(quantity, 2)
                        deck["cards"].append({
                            "id": card_id,
                            "name": card_name,
                            "region": card_region,
                            "type": card_type,
                            "quantity": add_quantity
                        })
                        deck["total"] += add_quantity
                    region_exists = False
                    for region in deck["regions"]:
                        if region["name"] == card_region:
                            region["quantity"] += quantity
                            region_exists = True
                            break
                    if not region_exists:
                        deck["regions"].append({
                            "name": card_region,
                            "quantity": quantity
                        })
                    for type in deck["types"]:
                        if type["name"] == card_type:
                            type["quantity"] += quantity
                            break
        save_deck(deck)
        generate_partial_deck_view(deck)
        for skip in skipped:
            print(skip)
        return f"Deck '{deck_name}' imported successfully!"

def edit_deck() -> str:
    chosen_deck = input("Which deck do you want to edit?\n")
    try:
        id = int(chosen_deck)
    except TypeError as e:        
        id = int(repository.find_deck_id_by_name(chosen_deck))
    deck = {"id": id}
    deck["analysis"] = repository.get_deck_analysis_by_id(id)
    return edit_deck_menu(deck)

def list_cards() -> str:
    createMenu("Choose an option:",
    {
        "List all cards": list_all_cards,
        "Filter the options": filter_cards
    })
    return "Returning to main menu"

def list_all_cards() -> str:
    with sqlite3.connect('cards.db') as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, type, region, effect, power, madness FROM cards;')
        table = from_db_cursor(cursor)
    print_card_table(table)

def filter_cards() -> str:
    params = {
        "name": "",
        "type": [],
        "region": [],
        "power": [],
        "madness": [],
        "effect": ""
    }
    createMenu("What do you want to filter by?",
        {
            lambda param: f'name {"(" + param["name"] + ")" if param["name"] != "" else ""}': lambda param: set_str_param_for_list_query(param, "name"),
            lambda param: f'card type {"(" + ",".join(param["type"]) + ")" if param["type"] != [] else ""}': lambda param: add_filter_param_to_list(param, "type", CARD_TYPES),
            lambda param: f'region {"(" + ",".join(param["region"]) + ")" if param["region"] != [] else ""}': lambda param: add_filter_param_to_list(param, "region", REGIONS),
            lambda param: f'effect {"(" + param["effect"] + ")" if param["effect"] != "" else ""}': lambda param: set_str_param_for_list_query(param, "effect"),
            lambda param: f'power {query_integer_condition_to_string(param["power"])}': lambda param: add_integer_condition_param_to_list(param, "power"),
            lambda param: f'madness {query_integer_condition_to_string(param["madness"])}': lambda param: add_integer_condition_param_to_list(param, "madness"),
             "Search with these filters": lambda param: query_card_list_with_params(param)
        }, option_arg=params, option_func_arg=params)

def set_str_param_for_list_query(params, param_type) -> str:
    params[param_type] = input(f"Enter the param_type or part of the param_type of the card")
    return f"Added {param_type} filter"

def print_card_table(table: PrettyTable):
    table.set_style(TableStyle.SINGLE_BORDER)
    table._hrules = HRuleStyle.ALL
    table._align = {"id": "r", "name": "l", "type": "l", "region": "l", "effect": "l", "madness": "r", "power": "r" }
    table._max_width = {"effect": 50}
    print(table)
    input("Press Enter to continue\n")

def add_filter_param_to_list(params: dict, param_type: str, reference_list: list[str]):
    print(f"Choose a {param_type} to search for:\n")
    for i, item in enumerate(reference_list):
        print(f"{i+1}. {item}")
    chosen_type_input = input()
    chosen_type = reference_list[int(chosen_type_input)-1]
    confirmation = input(f"Do you confirm adding '{chosen_type}'? The new list of {param_type} will be: {add_unique_to_array_as_copy(params[param_type], chosen_type)} (Y/n)\n")
    if confirmation.lower() == "y":
        params[param_type] = add_unique_to_array_as_copy(params[param_type], chosen_type)
        return f"Added {chosen_type} to the list of {param_type}"
    return "Nothing added to the filter"

def query_integer_condition_to_string(conditions: list[dict]) -> str:
    if conditions == []:
        return ""
    result = "("
    for condition in conditions:
        result += f' {condition["condition"]} {condition["value"]},'
    return result + ")"

def add_integer_condition_param_to_list(params: dict, param_type: str):
    conditions = ['=', '>', '<']
    verbose_conditions = ['equal to', 'greater than', 'lower than']
    selection = int(input(
f'''
Do you want to filter the cards that have a {param_type}

1. equal to
2. greater than
3. lower than

a certain value?
press 4 to cancel and go back
'''))
    if selection >= 4:
        return "No filter added"
    value = int(input(f"Search for cards with {param_type} {verbose_conditions[selection-1]} "))
    params[param_type].append({"condition": conditions[selection-1], "value": value})
    return f"The filter condition {param_type} {conditions[selection-1]} {value} was addded"

def add_unique_to_array_as_copy(array: list, new_item):
    if new_item not in array:
        copy = array.copy()
        copy.append(new_item)
        return copy
    return array

def query_card_list_with_params(params: dict) -> str:
    with sqlite3.connect('cards.db') as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        query = 'SELECT id, name, type, region, effect, power, madness FROM cards'
        if (params["name"] == "" and params["type"] == [] and params["region"] == [] and params["power"] == [] and params["madness"] == [] and params["effect"] == ""):
            cursor.execute(query + ';')
            table = from_db_cursor(cursor)
            print_card_table(table)
        else:
            query += " WHERE "
            conditions = []
            values = []
            if params["name"] != "":
                conditions.append("lower(name) LIKE ?")
                values.append("%" + params["name"].strip().lower() + "%")
            if params["type"] != []:
                conditions.append("type IN (" + ",".join(["?"]*len(params["type"])) + ")")
                values.extend(params["type"])
            if params["region"] != []:
                conditions.append("region IN (" + ",".join(["?"]*len(params["region"])) + ")")
                values.extend(params["region"])
            if params["power"] != []:
                for condition in params["power"]:
                    conditions.append(f"power {condition['condition']} ?")
                    values.append(condition['value'])
            if params["madness"] != []:
                for condition in params["madness"]:
                    conditions.append(f"madness {condition['condition']} ?")
                    values.append(condition['value'])
            if params["effect"] != "":
                conditions.append("lower(effect) LIKE ?")
                values.append("%" + params["effect"].strip().lower() + "%")
            query += " AND ".join(conditions) + ";"
            cursor.execute(query, tuple(values))
            table = from_db_cursor(cursor)
            print_card_table(table)
            #print(query)
            #print(tuple(values))

def no_op():
    pass

if __name__ == "__main__":
    create_main_menu()
