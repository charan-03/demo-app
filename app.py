import os
from flask import Flask, render_template, request, redirect, url_for, flash
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)
app.secret_key = os.urandom(24) # Needed for flash messages

APP_VERSION = "1.0.0"

# Initialize Firestore
try:
    # Use a service account
    # The path to your service account key file
    # For local development, place serviceAccountKey.json in the same directory as app.py
    # For deployment, consider environment variables or other secure methods
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
except Exception as e:
    print(f"Error initializing Firebase: {e}")
    print("Please ensure 'serviceAccountKey.json' is present and valid, or Firebase is initialized correctly.")
    db = None # Set db to None if initialization fails

@app.route('/')
def index():
    notes = []
    if db:
        try:
            # Fetch document ID along with data
            notes_ref = db.collection('notes').order_by('timestamp', direction=firestore.Query.DESCENDING).stream()
            notes = []
            for doc in notes_ref:
                note_data = doc.to_dict()
                note_data['id'] = doc.id  # Add the document ID to the note dictionary
                notes.append(note_data)
        except Exception as e:
            flash(f"Error fetching notes: {e}", "error")
            print(f"Error fetching notes: {e}")
    else:
        flash("Firestore is not initialized. Please check your setup.", "error")
    return render_template('index.html', notes=notes, app_version=APP_VERSION)

@app.route('/add_note', methods=['POST'])
def add_note():
    if not db:
        flash("Firestore is not initialized.", "error")
        return redirect(url_for('index'))

    title = request.form['title']
    content = request.form['content']
    if title and content:
        try:
            db.collection('notes').add({
                'title': title,
                'content': content,
                'timestamp': firestore.SERVER_TIMESTAMP
            })
            flash("Note added successfully!", "success")
        except Exception as e:
            flash(f"Error adding note: {e}", "error")
            print(f"Error adding note: {e}")
    else:
        flash("Title and content cannot be empty.", "error")
    return redirect(url_for('index'))

@app.route('/edit_note/<string:note_id>', methods=['GET', 'POST'])
def edit_note(note_id):
    if not db:
        flash("Firestore is not initialized.", "error")
        return redirect(url_for('index'))

    note_ref = db.collection('notes').document(note_id)

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        if title and content:
            try:
                note_ref.update({
                    'title': title,
                    'content': content,
                    'timestamp': firestore.SERVER_TIMESTAMP
                })
                flash("Note updated successfully!", "success")
            except Exception as e:
                flash(f"Error updating note: {e}", "error")
                print(f"Error updating note: {e}")
        else:
            flash("Title and content cannot be empty.", "error")
        return redirect(url_for('index'))
    else: # GET request
        try:
            note = note_ref.get()
            if note.exists:
                note_data = note.to_dict()
                note_data['id'] = note.id
                return render_template('edit.html', note=note_data, app_version=APP_VERSION)
            else:
                flash("Note not found.", "error")
        except Exception as e:
            flash(f"Error fetching note for editing: {e}", "error")
            print(f"Error fetching note for editing: {e}")
        return redirect(url_for('index'))

@app.route('/delete_note/<string:note_id>', methods=['POST'])
def delete_note(note_id):
    if not db:
        flash("Firestore is not initialized.", "error")
        return redirect(url_for('index'))

    try:
        db.collection('notes').document(note_id).delete()
        flash("Note deleted successfully!", "success")
    except Exception as e:
        flash(f"Error deleting note: {e}", "error")
        print(f"Error deleting note: {e}")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)