import time
import re

from handler.BaseHandler import *
from model.ADECommunicator import *
from model.Absentees import *
import time

class ClassAbsenteesHandler(BaseHandler):
    temp_prof_name = "CHAROY FRANCOIS"
    ade_communicator = None

    def __init__(self, request=None, response=None):
        self.initialize(request, response)
        self.page_name = "class_absentees"
        self.ade_communicator = ADECommunicator()

    def filter_teacher_class(self, teacher, time, date):
        """all_lessons = self.ade_communicator.get_lessons()

        teacher_classes = list()

        # Subject looks like 'TP TNI 2A G11'
        for subject in all_lessons:

            # lesson is a list of:
            # [ ...,
            # {'classroom': u'AIPL 3',
            # 'date': u'10/12/2013',
            # 'endHour': u'18:00',
            # 'instructor': u'SCHEID JEAN-FRANCOIS',
            # 'startHour': u'14:00',
            # 'trainee': [u'2A G11']},
            # ...,
            # ]
            for lesson in all_lessons[subject]:

                if 'instructor' in lesson.keys():
                    if lesson['instructor'] == teacher:
                        teacher_classes.append(lesson)

        #logging.error("Result")
        #logging.error(teacher_classes)

        first_step = list()

        # Filter by date
        for lesson in teacher_classes:
            if lesson['date'] == date:
                first_step.append(lesson)

        final_step = None
        # Filter by time
        my_time = time.split(':')
        my_time[0] = int(my_time[0])
        my_time[1] = int(my_time[1])

        for lesson in first_step:
            lesson_start_time = lesson['startHour'].split(':')
            lesson_start_time[0] = int(lesson_start_time[0])
            lesson_start_time[1] = int(lesson_start_time[1])
            lesson_end_time = lesson['endHour'].split(':')
            lesson_end_time[0] = int(lesson_end_time[0])
            lesson_end_time[1] = int(lesson_end_time[1])

            # if we are the same hours, compare minutes
            if lesson_start_time[0] == my_time[0]:
                if lesson_start_time[1] <= my_time[1]:
                    final_step = lesson
            elif lesson_end_time[0] == my_time[0]:
                if my_time[1] <= lesson_end_time[1]:
                    final_step = lesson
            # else if hours are not the same, compare hours
            elif lesson_start_time[0] < my_time[0] and my_time[0] < lesson_end_time[0]:
                final_step = lesson"""

        return {"class_name": "TP PGWEB 2A IL", "groups": ["2A IL"], "start_time": "10h00", "end_time": "12h00",
                "teacher_name": "CHAROY FRANCOIS", "room": "S2.42"}

        """if final_step is None:
            return None
        else:
            return {"class_name": final_step["subject"],
                    "groups": final_step["trainee"],
                    "start_time": final_step["startHour"],
                    "end_time": final_step["endHour"],
                    "teacher_name": final_step["instructor"],
                    "room": final_step["classroom"]}"""

    def get(self):
        #Test user connexion and privileges
        if self.is_connected() and get_is_teacher_from_id(self.request.cookies.get('user_id').split('|')[0]):
            #First, get the class the teacher should have right now
            class_date = time.strftime("%d/%m/%Y")
            class_to_display = self.filter_teacher_class(self.temp_prof_name, time.strftime("%H:%M"), class_date)

            #If there's a class
            if class_to_display is not None:
                #Then, we get the students for this class
                students_list = []
                groups = self.ade_communicator.get_students_groups()

                for group_name in groups:
                    for group_to_find in class_to_display['groups']:
                        if re.match(group_to_find, group_name) is not None:
                            temp = []
                            for student in groups[group_name]:
                                temp.append({"name": student, "group": group_name})

                            students_list.extend(temp)

                students_list.sort(key=lambda x: x['name'])

                #Check for already done absentees
                present_absentees = get_absentees_for_class(class_to_display['class_name'],
                                                            class_to_display['teacher_name'], class_date,
                                                            class_to_display['start_time'],
                                                            class_to_display['end_time'])

                mail_absentees = []
                if len(present_absentees) != 0:
                    for student_abs in present_absentees:
                        mail_absentees.append(student_abs.student_email)

                #Render the page
                self.render("class_absentees.html", students=students_list, absentees=mail_absentees,
                            **class_to_display)

            #Else, congrats, the teacher doesn't have to do anything
            else:
                self.render("message.html", title="No lessons found!", subtitle="Looks like you don't have to work!")
        else:
            self.render("message.html", title="Access forbidden",
                        text="It seems you're not a teacher nor a connected user")

    def post(self):
        #Test user connexion and privileges
        if self.is_connected() and get_is_teacher_from_id(self.request.cookies.get('user_id').split('|')[0]):
            #First, get the class the teacher should have right now
            class_date = time.strftime("%d/%m/%Y")
            class_to_display = self.filter_teacher_class(self.temp_prof_name, time.strftime("%H:%M"), class_date)

            #If there's a class
            if class_to_display is not None:
                #Then, we get the students for this class
                students_list = []
                groups = self.ade_communicator.get_students_groups()

                for group_name in groups:
                    for group_to_find in class_to_display['groups']:
                        if re.match(group_to_find, group_name) is not None:
                            temp = []
                            for student in groups[group_name]:
                                temp.append({"name": student, "group": group_name})

                            students_list.extend(temp)

                students_list.sort(key=lambda x: x['name'])

                #Purge current absentees
                present_absentees = get_absentees_for_class(class_to_display['class_name'],
                                                            class_to_display['teacher_name'], class_date,
                                                            class_to_display['start_time'],
                                                            class_to_display['end_time'])
                db.delete(present_absentees)

                #Check who is present now from post argument
                for student in students_list:
                    name = student['name']['name']
                    mail = student['name']['mail']

                    if self.request.get(mail + "|" + name + "|box"):
                        absentee = Absentees(student_name=name, student_email=mail,
                                             student_group=student['group'],
                                             class_title=class_to_display['class_name'],
                                             teacher_name=class_to_display['teacher_name'],
                                             start_hour=class_to_display['start_time'],
                                             end_hour=class_to_display['end_time'],
                                             class_date=class_date, justification_bool=False)
                        absentee.put()

                time.sleep(1)
                self.redirect('/class_absentees')
            #Else, congrats, the teacher doesn't have to do anything
            else:
                self.redirect('/class_absentees')

        else:
            self.render("message.html", title="Access fobidden",
                        text="It seems you're not a teacher nor a connected user")