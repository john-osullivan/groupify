from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from app import db

engine = create_engine('sqlite:///database.db', echo=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

# Set your classes here.

class User(Base):
    __tablename__ = 'users'

    '''
    Stores all users, gives a unique ID.  Allows for a name, email, password,
    phone number, 160 character biography, and a photo.  There is also a 
    one-to-many db.relationship with the Membership table, allowing each user
    to be a part of many groups.

    username = String(30), in-service name, unique and not nullable
    password = String(30), not nullable
    name = String(120), meant for real-world name, not unique
    email = String(120), unique
    phone = Integer, unique
    bio = String(160), super short self-description
    photo = LargeBinary, essentially a thumbnail to represent themselves
    memberships = -> Members, one-to-many, portal to all actual group management
    '''

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(30), nullable=False)
    name = db.Column(db.String(40))
    email = db.Column(db.String(40), unique=True)
    phone = db.Column(db.Integer, unique=True)
    bio = db.Column(db.String(160))
    photo = db.Column(db.LargeBinary)

    memberships = db.relationship("Member", backref= 'users')


    def __init__(self, username, password, name=None, email=None, phone=None, \
                            bio=None, photo=None, memberships=None):
        self.name = name
        self.username = username
        self.password = password
        self.email = email
        self.phone = phone
        self.bio = bio
        self.photo = photo
        self.memberships = memberships

    def __repr__(self):
        return "User #: %s"%(self.user_id)

# class GroupPartnership(Base):
#     __tablename__ = 'group_partnerships'

#     '''
#     GroupPartnership Table stores all the horizontal connections between groups.
#     It has its own tables because groups are horizontally connected in a
#     many-to-many db.relationship.  It takes two inputs to create a connection.  The
#     partnerships field describes groups which contain this group (i.e. TDC has a
#     representative at IFC).  The partners field describes groups which are contained
#     by this group (i.e. IFC has a number of partners, one of which is TDC).
#     '''

#     gp_id = db.Column(db.Integer, primary_key = True)

#     partnerships = db.Column(db.Integer, db.ForeignKey('groups.group_id'), primary_key=True)
#     partners = db.Column(db.Integer, db.ForeignKey('groups.group_id'), primary_key=True)

#     def __init__(self, partnerships=None, partners=None):
#         self.partners = partners
#         self.partnerships = partnerships

#     def __repr__(self):
#         return "Group Partnership #{0}".format(self.gp_id)

class Bond(Base):
    __tablename__ = 'bonds'
    '''
    Bond Table is a database of the connections between groups.  It takes the IDs of the two
    groups entering into a bond as initialization arguments. The groups attribute is a
    one-to-many relationship with Groups.  As of the current design (6/17/2014), a Bond can
    contain two and only two Groups.  They are pairwise links.  This constraint has to be
    ensured within the class.
    '''

    bond_id = db.Column(db.Integer, primary_key=True)
    
    groups = db.relationship("Group", backref='bonds')
    representatives = db.relationship("Representative", backref='bonds')

    def __init__(self, group1_id, group2_id):
        group1 = Group.query.get(group1_id)
        group2 = Group.query.get(group2_id)
        self.groups.append(group1)
        self.groups.append(group2)

    def __repr__(self):

    def is_valid(self):
        return len(self.groups) == 2


class Group(Base):
    __tablename__ = 'groups'

    '''
    Groups are the fundamental building block of the system.  Each one has a
    name, byline (160 character description), and full description.  Groups also
    contain members.  Every task assigned in a group is tied to that group via 
    a one-to-many relation.  Groups can be connected vertically or horizontally.
    A vertical connection implies a hierarchy -- TDC at MIT is a child of 
    TDC National.  A horizontal connection implies a partnership -- TDC at MIT
    cooperates with MIT IFC to help make Greek life better for everyone.

    code_name = String(80)
    human_name = String(80)
    byline = String(160)
    description = String(1024)
    members = --> Member, one-to-many
    tasks = --> Task, one-to-many
    partnerships = --> Group, many-to-many, describes non-hierarchical groups
                                this group is a member of
    partners = --> Group, many-to-many, describes non-hierarchical groups that
                            are a part of this group
    parent_id = ForeignKey(Group), each group has at most one parent group
    children = --> Group, one-to-many, each group can have as many children
                            groups as it wants
    '''

    group_id = db.Column(db.Integer, primary_key=True)
    human_name = db.Column(db.String(80), nullable=False)
    code_name = db.Column(db.String(80), unique=True, nullable=False)
    byline = db.Column(db.String(160))
    description = db.Column(db.String(2048))

    members = db.relationship('Member', backref='groups')
    tasks = db.relationship('Task', backref='groups')
    roles = db.relationship('Role', backref='groups')

    # Relations to establish bonds between groups.
    left_bond = db.relationship('Bond', backref='bonds')
    right_bond = db.relationship('Bond', backref='bonds')
    
    # Relations to establish one-to-many parent-child db.relationships.
    # NOTE: Not currently being used, as all group connection is being
    # handled by partnerships.
    parent_id = db.Column(db.Integer, db.ForeignKey('groups.group_id'))
    children = db.relationship('Group', backref='parent')

    def __init__(self, human_name, code_name, byline=None, description=None, members=None,\
                        parent_id=None, children=None):
        self.human_name = human_name
        self.code_name = code_name
        self.byline = byline
        self.description = description
        self.members = members
        self.parent_id = parent_id
        self.children = children
        self.roles = None

    def __repr__(self):
        return "Group #: %s --  Group Name: %s" % (self.group_id, self.name)


class Member(Base):
    __tablename__ = 'members'

    '''
    Members populate Groups.  All activites in the group correspond with the Member object, freeing
    the User from any specific Group interaction.  Each Member object has foreign keys to the group
    it's a part of and the user it is for.

    group_id = ForeignKey Integer to Group, many-to-one
    user_id = ForeignKey Integer to User, many-to-one
    preferred_name = String(80) - If the User wants to be known different in this context
    points = Integer - If a points sytem is in use, this is their running total.
    roles = --> Role, many-to-many, established by member_roles table
    doing_tasks = --> Task, one-to-many, describes tasks assigned TO the member
    giving_tasks = --> Task, one-to-many, describes tasks assigned BY the member
    '''

    member_id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.group_id'), default=None, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), default=None, index=True)
    
    preferred_name = db.Column(db.String(80))
    points = db.Column(Integer)

    roles = db.relationship('Role', backref='members')
    doing_tasks = db.relationship('Task', backref='members')
    giving_tasks = db.relationship('Task', backref='members')

    def __init__(self, group_id, preferred_name=None, points=None, roles=None):
        self.group_id = group_id
        self.preferred_name = preferred_name
        self.points = points
        self.roles = roles

    def __repr__(self):
        return "Member # of Group #: %s --- %s"%(self.member_id, self.group_id)

member_roles = db.Table(
    '''
    Handles the many-to-many db.relationship between members and roles, allowing for
    a role to have performed by multiple members or have one member perform 
    multiple roles.
    '''
    'member_roles', Base.metadata,
    db.Column('member_id', Integer, ForeignKey('members.member_id')),
    db.Column('role_id', Integer, ForeignKey('roles.role_id'))
    )

class Role(Base):
    __tablename__ = 'roles'

    '''
    Roles are the medium by which members can give or take on tasks.  Essentially, it represents
    any position in a group where you are given specific duties.  It has a name and
    description, and two many-to-many db.relationships with Tasks.  One db.relationship is for the Tasks
    assigned to the Role, the other is for Tasks assigned by the role.

    group_id = ForeignKey Group, many-to-one
    member_id = --> Member, many-to-many, so that one role can be performed by multiple people
    name = String(80), not nullable
    description = String(2048), to give people room to write out a decent description
    '''

    # Bookkeping ids
    role_id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.group_id'), index=True, nullable=False)
    member_id = db.relationship('Member', secondary=member_roles)

    # Position information
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(2048))
    
    # Responsiblity organization of both those given to you and those you give out.
    doing_task_id = db.Column(db.Integer, db.ForeignKey('tasks.task_id'))
    giving_task_id = db.Column(db.Integer, db.ForeignKey('tasks.task_id'))
    doing_tasks = db.relationship('Task', foreign_keys=[doing_task_id], backref='roles')
    giving_tasks = db.relationship('Task', foreign_keys=[giving_task_id], backref='roles')

    def __init__(self, group_id, name, member_id=None, description=None):
        self.group_id = group_id
        self.member_id = member_id
        self.name = name
        self.description = description

    def __repr__(self):
        return "Role #(%s) of Group #(%s) held by Member #(%s)"%(self.role_id, self.group_id, self.member_id)

member_tasks = db.Table(
    '''
    Table which handles the db.relationship between members and tasks.  Our goal is to have
    two members associated with each task, one who is giving it and one who is doing it.  The
    table has three columns, one for the giving_member_id, one for the doing_member_id, and
    one for the task_id.
    '''
    'member_tasks', Base.metadata,
    db.Column('giving_member_id', Integer, ForeignKey('members.member_id')),
    db.Column('given_member_id', Integer, ForeignKey('members.member_id')),
    db.Column('task_id', Integer, ForeignKey('tasks.task_id'))
    )

class Task(Base):
    __tablename__ = 'tasks'

    '''
    Tasks are the unit of gettings things done in the system.  They are meant to
    map to precisely two members: the member who assigned it and the member
    who is doing it.  Tasks are hierarchical, so a task can have subtasks.  
    All subtasks of a task should have their points values sum to no
    greater than the parent task, but that constraint is not yet enforced in the
    system.  A task given to every member in a role should actually 
    create a large number of sub-tasks for each member to individually complete.

    name = String(80) - Should just be a title
    description = String(512) - Fuller description of what should typically be done
    due_at = DateTime - The date/time at which this task is due.  To be used for reminders...
    delivered = Boolean - Whether the doer says they've finished the task
    approved = Boolean - Whether the giver says the task was fully satisfied
    points = Integer - Number of  points the task is worth
    comments = String(256) - Field for comments as needed
    parent_id = ForeignKey Task, points to the parent of this task_id
    children = --> Task, one-to-many to sub-tasks
    group_id = ForeignKey Group, points to the group this task was assigned as
                        a part of
    doing_id = ForeignKey Member, points to the member who is responsible for
                        completing the task
    giving_id = ForeignKey Member, points to the member who assigned the task
                        and is responsible for checking it
    '''

    task_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(512))
    deadline = db.Column(db.DateTime)
    delivered = db.Column(db.Boolean, default=False)
    approved = db.Column(db.Boolean, default=False)
    points = db.Column(db.Integer)
    comments = db.Column(db.String(256))

    # Relations to establish one-to-many parent-child db.relationships.
    parent_id = db.Column(db.Integer, db.ForeignKey('tasks.task_id'))
    children = db.relationship('Task', backref='parent')

    group_id = db.Column(db.Integer, db.ForeignKey('groups.group_id'), nullable=False)
    doing_id = db.Column(db.Integer, db.ForeignKey('members.member_id'), nullable=False)
    giving_id = db.Column(db.Integer, db.ForeignKey('members.member_id'), nullable=False)
 
    doer = db.relationship('Member', foreign_keys=[doing_id], secondary=member_tasks)
    giver = db.relationship('Member', foreign_keys=[giving_id], secondary=member_tasks)

    def __init__(self, name, doer_id, giver_id, group_id, description=None, points=None, \
                        comments=None):
        self.name = name
        self.description = description
        self.points = points
        self.comments = comments
        self.doing_id = doer_id
        self.giving_id = giver_id
        self.group_id = group_id
        self.delivered = False
        self.approved = False

    def __repr__(self):
        return "Task #(%s) of Group #(%s) held by Member #(%s)"%(self.task_id, self.group_id, self.doing_id)

class Infopage(Base):
    __tablename__ = 'infopages'

    '''
    Infopages allow for quick display of relevant information about a group, description of roles
    or any additional supporting material. Infopages are supposed to map to a group, a member, a user,
    a role, a task another infopage or not have any host at all (i.e. help page for groupify).
    For the developmental stage of groupify, Infopages shall be a massive container for HTML code that can
    be modified and made links between. Later on, a custom set of templates will be created to simplify and 
    standardize the look of all the Infopage instances.

    name = String(80) - big name of the Infopage
    description = String(150) - Short description of the infopage
    source_table = String(80) - String name of the table this Infopage points to
    source_id = ForeignKey value for source_table, specifies host of this Infopage
    content = String(42420) - The HTML holder for all the content
    children = --> sub-infopages, if any

    POTENTIAL REDESIGN:
    Invert the way infopages are referenced.  Every info page has a String representing the name
    of a table, and an integer ID representing which record in that table it's an Infopage for.
    '''

    infopage_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    source_table = db.Column(db.String(80), nullable=False)
    source_id = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(1024))
    content = db.Column(db.String(42420))

    # Relations to establish one-to-many parent-child db.relationships.
    children = db.relationship('Infopage', backref='parent') # +1 This is really slick. -JJO

    def __init__(self, name, source_table, source_id, description=None, content=None):
        self.name = name
        self.source_table = source_table
        self.source_id =source_id
        self.description = description
        self.content = content

    def __repr__(self):
        return "Infopage #{0} -- {1} #{2} -- {3}".format(self.infopage_id, self.source_table,\
                self.source_id, self.name)

class Event(Base):
    __tablename__ = 'events'

    '''
    Events are a class for getting people to come to a particular place at a particular time.
    Events have a date, RSVP lists, location, description, name, duration and attended/missed people.

    name = String(80) - big name of the Event
    description = String(150) - Short description of the Event
    creator_id = ForeignKey - Original creator of the event
    date = DateTime - the date and time of the event
    duration = DateTime - the duration of the event
    rsvp_yes/rsvp_no - collection of members who are RSVPing yes or no
    attended_yes/attended_no - collection of member who attended or not
    location = String(200) - location of the event, if any
    host - collection of additional people who can be added to host the event

    '''

    # A couple of parameters defining the different unique characteristics of an event type
    event_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(2000))
    creator_id = db.Column(db.Integer, db.ForeignKey('members.member_id'))
    start_time = db.Column(db.DateTime(datetime.datetime(0)))
    end_time = db.Column(db.DateTime(datetime.datetime(0)))

    # List of people invited to the event
    invited = db.relationship('Member', backref='events')

    # People's responses to the event will be recorded here
    rsvp_yes = db.relationship('Member', backref='events')
    rsvp_no = db.relationship('Member', backref='events')

    # List of people who attended and those who didn't, not always used
    attended_yes = db.relationship('Member', backref='events')
    attended_no = db.relationship('Member', backref='events')
    
    # See if there is a way to format location similarly to datetime, until then its a String
    location = db.Column(db.String(200))

    # Hosts are people who also have creator access
    host = db.relationship('Member', backref='events')

    def __init__(self, name, start_time=None, end_time=None, host_group_id=None, host_task_id=None, host_user_id=None, host_role_id=None, \
                        host_member_id=None, host_gp_id=None, content=None, description=None):
        self.name = name
        self.description = description
        self.creator_id=creator_id
        self.start_time=start_time
        self.end_time=end_time
        self.rsvp_yes=rsvp_yes
        self.rsvp_no=rsvp_no
        self.attended_yes=attended_yes
        self.attended_no=attended_no
        self.location=location

    def __repr__(self):
        return "Event #(%s) created by Member #(%s)"%(self.event_id, self.creator_id)

class Representative(Base):
    __tablename__ = 'representatives'
    '''
    A table containing information unique to a Representative.  Which group are they from,
    which group are they representing in.  Also a string describing how it's chosen -- elected
    or appointed.
    '''

    def __init__(self):

    def __repr__(self):

class Committee(Base):
    __tablename__ = 'committees'
    '''
    A table containing the internal sub-groupings.  A committee is a Group which is meant
    to be purely internal to another Group.  It can't Bond with Groups other than its host,
    and it shares all InfoPage access with the host group.  It is only separate because it
    allows for special functionality of smaller, lighter sub-spaces within the larger Group
    space.
    '''
    def __init__(self):

    def __repr__(self):

# Create tables.
Base.metadata.create_all(bind=engine)