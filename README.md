<div align="center">
<img src="/assets/recommenda.jpg" style="width: 400px">
</div>
<br>

Recommenda is a recommendation app that allows freinds to recommend various types of media to each other. How often has a friend recommended something to you, but you don't write it down and later forget about it? Now you can have all your recommendations for books, films, music, podcasts and articles in one place!

## Table of contents
- [Description](#description)
- [Demo](#demo)
- [How to use Recommenda](#how-to-use-recommenda)
- [User interface](#user-interface)
- [Technologies](#technologies)
- [Project status](#project-status)

## Description
This app is primarily intended for use on mobile devices, and as such was designed using the mobile-first design principle. The front-end is primarily basic bootstrap styling (this allowed me to focus on the functionality of the app).

There are two main parts of functionality that were implemented: the social network, and the interaction with the APIs. The social media network allows users to sign up and then login using an email address and password, afterwhich they are able to follow other users. Once the user has followers, they can recommend items to these followers. The APIs allow users to asscess content to recommend to their followers. Various APIs are used to search and fetch content of a specific media type (e.g. books use the [Google Books API](https://developers.google.com/books/docs/v1/using)).

## Demo
Try it out at https://clairesquires99.pythonanywhere.com/. 

Sign up or use one of the already created profiles to test the app out.

**User A**<br>
Email: _usera@gmail.com_<br>
Password: _password_

**User B**<br>
Email: _userb@gmail.com_<br>
Password: _password_

## How to use Recommenda

1. Sign up using an email address
2. Login using your email address and password
3. Go to you profile, and click "following"
4. Enter the email address of a friend using Recommenda
5. You will now see their name under "following"
6. Your friend can now send you recommendations
7. To send your friends recommendations, tell them to follow you!

## User interface
<div float="left">
<img src="/assets/books.png" width="250px">
<img src="/assets/films.png" width="250px">
<img src="/assets/profile.png" width="250px">
</div>

## Technologies

### Libraries

- Flask v2.2.2
- Flask-Login v0.6.2
- Flask-SQLAlchemy v2.5.1
- Jinja2 v3.1.2
- PyYAML v6.0
- requests v2.28.1
- SQLAlchemy v1.4.41
- Bootstrap v5

_For a complete list, see [requirements.txt](requirements.txt)_

### APIs

- Books: [Google Books API](https://developers.google.com/books/docs/v1/using)
- Films: [The Movie Database API](https://developers.themoviedb.org/3/getting-started/introduction)
- Music: [Spotify API](https://developer.spotify.com/documentation/web-api/)
- Podcasts: tbc
- Articles: tbc

## Project status

This project is still in development. There are several features that are scheduled to be implemented before the app is complete, as well as several features that are not strictly necessary, but will improve the user experience.

### Features to implement
#### For completion
- [x] Media type Books (realeased v1)
- [x] Meida type Films (released v2)
- [ ] Media type Music
- [ ] Media type Podcasts
- [ ] Media type Articles
- [ ] Fix problems with unreadable titles from Google Books API (causes internal server error)

#### For improved user experience

- [ ] Allow users to recommend items to themselves
- [ ] Lazy loading on images
- [ ] Allow users to recommend an item to several people at once
- [ ] Allow users to delete recommendations
- [ ] Allow users to unfollow users they are currently following
