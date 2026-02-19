import sqlite3
from prettytable import from_db_cursor, TableStyle, HRuleStyle, PrettyTable

DB_FILE_NAME = 'cards.db'
CARD_TYPES = ["creature", "event", "permanent"]

def print_all_decks():
    with sqlite3.connect(DB_FILE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
                       SELECT d.id, d.name, group_concat(distinct c.region) as regions, sum(dc.quantity) as card_count, 
                       CASE WHEN (d.games = 0) THEN 0 ELSE 100 * d.wins / d.games END as win_rate, d.games
                       FROM decks d
                       INNER JOIN deck_cards dc on dc.deck_id = d.id
                       INNER JOIN cards c on c.id = dc.card_id
                       GROUP BY d.id
                       ''')
        table = from_db_cursor(cursor)
        print_deck_table(table)
        
def print_card_table(table: PrettyTable):
    table.set_style(TableStyle.SINGLE_BORDER)
    table._hrules = HRuleStyle.ALL
    table._align = {"id": "r", "name": "l", "type": "l", "region": "l", "effect": "l", "madness": "r", "power": "r"}
    table._max_width = {"effect": 50}
    print(table)
    input("Press Enter to continue\n")

def print_deck_table(table: PrettyTable):
    table.set_style(TableStyle.SINGLE_BORDER)
    table._hrules = HRuleStyle.ALL
    table._align = {"id": "r", "name": "l", "regions": "l", "card_count": "r", "win_rate": "r", "games": "r"}
    table._max_width = {"effect": 50}
    print(table)
    input("Press Enter to continue\n")

def find_deck_id_by_name(deck_name):
    with sqlite3.connect(DB_FILE_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
                       SELECT id FROM decks
                       WHERE d.name = ?
                       ''', (deck_name,))
        return cursor.fetchone()["id"]

CARDS_FROM_DECK_QUERY = '''
    SELECT c.id, dc.quantity, c.name, c.type, c.region, c.effect, c.power, c.madness 
    FROM deck_cards dc 
    INNER JOIN cards c ON c.id = dc.card_id
    WHERE dc.deck_id = ?
'''

def print_deck_cards_by_id(deck_id):
    with sqlite3.connect(DB_FILE_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(CARDS_FROM_DECK_QUERY, (deck_id,))
        table = from_db_cursor(cursor)
    table.del_column("id")
    print_cards_in_deck_table(table)

def get_cards_for_deck_id(deck_id) -> list:
    with sqlite3.connect(DB_FILE_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(CARDS_FROM_DECK_QUERY, (deck_id,))
        return cursor.fetchall()

def print_cards_in_deck_table(table: PrettyTable):
    table.set_style(TableStyle.SINGLE_BORDER)
    table._hrules = HRuleStyle.ALL
    table._align = {"quantity": "r", "name": "l", "type": "l", "region": "l", "effect": "l", "madness": "r", "power": "r"}
    table._max_width = {"effect": 50}
    print(table)
    input("Press Enter to continue\n")

def get_deck_analysis_by_id(deck_id: int):
    with sqlite3.connect(DB_FILE_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
                       SELECT distinct(c.region) as region
                       FROM decks d
                       INNER JOIN deck_cards dc ON dc.deck_id = d.id
                       INNER JOIN cards c ON c.id = dc.card_id
                       WHERE d.id = ?
                       ''', (deck_id,))
        regions_dict = cursor.fetchall()
        regions: list[str] = []
        region_query = ""
        for region_dict in regions_dict:
            regions.append(region_dict["region"])
        for region in regions:
            region_query += f"sum(dc.quantity) FILTER (WHERE c.region = '{region}') as \"{region}\","
        type_query = ""
        for card_type in CARD_TYPES:
            type_query += f"sum(dc.quantity) FILTER (WHERE c.type = '{card_type}') as {card_type},"
        cursor.execute(f'''
                       SELECT d.wins, d.games, d.name,
                       {region_query}
                       {type_query}
                       sum(dc.quantity) as total
                       FROM decks d
                       INNER JOIN deck_cards dc ON dc.deck_id = d.id
                       INNER JOIN cards c ON c.id = dc.card_id
                       WHERE d.id = ?
                       GROUP BY d.id;
                       ''', (deck_id,))
        return {"stats": cursor.fetchone(),
                "regions": regions}

def delete_deck_by_id(deck_id):
    with sqlite3.connect(DB_FILE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
                       DELETE FROM deck_cards
                       WHERE deck_id = ?
                       ''', (deck_id,))
        cursor.execute('''
                       DELETE FROM decks
                       WHERE id = ?
                       ''', (deck_id,))
        conn.commit()

def register_win_for_deck(deck_id):
    with sqlite3.connect(DB_FILE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE decks SET wins = wins+1, games = games+1 WHERE id = ?", (deck_id,))
        conn.commit()

def register_loss_for_deck(deck_id):
    with sqlite3.connect(DB_FILE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE decks SET games = games+1 WHERE id = ?", (deck_id,))
        conn.commit()