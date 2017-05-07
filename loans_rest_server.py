''' Trivial Eve-SQLAlchemy example. '''
from eve import Eve
from sqlalchemy import Column, Integer, String, DateTime, Date,Boolean,ForeignKey,Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import column_property,relationship,mapper
from eve_sqlalchemy import SQL
from eve_sqlalchemy.decorators import registerSchema
from eve_sqlalchemy.validation import ValidatorSQL
import datetime
from faker import Factory
import datetime
import random
from flask_swagger_ui import get_swaggerui_blueprint
from eve_swagger import swagger, add_documentation

from settings import (SWAGGER_URL,
                      API_URL,
                      APP_HOST,
                      APP_PORT,
                      VCAP_CONFIG,
                      SWAGGER_INFO,
                      DEBUG,
                      SQLALCHEMY_DATABASE_URI)

phases = ["Eligibility Check","Marriage Check","Spouse Consent","Form Available","Admin Approval"]
statuses =["Submitted","Pending","Failed","Passed","Approved"]


Base = declarative_base()

class CommonColumns(Base):
    __abstract__ = True
    _created = Column(DateTime, default=datetime.datetime.now())
    _updated = Column(DateTime,
                      default=datetime.datetime.now(),
                      onupdate=datetime.datetime.now())
    _etag = Column(String)
    _id = Column(Integer, primary_key=True, autoincrement=True)

    @classmethod
    def from_tuple(cls, data):
        """Helper method to populate the db"""
        if cls.__tablename__ == "participant":
            return cls(firstname=data[0], lastname=data[1],dateofbirth=data[2],address=data[3],flag_married=data[4])

        if cls.__tablename__ == "plan":
            return cls(planname=data[0], description=data[1])

        if cls.__tablename__ == "enrollment":
            return cls(plan=data[0], participant=data[1],
                        flag_spouse_cnsnt=data[2],
                        flag_form_present=data[3],
                        amount=data[4])

        if cls.__tablename__ == "loan":
            return cls(enrollment=data[0], amount=data[1],status=data[2],phase=data[3])

        if cls.__tablename__ == "loanreqhistory":
            return cls(loan=data[0],status=data[1],phase=data[2])


class Participant(CommonColumns):
    __tablename__ = 'participant'
    __table_args__ = ({"schema": "loans_demo"})
    firstname = Column(String(80))
    lastname = Column(String(120))
    fullname = column_property(firstname + " " + lastname)
    dateofbirth = Column(Date)
    address = Column(String(300))
    age = column_property(dateofbirth-datetime.date.today())
    flag_married = Column(Boolean)

class Plan(CommonColumns):
    __tablename__ = 'plan'
    __table_args__ = ({"schema": "loans_demo"})
    planname = Column(String(80))
    description = Column(String(120))


class Enrollment(CommonColumns):
    __tablename__ = 'enrollment'
    __table_args__ = ({"schema": "loans_demo"})
    participant_id = Column(Integer,ForeignKey('loans_demo.participant._id'))
    plan_id = Column(Integer,ForeignKey('loans_demo.plan._id'))
    flag_spouse_cnsnt = Column(Boolean)
    flag_form_present = Column(Boolean)
    amount = Column(Float)
    participant = relationship(Participant)
    plan = relationship(Plan)

    
class Loan(CommonColumns):
    __tablename__ = 'loan'
    __table_args__ = ({"schema": "loans_demo"})
    enrollment_id =  Column(Integer,ForeignKey('loans_demo.enrollment._id'))
    amount = Column(Float)
    status = Column(String(30))
    phase = Column(String(60))
    enrollment = relationship(Enrollment)

class LoanReqHistory(CommonColumns):
    __tablename__ = 'loanreqhistory'
    __table_args__ = ({"schema": "loans_demo"})
    loan_id=Column(Integer,ForeignKey('loans_demo.loan._id'))
    status = Column(String(30))
    phase = Column(String(60))
    loan = relationship(Loan)



registerSchema('participant')(Participant)
registerSchema('plan')(Plan)
registerSchema('enrollment')(Enrollment)
registerSchema('loan')(Loan)
registerSchema('loanreqhistory')(LoanReqHistory)

DOMAIN = {
        'participant': Participant._eve_schema['participant'],
        'plan': Plan._eve_schema['plan'],
        'loan': Loan._eve_schema['loan'],
        'enrollment': Enrollment._eve_schema['enrollment'],
        'loanreqhistory': LoanReqHistory._eve_schema['loanreqhistory'],
}


SETTINGS = {
    'DEBUG': DEBUG,
    'SQLALCHEMY_DATABASE_URI': SQLALCHEMY_DATABASE_URI,
    'DOMAIN': DOMAIN
}

app = Eve(auth=None, settings=SETTINGS, validator=ValidatorSQL, data=SQL)

# required. See http://swagger.io/specification/#infoObject for details.
app.config['SWAGGER_INFO'] = SWAGGER_INFO

# bind SQLAlchemy
db = app.data.driver
Base.metadata.bind = db.engine
db.Model = Base
db.create_all()

# Insert some example data in the db


test_participant_data = []
test_plan_data = []

fake = Factory.create('en_US')
for i in range(10):
    # Participant data
    firstname = fake.first_name()
    lastname = fake.last_name()
    dateofbirth = fake.date()
    address = fake.address()
    flag_married = fake.pybool();
    test_participant_data.append((firstname,lastname,dateofbirth,address,flag_married))
#print(test_participant_data)

# Plan data
for i in range(10):
    planname = fake.company()
    description = fake.sentence()
    test_plan_data.append((planname,description))

if not db.session.query(Participant).count():
   print("Adding Participant Data")
   # Participant data updated to DB
   for item in test_participant_data:
       db.session.add(Participant.from_tuple(item))
       print("adding:",item)
   db.session.commit()

if not db.session.query(Plan).count():    
   print("Adding Plan Data")
   # Plan data updated to DB
   for item in test_plan_data:
       db.session.add(Plan.from_tuple(item))
       print("adding:",item)
   db.session.commit()

if not db.session.query(Enrollment).count():
    print("Adding Enrollment Data")
    # Enrollment data updated to DB
    for i in range(10):
        plan = db.session.query(Plan).filter_by(_id=random.randint(1,10)).first()
        participant = db.session.query(Participant).filter_by(_id=random.randint(1,10)).first()
        if participant.flag_married == True:
            flag_spouse_cnsnt = fake.pybool()
            flag_form_present = fake.pybool()
        amount = fake.pydecimal(positive=True)
        item = (plan,participant,flag_spouse_cnsnt,flag_form_present,amount)
        print("adding:",item)
        db.session.add(Enrollment.from_tuple(item))
    db.session.commit()

if not db.session.query(Loan).count():
    print("Adding Loan Data")
    #Loan data updated to DB
    for i in range(10):
        amount  = fake.pydecimal(positive=True)
        enrollment = db.session.query(Enrollment).filter_by(_id=random.randint(1,10)).first()
        phase = phases[random.randint(0,len(phases)-1)]
        status = statuses[random.randint(0,len(statuses)-1)]
        item = (enrollment,amount,status,phase)
        print("adding:",item)
        db.session.add(Loan.from_tuple(item))
    db.session.commit()

if not db.session.query(LoanReqHistory).count():
    print("Adding LoanReqHistory Data")
    # Loan LoanReqHistory
    for i in range(100):
        loan = db.session.query(Loan).filter_by(_id=random.randint(1,10)).first()
        phase = phases[random.randint(0,len(phases)-1)]
        status = statuses[random.randint(0,len(statuses)-1)]
        item = (loan,status,phase)
        print("adding:",item)
        db.session.add(LoanReqHistory.from_tuple(item))
    db.session.commit()

# Call factory function to create our blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
    API_URL,
    config={  # Swagger UI config overrides
        'supportedSubmitMethods': ['get']
    }
)

# Register blueprint at URL
# (URL must match the one given to factory function above)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
app.register_blueprint(swagger)

app.run(debug=True, use_reloader=False)
