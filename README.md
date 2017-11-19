# gr***** - A full-stack micro-blogging website
**Author:** Stephen Xie  
**Project Version:** 6.0.0

gr***** is a Django-based full-stack micro-blogging website. It's a featureful, near-production-ready web application that supports user registration and authentication, email integration, photo upload, and dynamic quasi-real-time updates.

Detailed documentations to be added later.


## Quick Notes

- Before someone mentions it again, yes I do know about the bad positioning of the follow / unfollow button ;p

- I used the Django shell (`manage.py shell`) to test my models during development. I should have utilized the unit testing tools from Django to standardize and automate the testing process. My bad...

- Heroku automatically collects static files during deployment, so you don't have to worry about that. Otherwise run `python manage.py collectstatic` to collects them to STATIC_ROOT after the debug mode is switched off. More info on [Django](https://docs.djangoproject.com/en/1.11/ref/contrib/staticfiles/).

- Right now the website uses HTTP polling strategy to update the grumbles (messages) in a fixed interval (10s). This may not be an efficient solution for real-time message streams esp. for a social website. To be updated to WebSocket (e.g. Django Channels).


## Screenshots

<img src="archive/screenshots/login.jpg" width="800" alt="Login">

<img src="archive/screenshots/signup.jpg" width="800" alt="Signup">

<img src="archive/screenshots/home.jpg" width="800" alt="Home">

<img src="archive/screenshots/profile.jpg" width="800" alt="Profile">

<img src="archive/screenshots/profile_settings.jpg" width="800" alt="Profile Settings">

<img src="archive/screenshots/pass_reset.jpg" width="800" alt="Password Reset">


## Pre-registered accounts

| Username | Password | Note                     |
|----------|----------|--------------------------|
| admin    | admin    | Is Project Administrator |
| jon      | jon      |                          |
| steve    | steve    |                          |
| seth     | seth     |                          |
| john     | john     |                          |
