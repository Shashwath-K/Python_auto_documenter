<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a id="readme-top"></a>

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/Shashwath-K/Python_auto_documenter">
    <img src="images\autodoc_logo.png" alt="Logo" width="120" height="120">
  </a>

  <h3 align="center">AutoDoc AI</h3>

  <p align="center">
    A Semantic-Aware File Converter and Documentation Engine powered by Local LLMs.
    <br />
    <a href="https://github.com/Shashwath-K/Python_auto_documenter"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="http://127.0.0.1:8000">View Demo</a>
    &middot;
    <a href="https://github.com/Shashwath-K/Python_auto_documenter/issues">Report Bug</a>
    &middot;
    <a href="https://github.com/Shashwath-K/Python_auto_documenter/issues">Request Feature</a>
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## About The Project

AutoDoc AI is a sophisticated automation platform designed to bridge the gap between complex source code and professional documentation. By leveraging local Large Language Models (via Ollama), it provides real-time intelligent code analysis, automated docstring generation, and high-fidelity project reporting.

### Key Features:
* **Live Generation Editor**: Type code and watch as the AI contextually understands and documents your functions and classes in real-time.
* **Repository Processing**: Upload an entire project as a ZIP file. The system scans the codebase, analyzes every module, and generates a fully documented version.
* **Semantic-Aware Conversion**: Convert raw source code or notebooks into professional, themed PDF and DOCX reports with automated AI summaries.
* **RPA-Powered "Ghost Typing"**: Experience documentation being typed directly into your editor using background automation.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Built With

This project is built using a powerful stack of modern web and automation technologies:

* [![FastAPI][FastAPI]][FastAPI-url]
* [![Python][Python]][Python-url]
* [![Ollama][Ollama]][Ollama-url]
* [![Jinja2][Jinja2]][Jinja2-url]
* [![ReportLab][ReportLab]][ReportLab-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running, follow these simple steps.

### Prerequisites

* **Python 3.10+**
* **Ollama** (Running locally with `llama3.2` or equivalent)
  ```sh
  ollama run llama3.2
  ```

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/Shashwath-K/Python_auto_documenter.git
   ```
2. Create and activate a virtual environment
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. Install dependencies
   ```sh
   pip install -r requirements.txt
   ```
4. Run the application
   ```sh
   uvicorn app.main:app --reload
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- USAGE EXAMPLES -->
## Usage

### 1. Landing Page
The central hub where you can choose between different automation modes: Live Editor, Upload Mode, or Repository Mode.
![Landing Screenshot][landing-screenshot]

### 2. Live Generation Editor
The most powerful mode for developers. It features a real-time editor that identifies "undocumented" items and offers one-click AI generation.
![Live Editor Screenshot][live-screenshot]

### 3. Repository Mode
Process entire codebases at once. Download a documented version of your project in seconds.
![Repo Mode Screenshot][repo-screenshot]

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- ROADMAP -->
## Roadmap

- [x] Initial release of Live Editor
- [x] ZIP Repository Processing
- [x] PDF/DOCX Export with AI Summary
- [ ] Multi-model LLM support (OpenAI, Anthropic)
- [ ] Direct VS Code Plugin Integration
- [ ] GitHub Actions for automated documentation on PRs

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- LICENSE -->
## License

Distributed under the Unlicense License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTACT -->
## Contact

Shashwath K - [@shashwath_k15](https://twitter.com/shashwath_k15) - [Email](shashwathkukkunoor@outlook.com)

Project Link: [https://github.com/Shashwath-K/Python_auto_documenter](https://github.com/Shashwath-K/Python_auto_documenter)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* [Ollama](https://ollama.com) for local LLM inferencing
* [FastAPI](https://fastapi.tiangolo.com/) for the high-performance backend
* [ReportLab](https://www.reportlab.com/) for PDF generation
* [Best-README-Template](https://github.com/othneildrew/Best-README-Template)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
[landing-screenshot]:https://github.com/Shashwath-K/Python_auto_documenter/blob/main/images/landing_page.png
[live-screenshot]: https://github.com/Shashwath-K/Python_auto_documenter/blob/main/images/live_mode.png
[repo-screenshot]: https://github.com/Shashwath-K/Python_auto_documenter/blob/main/images/repo_mode.png

[FastAPI]: https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi
[FastAPI-url]: https://fastapi.tiangolo.com/
[Python]: https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white
[Python-url]: https://www.python.org/
[Ollama]: https://img.shields.io/badge/Ollama-000000?style=for-the-badge&logo=ollama&logoColor=white
[Ollama-url]: https://ollama.com/
[Jinja2]: https://img.shields.io/badge/Jinja2-B41717?style=for-the-badge&logo=jinja&logoColor=white
[Jinja2-url]: https://jinja.palletsprojects.com/
[ReportLab]: https://img.shields.io/badge/ReportLab-FFD43B?style=for-the-badge&logo=pypi&logoColor=blue
[ReportLab-url]: https://www.reportlab.com/
