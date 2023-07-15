import sqlite3 as sq


def sql_start():
    global base, cur
    base = sq.connect('shop.db')
    cur = base.cursor()


async def change_vis(cat):
    cur.execute("UPDATE categories SET visibility =? WHERE name =?", (not (cur.execute("SELECT visibility FROM categories WHERE name =?", (cat,)).fetchone()[0]), cat))
    base.commit()


async def get_category_by_name(name):
    results = cur.execute('SELECT cat FROM items WHERE name ==?', (name,)).fetchone()[0]
    return results


async def get_nicotine_prices_1000():
    cur.execute('SELECT volume, price FROM nicotine_1000')
    results = cur.fetchall()
    return results
async def get_nicotine_prices_500():
    cur.execute('SELECT volume, price FROM nicotine_500')
    results = cur.fetchall()
    return results
async def get_nicotine_prices_100():
    cur.execute('SELECT volume, price FROM nicotine_100')
    results = cur.fetchall()
    return results


async def get_stat_items():
    arr = ""
    all = cur.execute("SELECT * FROM items").fetchall()

    for i in range(len(all)):
        arr += f"""{all[i][2]} | Остаток: {all[i][6]}\n"""

    return arr


async def get_stats():
    return int(cur.execute("SELECT * FROM stats").fetchall()[0][0])


async def minus_count(name):
    count = cur.execute("SELECT count FROM items WHERE name == ?", (name,)).fetchall()[0][0]
    count = int(count) - 1
    cur.execute("UPDATE items SET count = ? WHERE name == ?", (count, name))
    base.commit()


async def add_new_item(id, cat, name, price, descr, ratio, count, V):
    cur.execute("INSERT INTO items VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (id, cat, name, price, descr, ratio, count, V,))
    base.commit()


async def edit_item_count(name, count):
    cur.execute("UPDATE items SET count = ? WHERE name == ?", (count, name))
    base.commit()


async def del_item(name):
    cur.execute("DELETE FROM items WHERE name == ?", (name,))
    base.commit()


async def get_ratio(name):
    return cur.execute("SELECT * FROM items WHERE name == ?", (name,)).fetchall()[0][5]


async def get_v(name):
    return cur.execute("SELECT * FROM items WHERE name == ?", (name,)).fetchall()[0][7]


async def del_order(user_id):
    cur.execute("DELETE FROM orders WHERE user_id == ?", (user_id,))
    cur.execute("UPDATE stats SET all_orders = ? WHERE all_orders == ?", ((int(cur.execute("SELECT * FROM stats").fetchall()[0][0]) + 1), (int(cur.execute("SELECT * FROM stats").fetchall()[0][0]))))
    base.commit()


async def get_one_price(name):
    return int(cur.execute("SELECT price FROM items WHERE name == ?", (name,)).fetchall()[0][0])
    

async def get_one_price_1(name):
    return int(cur.execute("SELECT price FROM orders WHERE items == ?", (name,)).fetchone()[0])


async def get_for_basket(user_id):
    return cur.execute("SELECT items FROM orders WHERE user_id == ?", (user_id,)).fetchall()


async def get_total_price(user_id):
    all_data = cur.execute("SELECT price FROM orders WHERE user_id == ?", (user_id,)).fetchall()
    arr = []
    counter = 0

    for i in range(len(all_data)):
        arr.append(str(all_data[i][0]))
        
    for i in arr:
        counter += int(i)

    return counter


async def add_to_order(user_id, items, price):
    cur.execute('INSERT INTO orders VALUES(?, ?, ?)', (user_id, items, price,))
    base.commit()


async def get_item(name):
    return cur.execute("SELECT * FROM items WHERE name == ?", (name,)).fetchall()[0]


async def get_all_items(cat):
    return cur.execute("SELECT * FROM items WHERE cat == ? AND count!= 0", (cat,)).fetchall()


async def add_cat(name):
    cur.execute("INSERT INTO categories VALUES (?)", (name,))
    base.commit()


async def delete_cat(name):
    cur.execute("DELETE FROM categories WHERE name == ?", (name,))
    base.commit()


async def get_all_cat():
    return cur.execute("SELECT * FROM categories").fetchall()
