

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
from threading import Timer



class QuizManager:
	def __init__(self,update,context,opt):
		self.update = update
		self.context = context
		self.sh_num = opt['sheet_no']
		self.chat_id = update.effective_chat.id
		self.scoreinfo = {"uscores":{},"tscore":0}
		self.running = False
		self.ltimer = None
		self.lastpoll = None
		self.timed_explaination = None
		self.pollsInfo = {}
		self.question_count = 0
		pass
	def quiz_begin_msg(self,num):
		msg = f"🎲 🎲 Get ready for the quiz <b>'@WePrepareQuiz-Daily-Quiz Series-{str(num)}'</b>\n"
		msg += "\n"
		msg += "🖊 <b>100</b> questions"
		msg += "\n"
		msg += "⏱ <b>30</b> seconds for 1 marks "
		msg += "\n"
		msg += "⏱ <b>60</b> seconds for 2 marks"
		msg += "\n"
		msg += "📰 Votes are visible to group members and the quiz owner"
		msg += "\n"
		msg += "🏁 The quiz will begin when the questions are processed"
		self.sendm(msg)

	def sendm(self,t):
		self.context.bot.send_message(chat_id=self.chat_id, text=t,parse_mode=telegram.ParseMode.HTML)

	def get_sheet_shot(self,n):
		return shot_page(n)

	def startQuiz(self):
		self.quiz_begin_msg(self.sh_num)
		self.sendm("Processing Questions, May take a some time, have patience...")
		self.qinf = self.get_sheet_shot(self.sh_num)
		self.running = True
		self.m1_time = self.time_calc(self.qinf)
		self.sendPollHandle(0)
	def time_calc(self,qs):
		m_1qn = 0
		m_2qn = 0
		for qn in qs:
			if qn['marks'] == 1:
				m_1qn += 1
			if qn['marks'] == 2:
				m_2qn += 1
		# print(m_1qn,m_2qn)
		time_to_complete = 80 # Test is completed in 80 minutes
		return ((time_to_complete - m_2qn)/(100 - m_2qn))*60
		pass
	def sendPollHandle(self,i):
		if not self.running:
			return
		if i > 99:
			self.stopQuiz()
			return
		opentime = self.sendPoll(i)
		self.ltimer = Timer(opentime,self.sendPollHandle,(i+1,))
		self.ltimer.start()
	def sendPoll(self,n):
		self.send_timed_explaination()
		qn = self.qinf[n]
		opentime = self.m1_time
		if int(qn['marks']) == 2: opentime = 60
		# opentime = 5
		r_ans = qn['right_answer']
		copt = int(r_ans.replace('ans',''))-1
		imgob = self.context.bot.send_photo(chat_id=self.chat_id,photo=atob(qn['img']['question']))
		self.lastpoll = self.context.bot.send_poll(chat_id=self.chat_id, 
						question=f"[{n+1}/100] Choose the correct option. ({qn['marks']} mark)",
						is_anonymous=False, type='quiz', open_period=opentime,
						options=['A','B','C','D'],
						correct_option_id=copt
					)
		self.timed_explaination = qn['img']['explaination']
		poll_id = self.lastpoll.poll.id
		payload = {
			"timestamp": time.time(),
			"marks": qn['marks'],
			"correct_option": copt,
			"chat_id": self.chat_id
		}
		self.pollsInfo[poll_id] = payload
		self.context.bot_data.update({poll_id: payload})
		self.scoreinfo['tscore'] += qn['marks']
		self.question_count += 1
		return opentime
	def send_timed_explaination(self):
		if self.timed_explaination != None:
			try:
				self.context.bot.send_photo(chat_id=self.chat_id,photo=atob(self.timed_explaination))
			except:
				pass
	def isRunning(self):
		if self.ltimer != None:
			return True
		return self.running
	def stopQuiz(self):
		print('Stopping Quiz')
		if self.ltimer != None:
			print('LTIMER stopped')
			self.ltimer.cancel()
		if self.lastpoll != None:
			if not self.lastpoll.poll.is_closed:
				try:
					self.context.bot.stop_poll(self.chat_id,self.lastpoll.message_id)
				except telegram.error.BadRequest:
					pass
			self.send_timed_explaination()
		self.running = False
		self.show_results()
		pass
	def init_user_score(self,user):
		self.scoreinfo['uscores'][user.id] = {"score":0,"timetaken":0, "username":user.username, "first_name": user.first_name}
	def inc_user_score(self,user,marks):
		# print("Increasing score of user, ",user)
		if user.id not in self.scoreinfo['uscores']:
			self.init_user_score(user)
		self.scoreinfo['uscores'][user.id]['score'] += marks
		pass
	def inc_user_timetaken(self,user,dtime):
		if user.id not in self.scoreinfo['uscores']:
			self.init_user_score(user)
		self.scoreinfo['uscores'][user.id]['timetaken'] += dtime
		pass
	def sort_scorelist(self,scores):
		sortedlist = []
		for sc in scores:
			sortedlist.append([sc,scores[sc]])
		sortedlist.sort(key=lambda x:x[1]['score'],reverse=True)
		return sortedlist
	def show_results(self):
		# print(self.scoreinfo)
		chat_id = self.chat_id;
		scorelist = self.sort_scorelist(self.scoreinfo['uscores'])
		fullmarks = self.scoreinfo['tscore']
		sc_msg = f"🏁 The  quiz <i><b>@WePrepareIOE-Daily-Quiz-{self.sh_num}</b> has finished!!!\n\n<b>{self.question_count}</b> questions answered (Full-Marks:{fullmarks}) </i>\n\n"
		c = 0
		for sc in scorelist:
			c+=1
			# print(sc)
			is_cur_time = sc[1]['timetaken']
			formatted_is_cur_time = strfdelta(datetime.timedelta(seconds=is_cur_time),"%M min %S sec")
			sc_form = c;
			if sc_form < 4:
				sc_form = ["🥇","🥈","🥉"][sc_form-1]
			sc_msg += f"{str(sc_form)}.  <a href='tg://user?id={sc[0]}'>{sc[1]['username'] or sc[1]['first_name']}</a> - {sc[1]['score']} ({formatted_is_cur_time})\n"
		sc_msg += "\n\n🏆 Congratulations to the winners!"
		# print(sc_msg)
		self.sendm(sc_msg)
		pass





