# F1 Leaderboard Predictor Pro 🏎️

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://f1-predictor-2026.streamlit.app)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> **Real-time F1 race prediction using weighted scoring and circuit-specific analytics**

## Live Demo

**https://f1-predictor-2026.streamlit.app**

## Features

### Smart Prediction Engine
- **Weighted scoring model** (70% grid position + 30% points history)
- **Circuit-specific adjustments** for tracks like Monaco, Monza, and Singapore
- **Real-time confidence scoring** based on prediction reliability
- **Interactive weight sliders** to tune the model yourself

### Interactive Visualisations
- Grid position vs final position scatter plots with trendlines
- Points distribution pie charts
- Performance trend analysis
- Head-to-head prediction comparisons

### Race Analysis
- Track overtaking statistics (best gainers/losers)
- Constructor/team performance tracking
- Position change analysis
- Top 3 prediction accuracy metrics

### User Controls
- Adjust prediction weights in real-time
- Toggle circuit factor on/off
- Select any F1 season (2022-2025)
- View confidence scores

## Tech Stack

| Category | Technology |
|----------|------------|
| **Frontend** | Streamlit |
| **Data Processing** | Pandas |
| **Visualisation** | Plotly |
| **Statistics** | Statsmodels |
| **API** | Ergast F1 API |
| **Language** | Python 3.13+ |

## Quick Start

### Prerequisites

- Python 3.13 or higher
- Git (optional)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/zahra-ali-jaffer/f1-predictor.git
cd f1-predictor
```

2. **Create virtual environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the app**
```bash
streamlit run app.py
```

5. **Open your browser** to `http://localhost:8501`

## Dependencies

```
streamlit>=1.28.0
pandas>=2.0.0
requests>=2.31.0
plotly>=5.17.0
statsmodels>=0.14.0
```

## How It Works

### The Prediction Model

The prediction score for each driver is calculated as:

```
Score = -(Grid_Weight × Grid_Position) - (Points_Weight × Championship_Points)
```

Where:
- **Grid_Weight** = 0.7 (default, adjustable)
- **Points_Weight** = 0.3 (default, adjustable)

### Circuit Adjustments

Different tracks favor different strategies:

| Track Type | Tracks | Adjustment |
|------------|--------|------------|
| **Hard to Overtake** | Monaco, Singapore, Hungary, Imola | Grid weight ↑ to 0.9 |
| **Easy to Overtake** | Monza, Baku, Spa, Bahrain | Points weight ↑ to 0.5 |

### Confidence Score

The app calculates prediction confidence based on:
- Grid position variance
- Historical accuracy
- Circuit complexity

## Accuracy Metrics

The app tracks:
- **Top 3 Accuracy** - How often the podium is predicted correctly
- **Mean Position Error** - Average difference between predicted and actual positions
- **Exact Matches** - Number of drivers in the exact predicted position

## Acknowledgments

- **Data Source**: [Ergast F1 API](http://ergast.com/mrd/) - Free and open F1 data
- **Framework**: [Streamlit](https://streamlit.io/) - Turns Python scripts into web apps
- **Visualisation**: [Plotly](https://plotly.com/) - Interactive charts

## Contact

Project Link: [https://github.com/zahra-ali-jaffer/f1-predictor](https://github.com/zahra-ali-jaffer/f1-predictor)

## Screenshots
![1](https://github.com/user-attachments/assets/f9df7933-1de3-4c7c-8060-922b5cc4642c)
![2](https://github.com/user-attachments/assets/eba62586-9b64-47a7-a33d-cc246816ef19)
![3](https://github.com/user-attachments/assets/05b1395e-5726-4ccc-9fe7-96a8af6670db)
![4](https://github.com/user-attachments/assets/10dac10e-5e7e-4324-adbd-a2a689643f38)
![4](https://github.com/user-attachments/assets/10dac10e-5e7e-4324-adbd-a2a689643f38)
![5](https://github.com/user-attachments/assets/fd73ceb1-d027-496f-addc-ac26bd077128)
