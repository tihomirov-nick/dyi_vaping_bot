from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from create_bot import bot
from database import db

admin_kb = InlineKeyboardMarkup() \
    .add(InlineKeyboardButton(text="Работа с категориями", callback_data="Работа с категориями")) \
    .add(InlineKeyboardButton(text="Работа с товарами", callback_data="Работа с товарами")) \
    .add(InlineKeyboardButton(text="Статистика", callback_data="Статистика"))

admin_back = InlineKeyboardMarkup() \
    .add(InlineKeyboardButton(text="Главное меню администратора", callback_data="Главное меню администратора"))


async def start_admin(message: types.Message, state: FSMContext):
    await state.finish()
    if str(message.from_user.id) in "252172200 5440191358":
        await bot.send_message(message.from_user.id, text="Добро пожаловать в панель администратора",
                               reply_markup=admin_kb)


async def call_start_admin(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.edit_text(text="Добро пожаловать в панель администратора",
                                 reply_markup=admin_kb)


# Статистика


async def view_stat(call: types.CallbackQuery):
    text = "Статистика\n\n"
    orders = await db.get_stats()

    text += f"Кол-во заказов: {orders}\n\n{await db.get_stat_items()}"

    await call.message.edit_text(text=text, reply_markup=admin_kb)


# Работа с категориями


class AddNewCat(StatesGroup):
    name = State()


async def edit_cat_1(call: types.CallbackQuery):
    await call.message.edit_text(text="Выберите действие", reply_markup=InlineKeyboardMarkup().add(
        InlineKeyboardButton(text="Создать категорию", callback_data="Создать категорию")).add(
        InlineKeyboardButton(text="Удалить категорию", callback_data="Удалить категорию")).add(
        InlineKeyboardButton(text="Изменить видимость категории", callback_data="Изменить видимость категории")).add(
        InlineKeyboardButton(text="Главное меню", callback_data="/admin")
    ))


async def change_visibility(call: types.CallbackQuery):
    all_cat = await db.get_all_cat()
    cat_kb = InlineKeyboardMarkup()

    for cat in range(len(all_cat)):
        cat_kb.add(InlineKeyboardButton(text=f"{all_cat[cat][0]} - {all_cat[cat][1]}", callback_data="change_vis_cat" + all_cat[cat][0]))

    cat_kb.add(InlineKeyboardButton(text="Главное меню администратора", callback_data="Главное меню администратора"))

    await call.message.edit_text("Выберите категорию для изменения видимости", reply_markup=cat_kb)


async def change_visibility_1(call: types.CallbackQuery):
    cat = call.data.replace("change_vis_cat", "")
    await db.change_vis(cat)
    await call.message.edit_text(text=f'''Категория "{cat}" была успешно удалена''', reply_markup=admin_kb)


async def edit_cat_2(call: types.CallbackQuery):
    all_cat = await db.get_all_cat()
    cat_kb = InlineKeyboardMarkup()

    for cat in range(len(all_cat)):
        cat_kb.add(InlineKeyboardButton(text=all_cat[cat][0], callback_data="del_cat" + all_cat[cat][0]))

    cat_kb.add(InlineKeyboardButton(text="Главное меню администратора", callback_data="Главное меню администратора"))

    await call.message.edit_text("Выберите категорию для удаления", reply_markup=cat_kb)


async def edit_cat_3(call: types.CallbackQuery):
    cat = call.data.replace("del_cat", "")
    await db.delete_cat(cat)
    await call.message.edit_text(text=f'''Категория "{cat}" была успешно удалена''', reply_markup=admin_kb)


async def edit_cat_4(call: types.CallbackQuery):
    await call.message.edit_text(text="Введите название новой категории", reply_markup=admin_back)
    await AddNewCat.name.set()


async def edit_cat_5(mess: types.Message, state: FSMContext):
    name = mess.text
    await db.add_cat(name)
    await bot.send_message(mess.from_user.id, text="Категория" + f'''" {name} "''' + "успешно добавлена",
                           reply_markup=admin_kb)
    await state.finish()


# Работа с товаром


async def item_menu(call: types.CallbackQuery):
    menu = InlineKeyboardMarkup() \
        .add(InlineKeyboardButton(text="Добавить товар", callback_data="Добавить товар")) \
        .add(InlineKeyboardButton(text="Удалить товар", callback_data="Удалить товар")) \
        .add(InlineKeyboardButton(text="Изменить товар", callback_data="Изменить товар")) \
        .add(InlineKeyboardButton(text="Главное меню", callback_data="/admin"))

    await call.message.edit_text(text="Меню работы с товарами", reply_markup=menu)


# Добавление товара


class AddNewItem(StatesGroup):
    cat = State()
    name = State()
    price = State()
    desc = State()
    ratio = State()
    visibility = State()
    photo = State()


async def add_new_item_1(call: types.CallbackQuery):
    all_cat = await db.get_all_cat()
    cat_kb = InlineKeyboardMarkup()

    for cat in range(len(all_cat)):
        cat_kb.add(InlineKeyboardButton(text=all_cat[cat][0],
                                        callback_data="WIE" + all_cat[cat][0]))

    cat_kb.add(InlineKeyboardButton(text="Главное меню", callback_data="/admin"))

    await call.message.edit_text(text="Выберите категорию товара", reply_markup=cat_kb)
    await AddNewItem.cat.set()


async def add_new_item_2(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['cat'] = call.data.replace("WIE", "")

    await call.message.edit_text(text="Введите наименование нового товара",
                                 reply_markup=InlineKeyboardMarkup()
                                 .add(InlineKeyboardButton(text="Главное меню", callback_data="/admin")))
    await AddNewItem.name.set()


async def add_new_item_3(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text

    await bot.send_message(message.from_user.id, text="Введите цену нового товара",
                           reply_markup=InlineKeyboardMarkup()
                           .add(InlineKeyboardButton(text="Главное меню", callback_data="/admin")))
    await AddNewItem.price.set()


async def add_new_item_4(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['price'] = message.text

    await bot.send_message(message.from_user.id, text="Введите описание нового товара",
                           reply_markup=InlineKeyboardMarkup()
                           .add(InlineKeyboardButton(text="Главное меню", callback_data="/admin")))
    await AddNewItem.desc.set()


async def add_new_item_5(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['desc'] = message.text

    await bot.send_message(message.from_user.id, text="Введите описание соотношения нового товара\n\nПример ввода:\n\n50/50 60/40\n\n\nЕсли у товара нет соотношений отправьте 0",
                           reply_markup=InlineKeyboardMarkup()
                           .add(InlineKeyboardButton(text="Главное меню", callback_data="/admin")))
    await AddNewItem.ratio.set()


async def add_new_item_6(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['ratio'] = message.text

    await bot.send_message(message.from_user.id, text="Отправьте кол-во товара",
                           reply_markup=InlineKeyboardMarkup()
                           .add(InlineKeyboardButton(text="Главное меню", callback_data="/admin")))
    await AddNewItem.visibility.set()


async def add_new_item_7(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['visibility'] = message.text

    await bot.send_message(message.from_user.id, text="Отправьте фото товара",
                           reply_markup=InlineKeyboardMarkup()
                           .add(InlineKeyboardButton(text="Отправить без фото", callback_data="NOPHOTO"))
                           .add(InlineKeyboardButton(text="Главное меню", callback_data="/admin")))
    await AddNewItem.photo.set()


async def add_new_item_8(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['photo'] = message.photo[0].file_id

        if data['cat'] == "Расходники":
            V = "0"
        elif data['cat'] == "PG/VG, никотин, основы":
            V = "0"
        elif data['cat'] == "DIY Жидкости":
            V = "30/60/100"
        elif data['cat'] == "DIY Жидкости SALT":
            V = "30/60"
        elif data['cat'] == "Пропиленгликоль":
            V = "0"
        else:
            V = data['ratio']

        await db.add_new_item(data['photo'], data['cat'], data['name'], data['price'], data['desc'], data['ratio'], data['visibility'], V=V)

    await bot.send_message(message.from_user.id, text="Товар успешно добавлен",
                           reply_markup=InlineKeyboardMarkup()
                           .add(InlineKeyboardButton(text="Главное меню", callback_data="/admin")))
    await state.finish()


async def no_photo(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['photo'] = None

        if data['cat'] == "Расходники":
            V = "0"
        elif data['cat'] == "PG/VG, никотин, основы":
            V = "0"
        elif data['cat'] == "DIY Жидкости":
            V = "30/60/100"
        elif data['cat'] == "DIY Жидкости SALT":
            V = "30/60"
        elif data['cat'] == "Пропиленгликоль":
            V = "0"
        else:
            V = data['ratio']

        await db.add_new_item(data['photo'], data['cat'], data['name'], data['price'], data['desc'], data['ratio'], data['visibility'], V)

    await call.message.edit_text(text="Товар успешно добавлен",
                                 reply_markup=InlineKeyboardMarkup()
                                 .add(InlineKeyboardButton(text="Главное меню", callback_data="/admin")))
    await state.finish()


# Удаление товара


class DelItem(StatesGroup):
    cat = State()
    name = State()


async def del_item_1(call: types.CallbackQuery):
    all_cat = await db.get_all_cat()
    cat_kb = InlineKeyboardMarkup()

    for cat in range(len(all_cat)):
        cat_kb.add(InlineKeyboardButton(text=all_cat[cat][0],
                                        callback_data="DEC" + all_cat[cat][0]))

    cat_kb.add(InlineKeyboardButton(text="Главное меню", callback_data="/admin"))

    await call.message.edit_text(text="Выберите категорию товара", reply_markup=cat_kb)
    await DelItem.cat.set()


async def del_item_2(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['cat'] = call.data.replace("DEC", "")

        all_items = await db.get_all_items(data['cat'])
        items_kb = InlineKeyboardMarkup()

        for i in range(len(all_items)):
            items_kb.add(InlineKeyboardButton(text=all_items[i][2], callback_data="#" + all_items[i][2]))

        await call.message.edit_text(text="Выберите товар для удаления", reply_markup=items_kb)
    await DelItem.name.set()


async def del_item_3(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = call.data.replace("#", "")

        await db.del_item(data['name'])

        await call.message.edit_text(text=f'''Товар "{data['name']} успешно удален"''',
                                     reply_markup=InlineKeyboardMarkup()
                                     .add(InlineKeyboardButton(text="Главное меню", callback_data="/admin")))
    await state.finish()


# Редактирование товара


class EditItem(StatesGroup):
    cat = State()
    name = State()
    count = State()


async def edit_item_1(call: types.CallbackQuery):
    all_cat = await db.get_all_cat()
    cat_kb = InlineKeyboardMarkup()

    for cat in range(len(all_cat)):
        cat_kb.add(InlineKeyboardButton(text=all_cat[cat][0],
                                        callback_data="ED" + all_cat[cat][0]))

    cat_kb.add(InlineKeyboardButton(text="Главное меню", callback_data="/admin"))

    await call.message.edit_text(text="Выберите категорию товара", reply_markup=cat_kb)
    await EditItem.cat.set()


async def edit_item_2(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['cat'] = call.data.replace("ED", "")

        all_items = await db.get_all_items(data['cat'])
        items_kb = InlineKeyboardMarkup()

        for i in range(len(all_items)):
            items_kb.add(InlineKeyboardButton(text=all_items[i][2], callback_data="$" + all_items[i][2]))

        await call.message.edit_text(text="Выберите товар для редактирования", reply_markup=items_kb)
    await EditItem.name.set()


async def edit_item_3(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = call.data.replace("$", "")

        await call.message.edit_text("Введите кол-во товара",
                                     reply_markup=InlineKeyboardMarkup()
                                     .add(InlineKeyboardButton(text="Главное меню", callback_data="/admin")))
    await EditItem.count.set()


async def edit_item_4(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['count'] = message.text
        await db.edit_item_count(data['name'], data['count'])
        await bot.send_message(message.from_user.id, text="Изменения успешно внесены",
                               reply_markup=InlineKeyboardMarkup()
                               .add(InlineKeyboardButton(text="Главное меню", callback_data="/admin")))
    await state.finish()


def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(start_admin, commands=['admin'], state='*')
    dp.register_callback_query_handler(call_start_admin, lambda c: c.data == "/admin", state='*')
    dp.register_callback_query_handler(view_stat, lambda c: c.data == "Статистика")

    dp.register_callback_query_handler(edit_item_1, lambda c: c.data == "Изменить товар")
    dp.register_callback_query_handler(edit_item_2, lambda c: c.data and c.data.startswith("ED"), state=EditItem.cat)
    dp.register_callback_query_handler(edit_item_3, lambda c: c.data and c.data.startswith("$"), state=EditItem.name)
    dp.register_message_handler(edit_item_4, state=EditItem.count)

    dp.register_callback_query_handler(del_item_1, lambda c: c.data == "Удалить товар")
    dp.register_callback_query_handler(del_item_2, lambda c: c.data and c.data.startswith("DEC"), state=DelItem.cat)
    dp.register_callback_query_handler(del_item_3, lambda c: c.data and c.data.startswith("#"), state=DelItem.name)

    dp.register_callback_query_handler(add_new_item_1, lambda c: c.data == "Добавить товар")
    dp.register_callback_query_handler(add_new_item_2, lambda c: c.data and c.data.startswith("WIE"), state=AddNewItem.cat)
    dp.register_message_handler(add_new_item_3, state=AddNewItem.name)
    dp.register_message_handler(add_new_item_4, state=AddNewItem.price)
    dp.register_message_handler(add_new_item_5, state=AddNewItem.desc)
    dp.register_message_handler(add_new_item_6, state=AddNewItem.ratio)
    dp.register_message_handler(add_new_item_7, state=AddNewItem.visibility)
    dp.register_message_handler(add_new_item_8, content_types=['photo'], state=AddNewItem.photo)
    dp.register_callback_query_handler(no_photo, lambda c: c.data == "NOPHOTO", state=AddNewItem.photo)

    dp.register_callback_query_handler(edit_cat_1, lambda c: c.data == "Работа с категориями")
    dp.register_callback_query_handler(edit_cat_2, lambda c: c.data == "Удалить категорию")
    dp.register_callback_query_handler(edit_cat_3, lambda c: c.data and c.data.startswith("del_cat"))
    dp.register_callback_query_handler(edit_cat_4, lambda c: c.data == "Создать категорию")
    dp.register_message_handler(edit_cat_5, state=AddNewCat.name)

    dp.register_callback_query_handler(item_menu, lambda c: c.data == "Работа с товарами")


    dp.register_callback_query_handler(change_visibility, lambda c: c.data == "Изменить видимость категории")
    dp.register_callback_query_handler(change_visibility_1, lambda c: c.data and c.data.startswith("change_vis_cat"))