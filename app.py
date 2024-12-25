from flask import Flask, request, jsonify, send_file
import os
import pandas as pd
from Good_Script_XLXInput_Calcukate import get_dividend_data, save_to_excel  # Import your functions

app = Flask(__name__)

# Route to handle file upload and process it
@app.route('/process', methods=['POST'])
def process_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        # Save the uploaded file
        input_file = os.path.join("uploads", file.filename)
        os.makedirs("uploads", exist_ok=True)
        file.save(input_file)

        # Read input file
        stock_data = pd.read_excel(input_file, usecols=["Stock Name", "Number of Stocks"])
        stock_data = stock_data.dropna(subset=["Stock Name", "Number of Stocks"])
        stock_data["Number of Stocks"] = pd.to_numeric(stock_data["Number of Stocks"], errors="coerce").fillna(0).astype(int)
        stock_data = stock_data[stock_data["Number of Stocks"] > 0]

        stocks = stock_data["Stock Name"].tolist()
        num_stocks = stock_data["Number of Stocks"].tolist()

        # Process dividend data
        dividend_data = []
        for stock, num in zip(stocks, num_stocks):
            data = get_dividend_data(stock, num)
            dividend_data.append(data)

        # Save to output file
        output_file = os.path.join("uploads", "Dividend_Tracker.xlsx")
        save_to_excel(dividend_data, output_file)

        return send_file(output_file, as_attachment=True)

    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

if __name__ == "__main__":
    app.run(debug=True)
