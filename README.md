# System Design Architect Bot

A Streamlit-based AI chatbot that answers system design questions using context from a PDF book and Google Gemini models.

## What This Project Does

- Loads a system design book PDF into Google GenAI Files API.
- Uses the uploaded file as retrieval context for answers.
- Responds only as a system design expert with guardrails.
- Provides a chatbot-style UI with status chips, chat history, and response-precision control.
- Auto-selects a supported Gemini model to reduce model/version 404 errors.

## Key Features

- Book-grounded Q&A for architecture/scalability topics.
- Dynamic model selection from account-supported models.
- Streamlit chat interface with custom CSS styling.
- Adjustable response precision (`temperature` slider).
- One-click clear chat.

## Tech Stack

- Python
- Streamlit
- Google GenAI SDK (`google-genai`)
- Gemini models (`generate_content`)

## Project Structure

```text
system-design-bot/
├── app.py
├── requirements.txt
├── system_design_book.pdf
├── .gitignore
└── .env (optional/local only)
```

## How It Works

1. The app initializes a GenAI client with your API key.
2. It uploads `system_design_book.pdf` via `client.files.upload`.
3. It polls until file processing finishes.
4. It picks a supported model using `client.models.list()`.
5. User prompt + file context are sent to `client.models.generate_content`.
6. Response is shown in the chat UI and stored in `st.session_state`.

## Prerequisites

- Python 3.10+ (3.11/3.12 recommended)
- A valid Google AI API key
- Internet access for model/file API calls

## Local Setup

1. Clone repo

```bash
git clone https://github.com/<your-username>/system-design-bot.git
cd system-design-bot
```

2. Create and activate virtual environment

```bash
python -m venv env
env\Scripts\activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Add your API key

- Current code reads key directly from `app.py`:
- Edit `GOOGLE_API_KEY` in `app.py`.

5. Ensure PDF exists

- Keep `system_design_book.pdf` in project root.

6. Run app

```bash
streamlit run app.py
```

## Configuration

In `app.py`:

- `GOOGLE_API_KEY`: Google AI key (currently hardcoded).
- `PDF_PATH`: PDF file path used for context.
- `PREFERRED_MODELS`: model preference order.
- `temperature` slider: response precision/creativity.

## Deploy To Streamlit Community Cloud (Free)

1. Push code to GitHub.
2. Go to `https://share.streamlit.io`.
3. Create app from your repo and set main file to `app.py`.
4. Deploy.

Recommended for production:

- Do not keep key hardcoded in public repo.
- Use Streamlit Secrets instead:

```toml
GOOGLE_API_KEY="your_real_key"
```

If you migrate to secrets, update `app.py` key loading accordingly.

## Git Tips

- `.gitignore` already excludes `env/`, `.env`, and caches.
- If push fails with large pack/RPC issues, ensure virtualenv is not tracked.

## Troubleshooting

### 404 model not found

- Cause: unsupported model for your account/API route.
- Fix: keep dynamic model selection enabled (already implemented).
- Optional: update `PREFERRED_MODELS` to currently available models.

### PDF not found

- Ensure `system_design_book.pdf` is present in root.
- Or change `PDF_PATH` to correct relative path.

### Upload failed / processing failed

- Retry after a few minutes.
- Check key validity/quota/network.

### Text visibility/UI contrast issues

- Hard refresh browser (`Ctrl+Shift+R`).
- Clear Streamlit cache and rerun app.

### Streamlit deployment fails

- Confirm `requirements.txt` includes:
- `streamlit`
- `google-genai`

## Security Notes

- The API key is currently hardcoded in `app.py`.
- Rotate this key if it was ever committed publicly.
- Best practice for deployment: secrets manager (`st.secrets`) instead of hardcoding.

## Future Improvements

- Move auth to `st.secrets` + local `.env` fallback.
- Add conversation export/download.
- Add citations/snippets from source PDF in responses.
- Add multiple-book ingestion support.
- Add automated tests for model selection and UI state.

## Acknowledgements

- Built with Streamlit and Google Gemini APIs.
