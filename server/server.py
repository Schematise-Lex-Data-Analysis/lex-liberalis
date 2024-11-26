from flask import Flask, request, jsonify
from flask_cors import CORS 
import os

app = Flask(__name__)  
CORS(app)

# Directory to store files
BASE_DIRECTORY = os.path.join(os.getcwd(), "preview")

# Ensure the preview directory exists
os.makedirs(BASE_DIRECTORY, exist_ok=True)

@app.route('/api/savefile/preview', methods=['POST'])
def save_file():
    try:
        # Get the folder name from the request
        folder_name = request.form.get('folderName')
        file = request.files.get('file')
            
        if not folder_name or not file:
            return jsonify({"error": "Folder name or file is missing"}), 400

        # Create a subdirectory inside 'preview' for the folder name
        folder_path = os.path.join(BASE_DIRECTORY, folder_name)
        os.makedirs(folder_path, exist_ok=True)

        # Save the file to the folder
        file_path = os.path.join(folder_path, file.filename)
        file.save(file_path)

        return jsonify({"message": "File uploaded successfully", "file_path": file_path}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/deletefile', methods=['DELETE'])
def delete_file():
    try:
        data = request.get_json()
        folder_name = data.get('folderName')
        file_name = data.get('fileName')

        if not folder_name or not file_name:
            return jsonify({"error": "Folder name or file name is missing"}), 400

        # Construct file path
        folder_path = os.path.join(BASE_DIRECTORY, folder_name)
        file_path = os.path.join(folder_path, file_name)

        # Check if file exists and delete
        if os.path.exists(file_path):
            os.remove(file_path)
            return jsonify({"message": "File deleted successfully"}), 200
        else:
            return jsonify({"error": "File not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':  
    app.run(debug=True)
