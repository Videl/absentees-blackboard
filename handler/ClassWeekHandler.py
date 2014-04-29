from time import strftime,strptime

from handler.BaseHandler import *
from model.ADECommunicator import *
from model.Accounts import *


class ClassWeekHandler(BaseHandler):
    ade_communicator = None

    def __init__(self, request=None, response=None):
        self.initialize(request, response)
        self.page_name = "class_week"
        self.ade_communicator = ADECommunicator()

    def filter_lessons_of_week(self):
        all_lessons = self.ade_communicator.get_lessons()
        all_groups = self.ade_communicator.get_students_groups()

        current_user = get_connected_user(self.request.cookies['user_id'])

        users_groups = list()

        # Get the groups of one user
        for group in all_groups:
            members = all_groups[group]

            for member in members:
                if current_user.name in member['name']:
                    users_groups.append(group)

        # users_groups contains strings like:
        # [u'2A G42', u'2A IL 2']

        users_lessons = dict()
        # Filter all the lessons of one user
        for lesson in all_lessons:
            #logging.error(lesson)
            #logging.error(all_lessons[lesson])
            for one_class in all_lessons[lesson]:
                for one_group in users_groups:
                    if one_group in one_class['trainee']:
                        if lesson not in users_lessons.keys():
                            users_lessons[lesson] = list()
                        users_lessons[lesson].append(one_class)


        return users_lessons


    def get(self):
        my_lessons = self.filter_lessons_of_week()
        logging.error(">>>>>>>>>>>>>>>>>>>>>END OF THE FILTER<<<<<<<<<<<<<<<<<<<<<")
        logging.error("Result:")
        logging.error(my_lessons)


        ClassWeekHandler.renderTemp(self)

    def post(self):
        el=self.request.get('day_button')
        if el:
            ClassWeekHandler.renderTemp(self, el)
        else:
            ClassWeekHandler.renderTemp(self, el)

    def renderTemp(self, selected_day='0'):


        #Here days is a dict with 7 entry : one per day from monday tu sunday
        days_classes = dict()

        classes = dict()
        # based on ADECommunicator example
        # I create empty space which name is None to have an easy display
        # The height of each class_box is computed with start_time and end_time
        class0_example = {"class_name": "CM PGWEB 2A IL", "group": ["2A IL", "2A TRS"], "start_time": "8h00", "end_time": "10h00",
                "teacher_name": "CHAROY FRANCOIS"}
        class1_example =  {"class_name": "TP PGWEB 2A IL", "group": ["2A IL", "2A TRS"], "start_time": "10h00", "end_time": "12h45",
                "teacher_name": "CHAROY FRANCOIS"}
        class2_example = {"class_name": "None", "group": [], "start_time": "12h45", "end_time": "14h00",
                "teacher_name": ""}
        class3_example =  {"class_name": "TD MOCI 2A G1", "group": ["2A G1"], "start_time": "14h00", "end_time": "16h00",
                "teacher_name": "CHAROY FRANCOIS"}
        class4_example = {"class_name": "Exam PWEB", "group": ["2A IL"], "start_time": "16h00", "end_time": "17h00",
                "teacher_name": ""}
        class5_example =  {"class_name": "Something ...", "group": ["2A"], "start_time": "17h00", "end_time": "18h00",
                "teacher_name": "CHAROY FRANCOIS"}

        classes[0]=class0_example
        classes[1]=class1_example
        classes[2]=class2_example
        classes[3]=class3_example
        classes[4]=class4_example
        classes[5]=class5_example

        SaturdayAndSundayExample = dict()
        SandSEx ={"class_name": "None", "group": [], "start_time": "08h00", "end_time": "18h00",
                "teacher_name": ""}
        SaturdayAndSundayExample[0] = SandSEx

        #for the exemple I'll add the same classes, we'll be adapted with loops later ....
        days_classes[0]=classes
        days_classes[1]=classes
        days_classes[2]=classes
        days_classes[3]=classes
        days_classes[4]=classes
        days_classes[5]=SaturdayAndSundayExample
        days_classes[6]=SaturdayAndSundayExample

        week_nb = strftime("%W")
        year = strftime("%Y")
        buff = strptime('%s %s 1' %(year,week_nb), '%Y %W %w')
        buff2 = strptime('%s %s 0' %(year,week_nb), '%Y %W %w')

        first_day=strftime("%A %d %B",buff)
        last_day=strftime("%A %d %B",buff2)

        class_parameters = {'days':days_classes,'first_day':first_day,'last_day':last_day,'selected_day':selected_day}

        self.render('class_week.html', **class_parameters)