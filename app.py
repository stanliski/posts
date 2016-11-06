from flask import Flask


app = Flask("Blog")
app.secret_key = "super secret!"
