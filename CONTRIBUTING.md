# Contributing to Lottery Full Backend

Thank you for your interest in contributing to the Lottery Full Backend for Railway!

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git

### Initial Setup

If you're starting fresh with this project:

1. **Clone the repository**
   ```bash
   git clone https://github.com/louismoro28-svg/Lottery-full-backend-for-railway.git
   cd Lottery-full-backend-for-railway
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   export API_KEY=mysecretkey123
   ```
   Or create a `.env` file (make sure it's in .gitignore):
   ```
   API_KEY=mysecretkey123
   ```

4. **Run the application locally**
   ```bash
   python app.py
   ```
   The server will start on `http://localhost:8080`

## Creating a New Repository from This Code

If you want to create your own version of this backend:

1. **Download/unzip the code**

2. **Initialize a new git repository**
   ```bash
   cd Lottery-full-backend-for-railway
   git init
   git add .
   git commit -m "Initial commit: Lottery backend"
   ```

3. **Create an empty repository on GitHub**
   - Go to GitHub and create a new empty repository

4. **Connect and push to your repository**
   ```bash
   git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
   git branch -M main
   git push -u origin main
   ```

## Making Changes

### Workflow

1. **Create a new branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Edit code as needed
   - Test your changes locally

3. **Commit your changes**
   ```bash
   git add .
   git commit -m "Description of your changes"
   ```

4. **Push to GitHub**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create a Pull Request**
   - Go to GitHub and create a PR from your branch

## Testing

Before submitting a PR, test the endpoints:

```bash
# Health check
curl http://localhost:8080/health

# Test with API key
curl "http://localhost:8080/predictions?key=mysecretkey123"
```

## Code Style

- Follow PEP 8 style guidelines for Python code
- Use meaningful variable and function names
- Add comments for complex logic
- Keep functions focused and single-purpose

## Questions?

If you have questions about contributing, feel free to open an issue on GitHub.
