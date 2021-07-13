import telebot

tb = telebot.TeleBot("1829764543:AAGKI43k7bvar_AdSVHljsCnJ_yGdbihNcQ")
sinon = ['Заявка', 'Оставить Заявку', 'заявка', "вопрос", "оставить вопрос"]

inn = ''
number_phone = ''
program = ''
question = ''
name = ''
cid = '-543818502'



@tb.message_handler(content_types=['text'])
def create_quest(message):
        if message.text.lower() in sinon:
            tb.send_message(message.from_user.id, "Введите ваш ИНН")
            tb.register_next_step_handler(message, get_inn)
        else:
            tb.send_message(message.from_user.id, "Если хотите оставить заявку , напишите ЗАЯВКА")

def get_inn(message):
    global inn
    inn = message.text
    tb.send_message(message.from_user.id, "Введите название программы")
    tb.register_next_step_handler(message, get_prog)

def get_prog(message):
    global program
    program = message.text
    tb.send_message(message.from_user.id, "введите суть вопроса")
    tb.register_next_step_handler(message, get_question)

def get_question(message):
    global question
    question = message.text
    tb.send_message(message.from_user.id, "оставте номер для связи")
    tb.register_next_step_handler(message, get_number)

def get_number(message):
    global number_phone, name
    number_phone = message.text
    name = message.from_user.first_name
    parse = f'''Инн {inn}
Имя {name}
Программа {program}
Вопрос {question}
Номер для связи {number_phone}'''
    tb.send_message(chat_id=cid, text=parse)


tb.polling()