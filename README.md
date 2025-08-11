# 📸 ImageLab - https://image-lab-alpha.vercel.app/

ImageLab is a **full-stack image editing and processing platform** built using **Python (FastAPI)** on the backend and **Next.js (React + TypeScript)** on the frontend.  
It originated as a **command-line BMP image editor** for *CS150 at Northwestern University* — but after the course ended, it was completely reimagined into a **modern, web-based, cloud-deployed application** with an expanded feature set, polished UI, and full Dockerization.

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
- Green Shift & Blue Shift  
- Negative (invert colors)  
- Sepia Filter  
- Rotate 
- Pixelate  
- AI Image Generation (transform existing images using text prompts)  
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
- **Hugging Face** - AI Image Generation
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
final_project/
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

1️⃣ **Clone the repository**  
```bash
git clone git@github.com:jayrao213/ImageLab.git
cd ImageLab
```

2️⃣ **Start with Docker**  
```bash
docker compose up --build
```

3️⃣ **Access the app**  
- Frontend: **http://localhost:3000**  
- Backend API: **http://localhost:8000**  

---

## 🌐 Deployment

The project is deployed in two parts:
- **Backend API** → [Render](https://render.com) (Docker container)  
- **Frontend** → [Vercel](https://vercel.com) (Next.js hosting)  

---

## 📜 Author

**Jay Rao**  
