
print("Program started")

from telegram import Update
from telegram.ext import CallbackContext,Updater,CommandHandler,PollAnswerHandler
import config
from fetchsheet import fetch_sheet
from screenshot import shot_page
from threading import Thread
import multiprocessing
import time
import telegram
from tools import atob,strfdelta
import datetime
from QuizManager import QuizManager
import os


print("Importing done")


PORT = int(os.environ.get('PORT', 5000))



updater = Updater(token=config.TOKEN, use_context=True)
dispatcher = updater.dispatcher

print("Updater Invoked")

admins = ["sholmes_O_O","PrabeshAryal"]

def start(update: Update, context: CallbackContext):
	txt = update.message.text
	context.bot.send_message(chat_id=update.effective_chat.id, text="Send /squiz <num> to start quiz")
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)


appState = {}

def authorized(update,context):
	if update.message.from_user.username in admins:
		return True
	context.bot.send_message(chat_id=update.effective_chat.id, text=f"Unauthorized")
	return False
	pass

prefetchState = {}

def prefetch(update,context):
	if not authorized(update,context):
		return 
	sp = update.message.text.split(' ')
	nm = 0
	if len(sp) < 2:
		return
	try:
		nm = int(sp[1])
	except:
		return
	if nm in prefetchState:
		print('Already loaded or loading')
		return
	print('Prefetching ',nm)
	prefetchState[nm] = {'running':True}
	fetch_sheet(nm)
	print('Prefetch completed for  ',nm)
	prefetchState[nm]['running'] = False
	pass


prefetch_handler = CommandHandler('prefetch', prefetch)
dispatcher.add_handler(prefetch_handler)


def squiz(update, context):
	if not authorized(update,context):
		return 
	sp = update.message.text.split(' ')
	nm = 0
	if len(sp) < 2:
		return
	try:
		nm = int(sp[1])
	except:
		return
	# print(nm)
	# print('Authorized')
	chat_id = update.effective_chat.id
	context.bot.send_message(chat_id=chat_id, text=f"Starting {nm}th Quiz Sheet...")
	if chat_id in appState:
		if appState[chat_id].running == True:
			context.bot.send_message(chat_id=chat_id, text=f"Quiz is already begun.")
			return
	qm = QuizManager(update, context, {'sheet_no':nm})
	qm.startQuiz()
	appState[update.effective_chat.id] = qm


def stop(update,context):
	if not authorized(update,context):
		return
	chat_id = update.effective_chat.id
	if chat_id not in appState or appState[chat_id].isRunning() == False:
		context.bot.send_message(chat_id=chat_id,text="There is no Quiz to stop, 🤔")
		return
	appState[chat_id].stopQuiz()
stop_handler = CommandHandler('stop', stop)
dispatcher.add_handler(stop_handler)



def poll_answer_handler(update, context):
	# print(update)
	# print(context.bot_data)
	poll_id = update.poll_answer.poll_id
	try:
		cpoll_inf = context.bot_data[str(poll_id)]
	except Exception as e:
		print('Poll doesnt exist', [poll_id])
		print(e)
		return 
	chat_id = cpoll_inf['chat_id']
	time_stamp = cpoll_inf['timestamp']
	copt = cpoll_inf['correct_option']
	marks = cpoll_inf['marks']
	if chat_id not in appState or appState[chat_id].running == False:
		print('Quiz doesnt exist')
		return
	pollans = update.poll_answer
	user = pollans.user
	corrected = pollans.option_ids[0] == copt
	delta = time.time() - time_stamp
	appState[chat_id].inc_user_timetaken(user,delta)
	if corrected:
		appState[chat_id].inc_user_score(user,marks)
	else:
		appState[chat_id].inc_user_score(user,-marks*0.1)
	pass



squiz_handler = CommandHandler('squiz', squiz)
dispatcher.add_handler(squiz_handler)


dispatcher.add_handler(PollAnswerHandler(poll_answer_handler,pass_chat_data=True, pass_user_data=True))

print('Starting Polling')



production = (PORT != 5000)
print("Production Server" if production else "Development Server")
if production == True:
	mywebserver = "https://mcqquizbot.herokuapp.com/"
	updater.start_webhook(listen="0.0.0.0", port=int(PORT), url_path=config.TOKEN,webhook_url=mywebserver+config.TOKEN)
	updater.idle()
else:
	updater.start_polling()




print('Polling Started')