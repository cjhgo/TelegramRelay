#coding: utf-8
#created at 17-03-20 14:37
from __future__ import with_statement
from fabric.api import run, local, env, settings, cd
from fabric.contrib.console import confirm

env.use_ssh_config = True
env.hosts=["me"]


def commit(commit_message="fix"):
    local("git add -p ")
    local("git commit -m '{}'".format(commit_message))

def push():
    local("git push -u origin master")

def deploy():
    with settings(warn_only=True):
        commit()
        push()    
    code_dir = '/data/python/pda'
    with cd(code_dir):
        run('git pull origin master')
        run('supervisorctl restart pda')