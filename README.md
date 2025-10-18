# TalkAI - Hinglish Text-to-Speech

A self-hosted Text-to-Speech application that supports mixed Hindi and English (Hinglish) using Coqui XTTS v2.

## Features

- Mixed Hindi (Devanagari) and English text support
- Automatic language detection and segmentation
- Adjustable speech speed and pause duration
- Audio download as MP3
- Self-hosted with open-source models
- No external API dependencies

## Tech Stack

### Backend
- **Python 3.11** with FastAPI
- **Coqui TTS** (XTTS v2) - Multilingual text-to-speech
- **PyTorch** - Deep learning framework
- **pydub** - Audio processing
- **ffmpeg** - Audio encoding

### Frontend
- **React 18** with TypeScript
- **Vite** - Build tool
- **Node.js 22+**

## Local Development

### Prerequisites
- Python 3.11
- Node.js 22+
- ffmpeg

### Backend Setup

1. Navigate to the server directory:
   ```bash
   cd server
   ```

2. Create a virtual environment with Python 3.11:
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Pre-download the TTS model (optional but recommended):
   ```bash
   python download_model.py
   ```

5. Run the backend server:
   ```bash
   uvicorn app:app --reload --port 8000
   ```

The backend will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```

The frontend will be available at `http://localhost:5173`

## Deployment to Render

### Prerequisites
- A GitHub account
- A Render account (free tier available)

### Deployment Steps

#### 1. Push to GitHub

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: TalkAI Hinglish TTS"

# Add your GitHub repository as remote
git remote add origin https://github.com/YOUR_USERNAME/TalkAI.git

# Push to GitHub
git push -u origin main
```

#### 2. Deploy on Render

**Option A: Using render.yaml (Recommended)**

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New" → "Blueprint"
3. Connect your GitHub repository
4. Render will automatically detect the `render.yaml` file and create both services:
   - Backend API (Docker service)
   - Frontend Static Site

**Option B: Manual Setup**

**Backend:**
1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - Name: `talkai-backend`
   - Runtime: `Docker`
   - Dockerfile Path: `./server/Dockerfile`
   - Docker Context: `./server`
   - Plan: `Standard` (or `Starter` for lower cost)
   - Environment Variables:
     - `COQUI_TOS_AGREED=1`
     - `PORT=8000`

**Frontend:**
1. Click "New" → "Static Site"
2. Connect your GitHub repository
3. Configure:
   - Name: `talkai-frontend`
   - Build Command: `cd frontend && npm install && npm run build`
   - Publish Directory: `./frontend/dist`
   - Environment Variables:
     - `VITE_API_BASE=<your-backend-url>` (Get this from backend service)

#### 3. Set Up GitHub Actions (Optional)

1. Go to your Render Dashboard → Account Settings → API Keys
2. Create a new API key
3. Go to your GitHub repository → Settings → Secrets and variables → Actions
4. Add two secrets:
   - `RENDER_API_KEY`: Your Render API key
   - `RENDER_SERVICE_ID`: Your backend service ID (found in Render dashboard URL)

Now every push to `main` branch will automatically trigger a deployment!

## Important Notes

### Performance
- First request may take 20-30 seconds as the model loads
- CPU processing is slow (20-47 seconds per segment)
- For better performance, consider upgrading to GPU instances on Render

### Coqui TTS License
This project uses Coqui TTS which is licensed under the Coqui Public Model License (CPML).
- Non-commercial use is free
- Commercial use requires a license
- See: https://coqui.ai/cpml

### Model Size
- The XTTS v2 model is approximately 1.87GB
- First deployment will take longer as it downloads the model
- The Dockerfile pre-downloads the model during build time

### Known Limitations
- Hindi audio quality may vary depending on the speaker voice
- Processing is CPU-intensive and slow
- Limited to text input (no SSML support)

## Troubleshooting

### Backend Issues
- **Model download fails**: Ensure `COQUI_TOS_AGREED=1` is set
- **ffmpeg errors**: Make sure ffmpeg is installed and accessible
- **Out of memory**: Reduce batch size or upgrade server resources

### Frontend Issues
- **CORS errors**: Ensure backend URL is correctly set in `VITE_API_BASE`
- **Build fails**: Make sure Node.js version is 22+

### Deployment Issues
- **Render build timeout**: Model download may take time, be patient
- **Health check fails**: Increase health check start period in render.yaml

## API Documentation

### Endpoints

**GET `/health`**
- Health check endpoint
- Returns: `{"status": "ok"}`

**POST `/segments`**
- Preview text segmentation
- Body: `{"text": "string", "speed": 1.0, "pause_ms": 160}`
- Returns: `{"segments": [{"text": "...", "lang": "en|hi"}]}`

**POST `/tts`**
- Generate speech audio
- Body: `{"text": "string", "speed": 1.0, "pause_ms": 160}`
- Returns: MP3 audio file

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License. However, note that Coqui TTS has its own licensing terms (CPML).
