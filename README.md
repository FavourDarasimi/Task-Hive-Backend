# Task Hive API

## Overview

Task Hive API is a robust backend service for a collaborative task management application. Built with Python, Django, and Django REST Framework, it provides a comprehensive set of features for managing workspaces, projects, tasks, and teams through a RESTful interface secured with JWT authentication.

## Features

- **Django & Django REST Framework**: Provides a powerful and secure foundation for building the web API.
- **Simple JWT**: Implements JSON Web Token authentication for stateless and secure user sessions.
- **Workspace Management**: Users can create, switch between, and manage multiple workspaces.
- **Team Collaboration**: Supports team creation, member invitations, and collaborative project work.
- **Project & Task Management**: Full CRUD functionality for projects and their associated tasks, including assignments, deadlines, and status tracking.
- **Notification System**: In-app notifications for important events like task assignments, invitations, and status changes.

## Getting Started

### Installation

Follow these steps to set up the project locally.

1.  **Clone the repository**

    ```bash
    git clone https://github.com/FavourDarasimi/Task-Hive-Backend.git
    cd Task-Hive-Backend
    ```

2.  **Create and activate a virtual environment**

    ```bash
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Apply database migrations**

    ```bash
    python manage.py migrate
    ```

5.  **Run the development server**
    ```bash
    python manage.py runserver
    ```
    The API will be available at `http://127.0.0.1:8000`.

### Environment Variables

Create a `.env` file in the project root and add the following variables. While the project uses a default `SECRET_KEY`, it is best practice to override it.

```ini
SECRET_KEY='your-strong-secret-key-here'
DEBUG=True
```

## API Documentation

### Base URL

`http://127.0.0.1:8000/`

---

### Endpoints

### Authentication & Users

#### **POST** `/signup`

Registers a new user.

**Request**:

```json
{
  "username": "newuser",
  "first_name": "New",
  "last_name": "User",
  "email": "new.user@example.com",
  "password": "a-strong-password"
}
```

**Response**:

```json
{
  "message": "User Created Successfully",
  "data": {
    "username": "newuser",
    "first_name": "New",
    "last_name": "User",
    "email": "new.user@example.com",
    "is_online": false
  }
}
```

**Errors**:

- **400 Bad Request**: Invalid data or user already exists.

#### **POST** `/api/token`

Authenticates a user and returns JWT access and refresh tokens.

**Request**:

```json
{
  "username": "newuser",
  "password": "a-strong-password"
}
```

**Response**:

```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Errors**:

- **401 Unauthorized**: Invalid credentials.

#### **POST** `/api/refresh/token`

Refreshes an expired access token.

**Request**:

```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response**:

```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Errors**:

- **401 Unauthorized**: Invalid or expired refresh token.

#### **POST** `/logout`

Logs out the currently authenticated user. Requires authentication.

**Request**:
(No payload required)

**Response**:

```json
"User logged out"
```

**Errors**:

- **401 Unauthorized**: If the user is not authenticated.

#### **GET** `/is_authenticated`

Checks if the current user is authenticated.

**Request**:
(No payload required)

**Response** (Authenticated):

```json
{
    "is_authenticated": true,
    "user": {
        "id": 1,
        "username": "newuser",
        "email": "new.user@example.com",
        "first_name": "New",
        "last_name": "User",
        "is_online": true,
        "full_name": "New User",
        "profile": { ... }
    }
}
```

**Response** (Not Authenticated):

```json
{
  "is_authenticated": false
}
```

**Errors**:

- None.

#### **GET** `/view/profile`

Retrieves the profile of the authenticated user. Requires authentication.

**Request**:
(No payload required)

**Response**:

```json
{
  "id": 1,
  "user": 1,
  "age": null,
  "avatar": null,
  "phone_number": null,
  "gender": null,
  "occupation": null
}
```

**Errors**:

- **401 Unauthorized**: If the user is not authenticated.

#### **PUT** `/update/profile`

Updates the profile of the authenticated user. Requires authentication.

**Request**:

```json
{
  "first_name": "Updated",
  "last_name": "Name",
  "email": "updated.name@example.com",
  "age": 30,
  "phone_number": 1234567890,
  "gender": "Male",
  "occupation": "Developer"
}
```

**Response**:

```json
{
  "id": 1,
  "user": 1,
  "age": 30,
  "avatar": null,
  "phone_number": 1234567890,
  "gender": "Male",
  "occupation": "Developer"
}
```

**Errors**:

- **400 Bad Request**: Invalid data.
- **401 Unauthorized**: If the user is not authenticated.

---

### Workspaces

#### **POST** `/create/workspace`

Creates a new workspace for the authenticated user. Requires authentication.

**Request**:

```json
{
  "name": "My New"
}
```

**Response**:

```json
{
    "id": 2,
    "name": "My New's Workspace",
    "owner": { ... },
    "main": false,
    "space_id": 54321,
    "team": { ... },
    "active": []
}
```

**Errors**:

- **400 Bad Request**: Invalid data.
- **401 Unauthorized**: If the user is not authenticated.

#### **GET** `/list/user/workspace`

Lists all workspaces the authenticated user is a member of. Requires authentication.

**Request**:
(No payload required)

**Response**:

```json
{
    "workspaces": [
        {
            "id": 1,
            "name": "newuser's Workspace",
            ...
        }
    ],
    "active": {
        "id": 1,
        "name": "newuser's Workspace",
        ...
    }
}
```

**Errors**:

- **401 Unauthorized**: If the user is not authenticated.

#### **POST** `/switch/workspace`

Switches the user's active workspace. Requires authentication.

**Request**:

```json
{
  "last_workspace": 1,
  "new_workspace": 2
}
```

**Response**:

```json
{
  "message": "Workspace Switched Successfully"
}
```

**Errors**:

- **401 Unauthorized**: If the user is not authenticated.
- **404 Not Found**: If a workspace ID is invalid.

---

### Projects

#### **POST** `/create/project`

Creates a new project within the user's active workspace. Requires authentication.

**Request**:

```json
{
  "name": "New Website Design",
  "assigned_members": [{ "id": 2 }, { "id": 3 }]
}
```

**Response**:

```json
{
    "id": 1,
    "workspace": { ... },
    "user": { ... },
    "name": "New Website Design",
    "assigned_members": [ ... ],
    "favourite": false,
    "status": "In Progress",
    "created_at": "2023-10-27",
    "task": [],
    "percentage": 0
}
```

**Errors**:

- **400 Bad Request**: Invalid data.
- **401 Unauthorized**: If the user is not authenticated.

#### **GET** `/list/project`

Lists all projects the user is a member of in the active workspace. Requires authentication.

**Request**:
(No payload required)

**Response**:

```json
[
    {
        "id": 1,
        "workspace": { ... },
        "user": { ... },
        "name": "New Website Design",
        ...
    }
]
```

**Errors**:

- **401 Unauthorized**: If the user is not authenticated.

#### **GET** `/project/<int:pk>`

Retrieves details for a specific project. Requires authentication.

**Request**:
(No payload required)

**Response**:

```json
{
    "project": {
        "id": 1,
        "name": "New Website Design",
        ...
    },
    "task": [
        {
            "id": 1,
            "title": "Design Homepage Mockup",
            ...
        }
    ]
}
```

**Errors**:

- **401 Unauthorized**: If the user is not authenticated.
- **404 Not Found**: If project does not exist.

#### **PUT** `/update/project/<int:pk>`

Updates a project's details (e.g., name). Requires authentication.

**Request**:

```json
{
  "name": "Updated Project Name"
}
```

**Response**:
(Updated project object)

**Errors**:

- **400 Bad Request**: Invalid data.
- **401 Unauthorized**: If the user is not authenticated.
- **404 Not Found**: If project does not exist.

#### **DELETE** `/delete/project/<int:pk>`

Deletes a project and all its associated tasks. Requires authentication.

**Request**:
(No payload required)

**Response**:

- **204 No Content**: On successful deletion.

**Errors**:

- **401 Unauthorized**: If the user is not authenticated.
- **404 Not Found**: If project does not exist.

#### **PUT** `/add/project/favourite/<int:pk>`

Adds or removes a project from the user's favorites. Requires authentication.

**Request**:

```json
{
  "favourite": true
}
```

**Response**:
(Updated project object)

**Errors**:

- **401 Unauthorized**: If the user is not authenticated.
- **404 Not Found**: If project does not exist.

#### **PUT** `/add/member/project/<int:pk>`

Adds a team member to a project. Requires authentication.

**Request**:

```json
{
  "param": "member_username_or_email"
}
```

**Response**:

```json
{
  "message": "User Added"
}
```

**Errors**:

- **400 Bad Request**: User not in team or already added.
- **401 Unauthorized**: If the user is not authenticated.
- **404 Not Found**: If project or user does not exist.

#### **PUT** `/remove/member/project/<int:pk>`

Removes a member from a project. Requires authentication.

**Request**:

```json
{
  "param": "member_username_or_email"
}
```

**Response**:

```json
{
  "message": "User Removed"
}
```

**Errors**:

- **400 Bad Request**: User not in project, or attempting to remove the project creator.
- **401 Unauthorized**: If the user is not authenticated.
- **404 Not Found**: If project or user does not exist.

#### **GET** `/search/result`

Searches for projects by name within the user's active workspace. Requires authentication.
_Example Path: `/search/result?search=Website`_

**Request**:
(No payload required, uses query parameter)

**Response**:
(A list of matching project objects)

**Errors**:

- **401 Unauthorized**: If the user is not authenticated.

---

### Tasks

#### **POST** `/create/task`

Creates a new task. Can be associated with a project or a personal task. Requires authentication.

**Request** (for project):

```json
{
  "title": "Implement Login Form",
  "due_date": "2024-12-31",
  "priority": "High",
  "project": 1,
  "assigned_members": [{ "id": 2 }],
  "checked": true
}
```

**Response**:
(Newly created task object)

**Errors**:

- **400 Bad Request**: Invalid data.
- **401 Unauthorized**: If the user is not authenticated.

#### **GET** `/list/task`

Lists all tasks assigned to the user in the active workspace. Requires authentication.

**Request**:
(No payload required)

**Response**:
(A list of task objects)

**Errors**:

- **401 Unauthorized**: If the user is not authenticated.

#### **GET** `/task/status`

Provides a summary of all tasks, projects, and team members in the active workspace. Requires authentication.

**Request**:
(No payload required)

**Response**:

```json
{
    "all": [ ... ],
    "completed": [ ... ],
    "projects": [ ... ],
    "in_progress": [ ... ],
    "upcoming": [ ... ],
    "team": { ... },
    "missed_deadline": [ ... ]
}
```

**Errors**:

- **401 Unauthorized**: If the user is not authenticated.

#### **PUT** `/update/task/<int:pk>`

Updates a task's details. Requires authentication.

**Request**:

```json
{
  "title": "Updated Task Title",
  "priority": "Medium"
}
```

**Response**:
(Updated task object)

**Errors**:

- **400 Bad Request**: Invalid data.
- **401 Unauthorized**: If the user is not authenticated.
- **404 Not Found**: If task does not exist.

#### **DELETE** `/delete/task/<int:pk>`

Deletes a task. Requires authentication.

**Request**:
(No payload required)

**Response**:

- **204 No Content**: On successful deletion.

**Errors**:

- **401 Unauthorized**: If the user is not authenticated.
- **404 Not Found**: If task does not exist.

#### **PUT** `/complete/task/<int:pk>`

Marks a task as complete or incomplete. Requires authentication.

**Request**:

```json
{
  "complete": true,
  "projectId": 1
}
```

**Response**:
(Updated task object with status 'Completed')

**Errors**:

- **401 Unauthorized**: If the user is not authenticated.
- **404 Not Found**: If task does not exist.

#### **GET** `/task/due/today`

Lists tasks assigned to the user that are due today. Requires authentication.

**Request**:
(No payload required)

**Response**:
(A list of task objects)

**Errors**:

- **401 Unauthorized**: If the user is not authenticated.

---

### Teams & Invitations

#### **GET** `/team/memebers`

Retrieves the list of members in the active workspace's team. Requires authentication.

**Request**:
(No payload required)

**Response**:

```json
{
    "id": 1,
    "leader": { ... },
    "members": [ ... ]
}
```

**Errors**:

- **401 Unauthorized**: If the user is not authenticated.

#### **PUT** `/leave/team/<int:pk>`

Allows a user to leave a team or a leader to remove a member. Requires authentication.

**Request**:

```json
{
  "member_id": 2,
  "leader_id": 1,
  "remove": false
}
```

**Response**:
(Updated team object)

**Errors**:

- **401 Unauthorized**: If the user is not authenticated.
- **404 Not Found**: If team or user does not exist.

#### **POST** `/send/invitation`

Sends an invitation to a user to join the active workspace. Requires authentication.

**Request**:

```json
{
  "email": "user.to.invite@example.com"
}
```

**Response**:

```json
{
  "message": "Invitation sent Successfully"
}
```

**Errors**:

- **200 OK**: If user does not exist or is already in a team.
- **401 Unauthorized**: If the user is not authenticated.

#### **GET** `/user/invitations`

Retrieves all pending invitations for the authenticated user. Requires authentication.

**Request**:
(No payload required)

**Response**:
(A list of invitation objects)

**Errors**:

- **401 Unauthorized**: If the user is not authenticated.

#### **PUT** `/response/invitation/<int:pk>`

Accepts or declines a team invitation. Requires authentication.

**Request**:

```json
{
  "accepted": true,
  "sender": 1,
  "workspace": 1,
  "active": 2,
  "notification_id": 5
}
```

**Response**:

```json
{
  "accepted": "You Accepted the invite"
}
```

**Errors**:

- **401 Unauthorized**: If the user is not authenticated.
- **404 Not Found**: If invitation does not exist.

---

### Notifications

#### **GET** `/user/notifications`

Retrieves all notifications for the authenticated user. Requires authentication.

**Request**:
(No payload required)

**Response**:
(A list of notification objects)

**Errors**:

- **401 Unauthorized**: If the user is not authenticated.

#### **GET** `/user/unread/notifications`

Retrieves only unread notifications for the authenticated user. Requires authentication.

**Request**:
(No payload required)

**Response**:
(A list of notification objects)

**Errors**:

- **401 Unauthorized**: If the user is not authenticated.

#### **PUT** `/markasread/notifications/<int:pk>`

Marks a single notification as read. Requires authentication.

**Request**:

```json
{
  "read": true
}
```

**Response**:

```json
{
  "Message": "Notification Read"
}
```

**Errors**:

- **401 Unauthorized**: If the user is not authenticated.
- **404 Not Found**: If notification does not exist.

#### **POST** `/markallasread/notifications`

Marks all of the user's notifications as read. Requires authentication.

**Request**:
(No payload required)

**Response**:

```json
{
  "Read": "All Notification Read"
}
```

**Errors**:

- **401 Unauthorized**: If the user is not authenticated.
