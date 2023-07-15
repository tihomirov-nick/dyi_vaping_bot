from traceback import print_tb
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from create_bot import bot
from database import db


class BuyItem(StatesGroup):
    name = State()


async def start_client(message: types.Message, state: FSMContext):
    await state.finish()
    client_kb = InlineKeyboardMarkup().add(InlineKeyboardButton(text="Категории", callback_data="Категории")).add(
        InlineKeyboardButton(text=f"Корзина ({await db.get_total_price(message.from_user.id)} руб.)",
                             callback_data="Корзина"))
    await bot.send_message(message.from_user.id, text="Добро пожаловать!",
                           reply_markup=client_kb)


async def start_client_cal(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    client_kb = InlineKeyboardMarkup().add(InlineKeyboardButton(text="Категории", callback_data="Категории")).add(
        InlineKeyboardButton(text=f"Корзина ({await db.get_total_price(call.from_user.id)} руб.)",
                             callback_data="Корзина"))
    await call.message.edit_text(text="Добро пожаловать!",
                                 reply_markup=client_kb)


async def categories(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    all_cat = await db.get_all_cat()
    cat_kb = InlineKeyboardMarkup()

    for cat in range(len(all_cat)):
        if all_cat[cat][1]:
            cat_kb.add(InlineKeyboardButton(text=all_cat[cat][0] + f" ({len(await db.get_all_items(all_cat[cat][0]))})",
                                        callback_data="view" + all_cat[cat][0]))

    cat_kb.add(InlineKeyboardButton(
        text="Главное меню", callback_data="start"))

    try:
        await call.message.edit_text(text="Категории", reply_markup=cat_kb)
    except:
        await call.message.delete()
        await bot.send_message(call.message.chat.id, text="Категории", reply_markup=cat_kb)


async def items(call: types.CallbackQuery):
    cat = call.data.replace("view", "")
    items_kb = InlineKeyboardMarkup()
    all_items = await db.get_all_items(cat)

    for i in range(len(all_items)):
        if int(all_items[i][6]) > 0:
            items_kb.row(InlineKeyboardButton(text=str(all_items[i][2]), callback_data="info" + str(all_items[i][2])),
                         InlineKeyboardButton(text=str(all_items[i][3]) + " руб.",
                                              callback_data="info" + str(all_items[i][2])))

    items_kb.add(InlineKeyboardButton(
        text='Вернуться в "Категории"', callback_data="Категории"))

    await call.message.edit_text(text=f'''Товары категории "{cat}"''', reply_markup=items_kb)


class AddToBuy(StatesGroup):
    name = State()
    V = State()
    ratio = State()
    nekotin = State()


async def view_item(call: types.CallbackQuery):
    item = call.data.replace("info", "")
    data = await db.get_item(item)

    if data[0] is None:
        await call.message.edit_text(
            text=f'''Название: {item}\n\nОписание: {data[4]}\n\nВ наличии: {data[6]} шт.\n\nСтоимость: {data[3]} руб.''',
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton(text="В корзину", callback_data=f"add{item}")).add(
                InlineKeyboardButton(text='Вернуться в "Категории"', callback_data="Категории")))
    else:
        await call.message.delete()
        await bot.send_photo(call.message.chat.id, photo=data[0],
                             caption=f'''Название: {item}\n\nОписание: {data[4]}\n\nВ наличии: {data[6]} шт.\n\nСтоимость: {data[3]} руб.''',
                             reply_markup=InlineKeyboardMarkup().add(
                                 InlineKeyboardButton(text="В корзину", callback_data=f"add{item}")).add(
                                 InlineKeyboardButton(text='Вернуться в "Категории"', callback_data="Категории")))
    await AddToBuy.name.set()


async def add_1(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = call.data.replace("add", "")
        if (await db.get_ratio(data['name']) is None or await db.get_ratio(data['name']) == "0") and (
                await db.get_v(data['name']) is None or await db.get_v(data['name']) == "0"):
            send = f"""Товар: {data['name']}\n"""
            await db.add_to_order(call.from_user.id, send, await db.get_one_price(data['name']))
            await call.message.delete()
            await db.minus_count(data['name'])
            await bot.send_message(call.message.chat.id, text=f'''Товар "{data['name']}" добавлен в корзину''',
                                   reply_markup=InlineKeyboardMarkup().add(
                                       InlineKeyboardButton(text="Категории", callback_data="Категории")).add(
                                       InlineKeyboardButton(
                                           text=f"Корзина ({await db.get_total_price(call.from_user.id)} руб.)",
                                           callback_data="Корзина")))
            await state.finish()

        else:
            if "Основа" in str(data['name']):
                await call.message.delete()
                await db.minus_count(data['name'])
                await bot.send_message(call.message.chat.id, text=f'''Выбрано "{data['name']}"''',
                                       reply_markup=InlineKeyboardMarkup().add(
                                           InlineKeyboardButton(text="Продолжить",
                                                                callback_data=f"custom{data['name'].replace('Основа, ', '')}")))
                await AddToBuy.V.set()
            else:
                await call.message.delete()
                await db.minus_count(data['name'])

                kb = InlineKeyboardMarkup()
                all_v = str(await db.get_v(data['name'])).split("/")

                for i in range(len(all_v)):
                    kb.add(InlineKeyboardButton(
                        text=f"{all_v[i]} мл.", callback_data=all_v[i]))

                await bot.send_message(call.message.chat.id, text="Выберите объем",
                                       reply_markup=kb)
                await AddToBuy.V.set()


async def add_2(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['V'] = call.data.replace("custom", "").replace("мл", "")
        try:
            ratio = await db.get_ratio(data['name'])
            ratio = ratio.split("\n")

            kb = InlineKeyboardMarkup()

            for i in range(len(ratio)):
                try:
                    kb.add(InlineKeyboardButton(text=ratio[i], callback_data=str(ratio[i]).replace("\r")))
                except:
                    kb.add(InlineKeyboardButton(text=ratio[i], callback_data=ratio[i]))

            await call.message.edit_text(text="Выберите соотношение", reply_markup=kb)

        except:
            send = ""
            send = f"""Товар: {data['name']}\n"""
            send += f"""Объем: {data['V']}\n"""

            price = await db.get_one_price(data['name'])

            if str(data['V']) in "30/60/100":
                if data['V'] == "30":
                    price = 230
                elif data['V'] == "60":
                    price = 400
                elif data['V'] == "100":
                    price = 500

            if data['name'] == "Пищевой глицерин USP":
                if data['V'] == "100":
                    price = 175
                elif data['V'] == "500":
                    price = 600
                elif data['V'] == "1000":
                    price = 1100

            elif data['name'] == "Пищевой пропиленгликоль USP":
                if data['V'] == "100":
                    price = 200
                elif data['V'] == "500":
                    price = 800
                elif data['V'] == "1000":
                    price = 1500

            elif data['name'] == "Сотка Chemnovatic":
                if data['V'] == "10":
                    price = 120
                elif data['V'] == "50":
                    price = 450

            await state.finish()
            await db.add_to_order(call.message.chat.id, send, price)
            await call.message.edit_text(text=f'''Товар "{data['name']}" добавлен в корзину''',
                                         reply_markup=InlineKeyboardMarkup().add(
                                             InlineKeyboardButton(text="Категории", callback_data="Категории")).add(
                                             InlineKeyboardButton(
                                                 text=f"Корзина ({await db.get_total_price(call.message.chat.id)} руб.)",
                                                 callback_data="Корзина")))

    await AddToBuy.ratio.set()


async def add_3(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['ratio'] = call.data
        if "Основа" in str(data['name']):
            osn_kb = InlineKeyboardMarkup()
            if data['name'] == "Основа, 1000мл":
                buttons = await db.get_nicotine_prices_1000()
            elif data['name'] == "Основа, 500мл":
                buttons = await db.get_nicotine_prices_500()
            elif data['name'] == "Основа, 100мл":
                buttons = await db.get_nicotine_prices_100()
            for button in buttons:
                osn_kb.add(InlineKeyboardButton(text=f"{button[0]} мг/мл (+{button[1]}.00 руб.)", callback_data=f"osn_volume{button[0]}-{button[1]}"))
            await call.message.edit_text(text="Выберите кол-во никотина", reply_markup=osn_kb)
        elif "SALT" in await db.get_category_by_name(data['name']):
            await call.message.edit_text(text="Введите кол-во никотина\n\n1-20мг = 350p, 21-50мг = 450p")
        else:
            await call.message.edit_text(text="Введите кол-во никотина\n\n100мл\n1мг = 4р\n\n60мл\n1мг = 2.8р\n\n30мл\n1мг = 1.5р")
    await AddToBuy.nekotin.set()


async def add_4_osn(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['nekotin'] = str(call.data).split("-")[0].replace("osn_volume", "")
        price = await db.get_one_price(data['name']) + int(str(call.data).split("-")[1])

        send = f"""Товар: {data['name']}\n"""
        send += f"""Объем: {data['V']}\n"""
        send += f"""Соотношение: {data['ratio']}\n"""
        send += f"""Кол-во никотина: {data['nekotin']}"""

    await state.finish()
    await db.add_to_order(call.from_user.id, send, price)
    await call.message.edit_text(text=f'''Товар "{data['name']}" добавлен в корзину''',
                           reply_markup=InlineKeyboardMarkup().add(
                               InlineKeyboardButton(text="Категории", callback_data="Категории")).add(
                               InlineKeyboardButton(
                                   text=f"Корзина ({await db.get_total_price(call.from_user.id)} руб.)",
                                   callback_data="Корзина")))


async def add_4(mess: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['nekotin'] = mess.text

        send = f"""Товар: {data['name']}\n"""
        send += f"""Объем: {data['V']}\n"""
        send += f"""Соотношение: {data['ratio']}\n"""
        send += f"""Кол-во никотина: {data['nekotin']}"""

        price = await db.get_one_price(data['name'])
    
    if await db.get_category_by_name(data['name']) != "DIY Жидкости SALT":
        price_dict = {"30": 230, "60": 400, "100": 500}
        if data['V'] in price_dict:
            price = price_dict[data['V']]

        if data['name'] == "Пищевой глицерин USP":
            if data['V'] == "100":
                price = 175
            elif data['V'] == "500":
                price = 600
            elif data['V'] == "1000":
                price = 1100

        elif data['name'] == "Пищевой пропиленгликоль USP":
            if data['V'] == "100":
                price = 200
            elif data['V'] == "500":
                price = 800
            elif data['V'] == "1000":
                price = 1500

        elif data['name'] == "Сотка Chemnovatic":
            if data['V'] == "10":
                price = 120
            elif data['V'] == "50":
                price = 450

    if await db.get_category_by_name(data['name']) == "DIY Жидкости SALT":
        if int(data['nekotin']) > 0 and int(data['nekotin']) < 21:
            price += 350
            await db.add_to_order(mess.from_user.id, send, price)
            await bot.send_message(mess.from_user.id, text=f'''Товар "{data['name']}" добавлен в корзину''',
                                reply_markup=InlineKeyboardMarkup().add(
                                    InlineKeyboardButton(text="Категории", callback_data="Категории")).add(
                                    InlineKeyboardButton(
                                        text=f"Корзина ({await db.get_total_price(mess.from_user.id)} руб.)",
                                        callback_data="Корзина")))
            await state.finish()
        elif int(data['nekotin']) > 20 and int(data['nekotin']) < 50:
            price += 450
            await db.add_to_order(mess.from_user.id, send, price)
            await bot.send_message(mess.from_user.id, text=f'''Товар "{data['name']}" добавлен в корзину''',
                                reply_markup=InlineKeyboardMarkup().add(
                                    InlineKeyboardButton(text="Категории", callback_data="Категории")).add(
                                    InlineKeyboardButton(
                                        text=f"Корзина ({await db.get_total_price(mess.from_user.id)} руб.)",
                                        callback_data="Корзина")))
            await state.finish()
        else:
            await AddToBuy.nekotin.set()
            await mess.answer("Вы вышли за установленные рамки, повторите ввод\n\n1-20мг = 350p, 21-50мг = 450p")
    elif await db.get_category_by_name(data['name']) == "DIY Жидкости":
        if str(data['V']) == "100":
            price += int(data['nekotin']) * 4
        elif str(data['V']) == "60":
            price += int(data['nekotin']) * 3
        elif str(data['V']) == "30":
            price += int(data['nekotin']) * 2

        await db.add_to_order(mess.from_user.id, send, price)
        await bot.send_message(mess.from_user.id, text=f'''Товар "{data['name']}" добавлен в корзину''',
                            reply_markup=InlineKeyboardMarkup().add(
                                InlineKeyboardButton(text="Категории", callback_data="Категории")).add(
                                InlineKeyboardButton(
                                    text=f"Корзина ({await db.get_total_price(mess.from_user.id)} руб.)",
                                    callback_data="Корзина")))
        await state.finish()
    else:
        await db.add_to_order(mess.from_user.id, send, price)
        await bot.send_message(mess.from_user.id, text=f'''Товар "{data['name']}" добавлен в корзину''',
                            reply_markup=InlineKeyboardMarkup().add(
                                InlineKeyboardButton(text="Категории", callback_data="Категории")).add(
                                InlineKeyboardButton(
                                    text=f"Корзина ({await db.get_total_price(mess.from_user.id)} руб.)",
                                    callback_data="Корзина")))
        await state.finish()


async def basket(call: types.CallbackQuery):
    data = await db.get_for_basket(call.from_user.id)
    kb = InlineKeyboardMarkup()
    if data != []:
        text = "Ваш заказ:\n\n"

        for i in data:
            try:
                prev_text = str(i[0]).split("\n")[0] + "\n" + (str(i[0]).split("\n")[1] + " мл.\n") + str(i[0]).split("\n")[2] + "\n" + str(i[0]).split("\n")[3]
                text += prev_text + "\n" + f"""Цена: {await (db.get_one_price_1(i[0]))} руб.\n\n"""
            except:
                prev_text = str(i[0]).split("\n")[0]
                text += prev_text + f"""\nЦена: {await (db.get_one_price_1(i[0]))} руб.\n\n"""

        kb.add(InlineKeyboardButton(
            text="Оформить заказ", callback_data="Оформить заказ"))
        kb.add(InlineKeyboardButton(text="Категории", callback_data="Категории"))
        await call.message.edit_text(text=text, reply_markup=kb)

    else:
        kb.add(InlineKeyboardButton(text="Категории", callback_data="Категории"))
        await call.message.edit_text(text="В корзине ничего нет", reply_markup=kb)


class EndOrder(StatesGroup):
    fio = State()
    number = State()
    adr = State()


async def end_order_1(call: types.CallbackQuery):
    await call.message.edit_text(text="Введите Ваши ФИО")
    await EndOrder.fio.set()


async def end_order_2(mess: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['fio'] = mess.text
    await bot.send_message(mess.from_user.id, text="Введите Ваш контактный номер телефона")
    await EndOrder.number.set()


async def end_order_3(mess: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['number'] = mess.text
    await bot.send_message(mess.from_user.id, text="Введите удобный вам адрес офиса СДЭК")
    await EndOrder.adr.set()


async def end_order_4(mess: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['adr'] = mess.text

        datas = await db.get_for_basket(mess.from_user.id)
        arr = []

        for i in range(len(datas)):
            arr.append(str(datas[i][0]).split("\n"))

        text = ""

        for i in range(len(arr)):
            try:
                text += f"""{arr[i][0]}
{arr[i][1]} мл.
{arr[i][2]}
{arr[i][3]}
Цена: {await db.get_one_price_1(datas[i][0])} руб.\n\n"""
            except:
                text += f"""{arr[i][0]}
Цена: {await db.get_one_price_1(datas[i][0])} руб.\n\n"""

        await db.del_order(mess.from_user.id)

        await bot.send_message(mess.from_user.id, text="Заказ успешно оформлен, скоро с Вами свяжутся!",
                               reply_markup=InlineKeyboardMarkup().add(
                                   InlineKeyboardButton(text="Категории", callback_data="Категории")).add(
                                   InlineKeyboardButton(
                                       text=f"Корзина ({await db.get_total_price(mess.from_user.id)} руб.)",
                                       callback_data="Корзина")))
        await bot.send_message(-1001645778485,
                               text=f"Заказ на имя: {data['fio']}\nКонтактный номер: {data['number']}\nАдрес СДЭК: {data['adr']}\nИмя пользователя: {mess.from_user.username}\n\n" + text)
        await state.finish()


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(start_client, commands=['start'], state='*')
    dp.register_callback_query_handler(
        start_client_cal, lambda c: c.data == "start")

    dp.register_callback_query_handler(
        categories, lambda c: c.data == "Категории", state='*')
    dp.register_callback_query_handler(
        items, lambda c: c.data and c.data.startswith("view"))

    dp.register_callback_query_handler(basket, lambda c: c.data == "Корзина")
    dp.register_callback_query_handler(
        end_order_1, lambda c: c.data == "Оформить заказ")
    dp.register_message_handler(end_order_2, state=EndOrder.fio)
    dp.register_message_handler(end_order_3, state=EndOrder.number)
    dp.register_message_handler(end_order_4, state=EndOrder.adr)

    dp.register_callback_query_handler(
        view_item, lambda c: c.data and c.data.startswith("info"))

    dp.register_callback_query_handler(
        add_1, lambda c: c.data and c.data.startswith("add"), state=AddToBuy.name)
    dp.register_callback_query_handler(add_2, lambda
        c: c.data == "10" or c.data == "30" or c.data == "50" or c.data == "60" or c.data == "100" or c.data == "500" or c.data == "1000" or (
                c.data and c.data.startswith("custom")),
                                       state=AddToBuy.V)
    dp.register_callback_query_handler(add_3, lambda c: str(c.data) in "50/50\r 60/40\r 70/30\r 80/20\r 90/10",
                                       state=AddToBuy.ratio)
    dp.register_message_handler(add_4, state=AddToBuy.nekotin)
    dp.register_callback_query_handler(add_4_osn, lambda c: c.data and c.data.startswith("osn_volume"), state=AddToBuy.nekotin)
