# Data cleaning
[TBD]

# API
## How to start the server
- Clone the repo `git clone https://github.com/elkuradusenge/urban-mobility-assignment.git`
- Change the directory `cd server`
- With Node.js installed, install all the packages with `npm install`
- Run `node server.js` to start the server at `http://localhost:3000`
- On server start up the database will be initiated with tables and seed data. To demonstrate make a GET HTTP request to `/locations` to retrieve all locations in the database
- We are using `SQLite` as the database

## Running the web client
- The server should already be running.
- Open `index.html` at `client/index.html` in your browser. The app should open at `http://localhost:63343/urban-mobility-assignment/client/index.html?_ijt=ce92ti2vjk2obnld80msrb3ntm&_ij_reload=RELOAD_ON_SAVE`

## File structure
- Data cleaning is handled in `data` directory with Python
- The API will be built in the `server` directory with Node.js
- The web app will go in `client` directory with vanilla HTML, CSS and JavaScript

```markdown
│── client/
│   ├── assets/
│   │   ├── css # This is where we have our stylesheets
│   │   └── js # This is where we have our JavaScript files
│   ├── components # Containes components like header, navbar,...
│   └── index.html # This is the main entry file for the client. Other navigation pages are at the root of client as well
├── data/
│   ├── clean_data # Contains cleaned CSV files
│   └── raw_data # Contains uncleaned CSV files
├── server/
│   ├── src/
│   │   ├── config # For configurations like Swagger
│   │   ├── db # For configuring SQLite database
│   │   ├── docs # For documentations
│   │   ├── repository # For talking to the database
│   │   ├── routes # For configuring routes
│   │   ├── services # Handling business logi
│   │   ├── utils # Helper functions
│   │   └── server.js # Main entry point of the server
│   └── package.json # For managing dependencies
├── .gitignore # For files we don't need to push
└── README.md # For basic documentation such as set up
```

## Important links
- Link to YouTube video: TBD
- [Team participation sheet]( https://docs.google.com/spreadsheets/d/11-xA8QXkXfPswp3CypwRaMWXdrGt6T2iPRYr3ock8tI/edit?usp=sharing)