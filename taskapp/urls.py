from django.urls import path
from .notification_views import NotificationView,UnReadNotificationView,MarkAsReadView,MarkAllAsReadView
from .project_views import CreateProjectView,ListProjectView,AddUserToProject,RemoveUserFromProject,UpdateProject,DetailProjectView,ProjectTaskDueToday,DeleteProject,SearchResult,AddProjectToFavorites
from .task_views import CreateTaskView,ListTaskView,AssignUsersToTask,SearchTaskMembers,UpdateTask,DeleteTask,TodaysDueTaskView,StatusOfTasks,CompleteTaskView
from .team_views import TeamMembers,LeaveTeam,SendInvitationView,ResponseToInvitationView,UserInvitationView
from .workspace_views import CreateWorkSpace,SwitchWorkspace,UserWorkSpace


urlpatterns = [
    path('list/user/workspace', UserWorkSpace.as_view()),
    path('search/result', SearchResult.as_view()),
    path('switch/workspace', SwitchWorkspace.as_view()),
    path('create/workspace', CreateWorkSpace.as_view()),
    path('create/task', CreateTaskView.as_view()),
    path('list/task', ListTaskView.as_view()),
    path('task/due/today', TodaysDueTaskView.as_view()),
    path('task/status', StatusOfTasks.as_view()),
    path('search/task/members', SearchTaskMembers.as_view()),
    path('update/task/<int:pk>', UpdateTask.as_view()),
    path('update/project/<int:pk>', UpdateProject.as_view()),
    path('team/memebers', TeamMembers.as_view()),
    path('leave/team/<int:pk>', LeaveTeam.as_view()),
    path('list/project', ListProjectView.as_view()),
    path('create/project', CreateProjectView.as_view()),
    path('project/<int:pk>', DetailProjectView.as_view()),
    path('add/project/favourite/<int:pk>', AddProjectToFavorites.as_view()),
    path('project/task/due/<int:pk>', ProjectTaskDueToday.as_view()),
    path('add/member/project/<int:pk>', AddUserToProject.as_view()),
    path('add/member/task/<int:pk>', AssignUsersToTask.as_view()),
    path('remove/member/project/<int:pk>', RemoveUserFromProject.as_view()),
    path('delete/project/<int:pk>', DeleteProject.as_view()),
    path('delete/task/<int:pk>', DeleteTask.as_view()),
    path('complete/task/<int:pk>', CompleteTaskView.as_view()),
    path('response/invitation/<int:pk>', ResponseToInvitationView.as_view()),
    path('send/invitation', SendInvitationView.as_view()),
    path('user/invitations', UserInvitationView.as_view()),
    path('user/notifications', NotificationView.as_view()),
    path('user/unread/notifications', UnReadNotificationView.as_view()),
    path('markasread/notifications/<int:pk>', MarkAsReadView.as_view()),
    path('markallasread/notifications', MarkAllAsReadView.as_view()),
]