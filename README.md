
# Django To Do List App

This project is a simple to do list application using Django.


## Authors

- [Juan Esteban Oviedo](https://github.com/juanoviedog)

## Features

- Add items with detailed descriptions.
- See, update and delete items on your list.
- User login and registration support.


## Tech Stack

**Client:** HTML, CSS

**Server:** Python, Django

**Database Service:** SQLite using Django ORM




## Screenshots

## Login and Registration

Users have the possibility to register and log into their accounts to keep their own tasks. All pages are handled using class based views, increasing development speed. 

![App Screenshot](https://raw.githubusercontent.com/juanoviedog/django-todo/main/Screenshots/RegisterSite.png)

![App Screenshot](https://raw.githubusercontent.com/juanoviedog/django-todo/main/Screenshots/Login.png)

## Home Site 
The home page provides a general view of all tasks for a given user. 
![App Screenshot](https://raw.githubusercontent.com/juanoviedog/django-todo/main/Screenshots/HomePage.png)

## Add Task 
Any user can add tasks to his own list, each consisting of a title and a description. 
![App Screenshot](https://raw.githubusercontent.com/juanoviedog/django-todo/main/Screenshots/AddTaskView.png)

The following is a view of the task list including a completed task.
![App Screenshot](https://raw.githubusercontent.com/juanoviedog/django-todo/main/Screenshots/CompletedTask.png)

## Search For Tasks
A user can search inside his tasks. The search is performed using containment but the code can be modified to allow for other types of search. 
![App Screenshot](https://raw.githubusercontent.com/juanoviedog/django-todo/main/Screenshots/SearchTasks.png)

## Delete Task 
If a user wishes to delete a task he will be provided with a confirmation dialogue, to avoid mistakes.
![App Screenshot](https://raw.githubusercontent.com/juanoviedog/django-todo/main/Screenshots/TaskDeleteConfirmation.png)

## Installation

To start the application just clone the repository, and while in the same directory, you will need to run the following commands.

- First install the required libraries for the application, including django.

```
pip install requirements.txt
```

- Run the application using python. 
```
python manage.py runserver
```
