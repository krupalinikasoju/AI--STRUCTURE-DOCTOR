# Structure Doctor AI — Streamlit project

This app follows the supplied 7-step reference workflow:
1. Project inputs
2. Image processing
3. Crack image review overlay
4. Crack pattern and measured dimensions
5. Structural assessment summary
6. Repair and safety guidance
7. Final inspection report with PDF export

## Important limitation
The red overlay is an image-edge visualization, not a trained AI crack detector. It can highlight texture, joints, shadows and stains. Crack width and length are entered by the user based on site measurements. The app does not provide a numeric remaining-safe-life estimate because a photo alone cannot support a defensible estimate. A qualified structural engineer must inspect the building and consider crack history, movement, materials, loading, member details and foundation conditions.

## Run on Windows
1. Install Python 3.10+ from https://www.python.org/downloads/
2. Extract this folder and open Command Prompt inside it.
3. Run:

```bat
py -m venv .venv
.venv\Scripts\activate
py -m pip install -r requirements.txt
streamlit run app.py
```

Open the local URL shown in the terminal, usually `http://localhost:8501`.

Python IDLE can edit the file, but Streamlit must be started from Command Prompt or a terminal.

## GitHub
Upload `app.py`, `requirements.txt`, and `README.md` to a GitHub repository. Deploy through https://share.streamlit.io/ by selecting the repository and setting the main file to `app.py`.

Do not upload private building photographs or sensitive site information to a public repository.
