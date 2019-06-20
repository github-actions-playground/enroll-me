FROM python:3.7-slim

LABEL "maintainer"="Sviatoslav Sydorenko <wk+github-actions-playground@sydorenko.org.ua>"
LABEL "repository"="https://github.com/github-actions-playground/enroll-me"
LABEL "homepage"="https://tutorial.octomachinery.dev"

LABEL "com.github.actions.name"="enroll-me"
LABEL "com.github.actions.description"="Create a GitHub Actions playground repo for an issue commenter"
LABEL "com.github.actions.icon"="user-plus"
LABEL "com.github.actions.color"="orange"

ADD . /usr/src/enroll-me
RUN pip install -r /usr/src/enroll-me/requirements.txt

ENV PYTHONPATH /usr/src/enroll-me

ENTRYPOINT ["python", "-m", "enroll_me.action"]
