from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_socketio import SocketIO, emit
from scraper import process_queries  # Adjust import as necessary
import asyncio

app = Flask(__name__)
socketio = SocketIO(app, async_mode="threading")

# Home page route
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        query = request.form.get("query")
        location = request.form.get("location")
        if not query or not location:
            return render_template("index.html", error="Both inputs are required.")
        return redirect(url_for("scrape", query=query, location=location))
    return render_template("index.html")

# Route to scrape and display results in real-time
@app.route("/scrape/<query>/<location>")
def scrape(query, location):
    return render_template("results.html", query=query, location=location)

@socketio.on("start_scrape")
def handle_scrape(data):
    query = data["query"]
    location = data["location"]

    async def scrape_and_emit():
        results = await process_queries([query], [location])  # Asynchronous scraping
        
        # Gather only emails
        emails = []
        for result in results:
            emails.extend(result["emails"])  # Collect all emails into a single list
        
        # Emit each email to the client
        for email in emails:
            socketio.emit("update", {
                "email": email  # Emit email without prefix
            })
        
        # Send completion message
        socketio.emit("update", {"message": "Scraping complete"})
    
    asyncio.run(scrape_and_emit())

# Download route for concatenated email file
@app.route("/download/<query>/<location>")
def download(query, location):
    # The download functionality has been removed since no database is being used.
    return jsonify({"error": "Download functionality has been removed."}), 404

if __name__ == "__main__":
    socketio.run(app, debug=True)
