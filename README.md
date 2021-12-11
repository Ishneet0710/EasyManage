# EasyManage
Productive and Efficient Task/Project Manager Discord Bot
# Features
- Add tasks 
- View tasks
- Delete tasks when completed
- Add meetings
- View upcoming meetings
- Obtain daily meeting summaries
- Add reminders
- Pomodoro timers
- Get daily inspirational quotes
# How to use it

With this bot, you can begin commands with the prefix **!** and separate arguments with **, ** (a comma followed by a space).

### tasks

##### assign a task:

`!addTask task title, task description, due date, @person1#1234 @person2#1234`

- note that the task date must be formatted as such: `YYYY/MM/DD` or`2021-08-04`
- multiple people can be mentioned

##### view your assigned tasks:

`!viewTasks`

##### delete/complete your tasks:

`!deleteTask task title`



### meetings

##### add a meeting

`!addMeeting meeting title, meeting description, meeting url, meeting date and time, @person1#1234 @person2#1234`

- note that the date and time must be formatted as such: `YYYY/MM/DD HH:MM PM` or `2021-08-14 10:00 PM`

- multiple people can be mentioned

##### view your upcoming meetings

`!viewMeetings`
- meetings wil automatically be deleted the day after they occur

##### get daily meeting summaries

you can get a summary of your upcoming meetings daily! just use this command in the channel you'd like to receive the summary.

`!set_summary_channel`

### pomodoro

##### add no. of sessions for pomodoro

`!pomodoro @person1#1234 sessions`

### quote

##### get quote

`!quote`


### reminder

##### add reminder

`!reminder time, title`
- time must be in minutes
- after the time is up, reminder will pop up



