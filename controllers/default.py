# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################

if False:  
    from gluon import *
    from models.db import *  #repeat for all models
    from models.menu import *
    request = current.request
    response = current.response
    session = current.session
    cache = current.cache
    
    
    
def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simple replace the two lines below with:
    return auth.wiki()
    """


    return dict(message='')


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())

@auth.requires_membership('parent')
def edit_chores():
    grid= SQLFORM.grid(db.chore)
    return dict(form=grid)

@auth.requires_membership('parent')
def pay_jobs():
    grid= SQLFORM.grid(db.job,editable=False,details=False,deletable=False,
        links = [lambda row: A('Mark Paid',_class = 'btn',
        _href=URL("mark_job_paid",args=[row.id]))])
    return dict(form=grid)

@auth.requires_membership('parent')
def mark_job_paid():
    run_id = request.args(0)
    if run_id:
        pass
    

@auth.requires_login()
def submit_jobs():
    db.job.approver.readable= False
    db.job.approver.writable= False
    child_query = ((db.auth_group.role == 'child') &
        (db.auth_membership.group_id == db.auth_group.id) & 
        (db.auth_user.id == db.auth_membership.user_id))
    child_set = db(child_query)
    db.job.child.requires = IS_IN_DB( child_set,'auth_user.id','auth_user.username')
    grid=SQLFORM.grid(db.job,fields=[db.job.chore,db.job.child,db.job.job_date])
    return dict(form=grid)

@auth.requires_login()
def list_jobs():
    job_query = (   (db.job.child == auth.user_id) &
                   (db.chore.id == db.job.chore))
    grid=SQLFORM.grid(job_query,editable=False,deletable=False,details=False,
                      fields=[db.job.child,db.chore.chore_name,db.job.job_date,
                              db.chore.chore_value,db.chore.chore_reward,db.job.approver])
    return dict(form=grid)



@auth.requires_membership('parent')
def approve_jobs():
    parent_query = ((db.auth_group.role == 'parent') &
        (db.auth_membership.group_id == db.auth_group.id) & 
        (db.auth_user.id == db.auth_membership.user_id))
    parent_set = db(parent_query)
    db.job.approver.requires = IS_IN_DB( parent_set,'auth_user.id','auth_user.username')
    grid=SQLFORM.grid(db.job)
    return dict(form=grid)
