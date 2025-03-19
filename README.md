# Character-Driven Novel Generation System

This is a modular novel generation system that uses LLMs (Large Language Models) to drive novel plot development with characters as the core focus. The system draws inspiration from the character traits and event trigger mechanisms of the CK3 game, gradually generating novel content through chapter progression and event triggers.

## Key Features

- **Character-Centric**: Detailed management of character traits, relationships, and states, driving plot development through character interactions
- **Event Engine**: Triggers events based on chapter progression, affecting character relationships and state changes
- **Structured Output**: Uses XML tags to ensure parsable output structure
- **High Controllability**: Provides a complete middleware system for easy modification/querying/editing of all elements
- **Modular Design**: Independent components, easy to customize and extend
- **Complete Storage System**: Supports saving novels in XML format for later loading and continued creation
- **Context Management**: Supports setting global and chapter-specific contexts to maintain novel coherence

## System Architecture

The system consists of the following core modules:

- **Core Components**: Data models, LLM interface, event engine, narrative generator
- **Middleware**: Character management, event management, outline management, chapter management, context management
- **Utility Library**: XML processing, file operations, logging system
- **User Interface**: Command line interface

## Installation and Setup

### Install Dependencies

```bash
pip install openai python-dotenv
```

### Configure API Key
1. Create a .env file in the project root directory
2. Add the following content:


## Usage
Run the main program:
```
python main.py
```


## Basic Workflow
1. Create a novel: Set title, genre, and background, with options to generate characters and outline
2. Manage characters: Manually create or generate characters, edit their traits and relationships
3. Manage events: Define events that might occur in the story
4. Manage outline: Plan the overall structure and key turning points of the novel
5. Generate chapters: Generate chapter content based on characters, events, and outline
6. Refine context: Add context information to ensure story coherence
7. Save and export: Save the novel in XML format or export as plain text


## Feature Menu
The main menu includes:
1. Create new novel
2. Load novel
3. Manage characters: View, create, generate, edit, delete characters and their relationships
4. Manage events: View, create, generate, edit, delete events
5. Manage outline: View, create, generate, edit outline and story arcs
6. Manage chapters: View, create, generate, edit, delete, regenerate chapters
7. Manage context: Edit global context and chapter-specific context
8. Save novel: Save the novel in XML format
9. Export novel: Export the novel as a readable text file
10. Settings: Modify LLM model and other configurations


## Customization and Extension

### Modify Prompt Templates
You can modify the prompt templates for various functions in config/prompts.py to adjust the style and content of generated results according to your needs.

### Add New Features
Based on the modular design, you can easily add new features:

1. Add new functions to the corresponding modules
2. Add corresponding menus and interaction logic to the CLI
3. Connect new features with the existing system

### Supported File Formats
- XML: For saving complete novel data, including characters, events, chapters, and all other elements
- TXT: For exporting novels in readable plain text format


## System Directory Structure
```
novel_generator/
├── config/                  # Configuration files
│   └── prompts.py           # Prompt configurations
├── core/                    # Core modules
│   ├── models.py            # Data models
│   ├── llm_interface.py     # LLM interface
│   ├── event_engine.py      # Event engine
│   └── narrative_generator.py # Narrative generator
├── middleware/              # Middleware
│   ├── character_manager.py # Character management
│   ├── event_manager.py     # Event management
│   ├── outline_manager.py   # Outline management
│   ├── chapter_manager.py   # Chapter management
│   └── context_manager.py   # Context management
├── utils/                   # Utility functions
│   ├── xml_utils.py         # XML processing
│   ├── file_utils.py        # File operations
│   └── logger.py            # Logging
├── ui/                      # User interface
│   └── cli.py               # Command line interface
├── main.py                  # Main program entry
└── README.md                # Documentation
```

## Notes
The quality and consistency of generated content depends on the LLM model used
GPT-4 model is used by default, can be changed in settings
Generating chapters may take a considerable amount of time, please be patient
It is recommended to save your work regularly to prevent data loss due to unexpected situations
