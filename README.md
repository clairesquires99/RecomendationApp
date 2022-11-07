# Recommenda

Recommenda is a recommendation app that allows freinds to recommend various types of media to each other. How often has a friend recommended something to you, but you don't write it down and later forget about it. Now you can have all your recommendations for books, films, podcasts, music and articles in one place!

**DEMO**: Try it out [here](https://clairesquires99.pythonanywhere.com/).

## Table of contents

- [How to use Recommenda](#how-to-use-recommenda)
- [User interface](#user-interface)
- [Technologies](#technologies)
- [Project Status](#project-status)
- [External Resources](#external-resources)

## How to use Recommenda

1. Sign up using an email address
2. Login using your email address and password
3. Go to you profile, and click "following"
4. Enter the email address of a friend using Recommenda
5. You will now see their name under "following"
6. Your friend can now send you recommendations
7. To send your friends recommendations, tell them to follow you!

## User interface

![Image of the books recommended to the user](/assets/books.jpg)
![Image of the films recommended by the user](/assets/films.jpg)
![Image of the user's profile and thier followers](/assets/followers.jpg)

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
  _For a complete list, see `requirements.txt`_

### APIs

- Books: [Google Books API](https://developers.google.com/books/docs/v1/using)
- Films: [The Movie Database API](https://developers.themoviedb.org/3/getting-started/introduction)
- Music: [Spotify API](https://developer.spotify.com/documentation/web-api/)
- Podcasts: tbc
- Articles: tbc

## Project status

This project is still in development. There are several features that are scheduled to be implemented before the app is complete, as well as several features that are not strictly necessary, but will improve the user experience.

### Features to complete

- Media types of podcasts, music and articles

### Features for UX

- Allow users to recommend items to themselves

## External resources
