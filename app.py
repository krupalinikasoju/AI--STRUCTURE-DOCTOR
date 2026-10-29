# Structure Doctor AI

A Streamlit prototype for building condition screening, preliminary RCC
load estimation, crack image review, and combined PDF reporting.

## Features
- Building type and number-of-floors inputs
- Preliminary RCC load estimates using explicit assumptions
- Building/crack image upload and enhancement
- Edge-visualization overlay
- Crack measurement and screening
- Preliminary inspection and safety guidance
- Combined PDF report

## Run locally

Install Python, then run:

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Limitations

This is an engineering prototype. Load values use assumed floor areas
and loads; the image overlay is not a trained AI crack detector.
It does not replace structural analysis or inspection by a qualified
structural engineer.
