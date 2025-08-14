# 🎬 MOVIE_RECOMMENDATION_AGENT

Welcome to the **Movie Recommendation Agent**!  
A Python-powered system that leverages database APIs and smart agents to fetch accurate movie data and provide personalized recommendations. 🍿🤖

---

## 🚀 Features

- **Intelligent Recommendations**: Get movie suggestions based on your preferences and search history.
- **API Integration**: Fetches up-to-date and accurate movie data from online databases.
- **Agent-Based Architecture**: Utilizes smart agents for efficient data retrieval and recommendation logic.
- **Easy to Use**: Simple interface via `Main.py` and modular code in the `app/` folder.
- **Docker-Ready**: Includes `Dockerfile` and `.dockerignore` for seamless containerization.
- **Customizable**: Easily adapt or extend for your own databases or recommendation logic.

---

## 📁 Repository Structure

```
.
├── Main.py               # Entry point for the agent system
├── app/                  # Core application code and modules
├── requirements.txt      # Python dependencies
├── Dockerfile            # Docker build configuration
├── .dockerignore         # Files ignored in Docker build
├── .gitignore            # Git ignored files
└── README.md             # Project documentation
```

---

## 🏁 Getting Started

### **Run Locally**

1. **Clone the repo**
   ```bash
   git clone https://github.com/Rishabh-Sharma-12/MOVIE_RECOMMENDATION_AGENT.git
   cd MOVIE_RECOMMENDATION_AGENT
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the agent**
   ```bash
   python Main.py
   ```

---

### **Run with Docker**

You can either build the image locally or pull it directly from Docker Hub.

#### **Pull from Docker Hub**
```bash
docker pull <your-dockerhub-username>/movie-recommendation-agent:latest
docker run -it --rm <your-dockerhub-username>/movie-recommendation-agent
```

#### **Build Locally**
```bash
docker build -t movie-recommendation-agent .
docker run -it --rm movie-recommendation-agent
```

---

## 🔑 Environment Variables

This project uses a `.env` file for API keys and configuration.

**Example `.env` file:**
```ini
TMDB_API_KEY=your_tmdb_api_key
OMDB_API_KEY=your_omdb_api_key
```

When using Docker, pass the `.env` file:
```bash
docker run --env-file .env movie-recommendation-agent
```

---

## 🛠️ Technologies Used

- Python (97.1%)
- CSS (2.9%)
- Docker for containerization

---

## 📚 How it Works

- The main logic is in `Main.py`, which orchestrates the agents and API calls.
- The `app/` folder contains supporting modules and features for the recommendation engine.
- Docker support makes deployment simple and portable across environments.
- Customize or extend the agent logic as needed to plug in more APIs or refine recommendations.

---

## 🤝 Contributing

Feel free to fork the repository, open issues, or submit pull requests!  
Whether you're fixing bugs or adding new features, contributions are welcome. 🙌

---

⭐️ If you like this project, give it a star and try running it with Docker! 🚢
