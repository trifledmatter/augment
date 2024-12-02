# Augment

<p align="center">
Welcome to my little experiment in voice-driven AI. It listens, it talks, it tries its best. 
</p>

<p align="center">
Think of this as less of a polished product and more of a playground to see just how much we can squeeze out of voice recognition, AI models, and some duct tape.
</p>

---

## Table of Contents

- [About](#about)
- [Features](#features)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [To-Do List](#to-do-list)
- [Community](#community)
- [Contributing](#contributing)

---

## About

This project is a playground, not a polished product. It uses Vosk for speech-to-text, a conversational AI backend for generating responses, and pyttsx3 for its best attempt at sounding human. It’s ambitious, experimental, and probably a little overengineered.

What can it do? Well, it listens to you, tries to answer your questions, and eventually, it’ll be able to:

    Run system commands (like opening files or automating tasks).
    Handle tools and images dynamically.
    Switch between different operational modes (more on that below).

---

## Features

- **Speech Recognition**: Powered by [Vosk](https://alphacephei.com/vosk/), so it actually listens to you.
- **AI Conversations**: Talks back using a conversational AI backend. It’s like having a friend who knows everything… or at least pretends to.
- **Text-to-Speech**: Responds with synthesized audio, because typing is overrated.
- **(Planned) Modes for Every Mood**:
  - **Online**: No cache-checking nonsense, just generates answers on the fly.
  - **Data**: Tries to be smart—uses cached answers first, generates only if needed.
  - **Offline**: Refuses to generate anything new. Cache or bust.
- **Dynamic Context**: Adapts to tools, images, or whatever it needs to handle.
- **(Planned) System Commands**: Wants to run commands or automate apps, but we’re not there yet. One day, maybe.

---

## Getting Started

1. **Clone the repo**:

   ```bash
   git clone https://github.com/trifledmatter/augment.git
   cd augment
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up a Vosk model**:

   - Download one from [Vosk Models](https://alphacephei.com/vosk/models).
   - Unpack it into `src/models/`.

4. **Add your API key**:

   - Create a `.env` file in the project root:
     ```plaintext
     GROQ_SECRET_KEY=your_api_key_here
     ```

5. **Run it**:
   ```bash
   python src/main.py
   ```

---

## Project Structure

```
.
├── src/
│   ├── main.py               # The heart of the assistant
│   ├── speech.py             # Speech recognition and synthesis
│   ├── base.py               # Generative completion model lives here
│   ├── history.py            # Keep track of conversation history
│   ├── text.py               # Text formatting
│   ├── errors/               # Where custom errors live
│   └── models/               # Where vosk models live
├── requirements.txt          # The stuff you need to install
└── .env                      # Where the GROQ_API_KEY goes
```

---

## To-Do List

### Modes

- [ ] Implement **Online**, **Data**, and **Offline** modes.
- [ ] Make sure each mode actually works:
  - [ ] Online: Just generate without asking.
  - [ ] Data: Check cache first, then generate.
  - [ ] Offline: Use cache only, no funny business.

### Dynamic Context

- [ ] Automatically figure out when tools or images are involved.
- [ ] Integrate tools dynamically for tasks.
- [ ] Handle image inputs for vision-related queries.

### System Commands

- [ ] Add the ability to run system commands securely.
- [ ] Automate tasks like opening files or controlling apps.
- [ ] Make sure it doesn’t accidentally delete your hard drive.

### Miscellaneous

- [ ] Make the voice synthesis sound less like a robot.
- [ ] Add more voices because variety is fun.
- [ ] Improve caching and history management:
  - [ ] Add timestamps to cached answers.
  - [ ] Make history searchable.
- [ ] Build a simple web interface for configuration and logs.

---

## Community

This isn’t a serious product, but if you want to chat, contribute, or share ideas, feel free to reach out.

- **GitHub Discussions**: [Start a thread](https://github.com/trifledmatter/augment/discussions)

---

## Contributing

If you’re feeling brave enough to dive into this mess, here’s how you can help:

1. Fork the repo.
2. Create a branch:
   ```bash
   git checkout -b my-cool-feature
   ```
3. Make your changes and commit:
   ```bash
   git commit -m "Added something cool"
   ```
4. Push it:
   ```bash
   git push origin my-cool-feature
   ```
5. Open a pull request.
