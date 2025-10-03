# 📸 ImageLab - https://image-lab-alpha.vercel.app/

ImageLab is a **full-stack image editing and processing platform** built using **Python (FastAPI)** on the backend and **Next.js (React + TypeScript)** on the frontend.  
It originated as a **command-line BMP image editor** for *CS150 at Northwestern University* — but after the course ended, it was completely reimagined into a **modern, web-based, cloud-deployed application** with an expanded feature set, polished UI, and full Dockerization.

**Note on Live Performance**: The live demo sometimes fails or runs out of memory because it's hosted entirely on free tiers (Render, Hugging Face, Vercel) with very limited RAM, no GPU, and cold starts. You can clone the repo and run it locally for much faster and more reliable performance.

**Note on Repository History:** This repo's commit history is structured to demonstrate the project's evolution rather than reflect real-time development. The commits are organized chronologically to show: (1) the original CS150 command-line project, (2) backend expansion with FastAPI, new image functions, and Pillow integration, (3) full Next.js/React frontend implementation, and (4) complete Dockerization of both services and deployment configuration.

---

## 📖 Project History

The **original CS150 final project** was a purely Python-based program that ran in the terminal and only worked with **BMP** image files.  
It supported the following functions:
- **Add Color**
- **Red Shift**
- **Shift Brightness**
- **Make Monochrome**
- **Mirror Horizontal**
- **Mirror Vertical**
- **Tile**
- **Blur**

After the course, I took the foundational logic and:
1. **Rebuilt the backend** into a modern REST API with FastAPI.
2. **Rewrote** the old BMP-only `util.py` to use **Pillow**, enabling support for **all major image formats** (PNG, JPG, WebP, etc.).
3. **Expanded functionality** with entirely new image transformations.
4. **Created a full frontend** in React + Next.js for a smooth, interactive experience.
5. **Dockerized** both frontend & backend for easy deployment.
6. **Deployed** the backend to Render and frontend to Vercel.

---

## ✨ Features

### 🖼️ Original CS150 Functions I created
- Add Color  
- Red Shift  
- Shift Brightness  
- Make Monochrome  
- Mirror Horizontal  
- Mirror Vertical  
- Tile  
- Blur  

### 🚀 New Features I Added
- AI Image Generation  
- Resize Dimensions
- Green Shift & Blue Shift  
- Negative (invert colors)  
- Sepia Filter  
- Rotate 
- Pixelate  
- Multi-format download (PNG, JPG, WEBP, BMP)  
- Full support for **all image types** via Pillow  
- Optimized and clean API endpoints  
- Fully interactive **web interface**  

---

## 🛠️ Tech Stack

### Backend
- **Python 3**  
- **FastAPI** – REST API framework  
- **Pillow (PIL)** – Image manipulation library  
- **Pollinations.AI** - AI Image Generation
- **Docker** – Containerization for consistent environments  

### Frontend
- **Next.js (React + TypeScript)** – Modern React framework  
- **TailwindCSS** – Utility-first CSS for rapid UI development  

### Deployment
- **Render** – Backend hosting (Docker-based)  
- **Vercel** – Frontend hosting (Next.js static hosting)  

---

## 📂 Project Structure

```
ImageLab/
│
├── backend/              # FastAPI server and image processing logic
│   ├── api.py
│   ├── image.py
│   ├── pixel.py
│   ├── util.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .gitignore
│
├── frontend/             # Next.js (React + TypeScript) UI
│   ├── src/app/page.tsx
│   ├── Dockerfile
│   ├── package.json
│   └── ...
│
├── docker-compose.yml    # Orchestration for frontend & backend
└── README.md
```

---

## 🚀 Running Locally

### Option 1: Using Docker (Recommended)

1️⃣ **Clone the repository**  
```bash
git clone git@github.com:jayrao213/ImageLab.git
cd ImageLab
```

2️⃣ **Install Docker**
- Install [Docker Desktop](https://www.docker.com/products/docker-desktop) for your OS
- Make sure Docker is running

3️⃣ **Start with Docker Compose**  
```bash
docker compose up --build
```

4️⃣ **Access the app**  
- Frontend: **http://localhost:3000**  
- Backend API: **http://localhost:8000**  

5️⃣ **Stop the containers**
```bash
docker compose down
```

---

### Option 2: Manual Setup (Without Docker)

#### Prerequisites
**Backend:**
- Python 3.8+
- pip

**Frontend:**
- Node.js 18+
- npm or yarn

#### Backend Setup

1️⃣ **Navigate to backend directory**
```bash
cd backend
```

2️⃣ **Create a virtual environment**
```bash
python3 -m venv venv
```

3️⃣ **Activate the virtual environment**
```bash
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

4️⃣ **Install dependencies**
```bash
pip install -r requirements.txt
```

5️⃣ **Run the backend server**
```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

Backend will be running at **http://localhost:8000**

---

#### Frontend Setup

1️⃣ **Open a new terminal and navigate to frontend directory**
```bash
cd frontend
```

2️⃣ **Install Node.js** (if not already installed)
- Download and install [Node.js](https://nodejs.org/) (v18 or higher recommended)
- Verify installation:
```bash
node --version
npm --version
```

3️⃣ **Install dependencies**
```bash
npm install
```

4️⃣ **Run the development server**
```bash
npm run dev
```

Frontend will be running at **http://localhost:3000**

---

## 🌐 Deployment

The project is deployed in two parts:
- **Backend API** → [Render](https://render.com) (Docker container)  
- **Frontend** → [Vercel](https://vercel.com) (Next.js hosting)  

---

## 📜 Author

**Jay Rao**