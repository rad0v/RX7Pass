# RX7Pass

## _All In One Secure Password Management_

## Features

RX7Pass is a lightweight CLI-based password manager designed for users who value security, simplicity, and control over their credentials.

It stores all passwords encrypted at rest, protected by a single master password, and avoids unnecessary complexity or cloud dependencies. RX7Pass is intended to be fast, transparent, and easy to extend.

This project was built to understand and implement:

- Secure password handling
- Encryption best practices
- Clean CLI UX
- Practical security-focused design

## Targeted Users
RX7Pass is best suited for:

- Developers and engineers who prefer CLI tools
- Security-conscious users who want local-only storage
- Learners exploring cryptography and secure systems
- Anyone who wants a simple, offline password vault

It is not intended to replace full-featured GUI password managers, but rather to serve as a reliable, minimal alternative or learning project.

## Versions
I have created two branches for RX7Pass: 
- Firstly the `base` branch that is raw implementation, no UI-UX is implemented. This is good for you if you want to learn more about this tool, and the basic functionality. 
- Second is the `uiux-added` branch that is more user friendly to use, with better visibility of the data. This version is good for you if you are only interested in using the program and not look at the inner workings.
- See demo below for better visualization. 

## Installation Guide

Requirements:
- Python 3.10+
- pip
- Virtual environment ( I would personally recommend you to use a virtual env and install dependencies there)

Installation:
```
git clone https://github.com/yourusername/RX7Pass.git
cd RX7Pass
pip install -r requirements.txt
python main.py
```

Dependencies:
- `cryptography`
- `rich` (for uiux-added version)
- `pyperclip`

## Features 
Core Features: 
- Master password authentication
- Secure password hashing with salt
- AES-based encryption for stored credentials
- Add, view, list, and delete entries
- Notes support per entry
- Password generator with configurable options
- Clipboard copy with automatic clearing
- Clean, readable CLI interface using rich

## Demo 
### Base Version 
1. Menu 
<img width="354" height="281" alt="base-menu" src="https://github.com/user-attachments/assets/06df3040-7169-496d-913e-7c8ba177632c" />

2. Viewing Entries 
<img width="359" height="291" alt="base-entries" src="https://github.com/user-attachments/assets/acd98f5d-579f-4e3d-959f-da08c889e3df" />

3. Generating Passwords
<img width="368" height="380" alt="base-pw-gen" src="https://github.com/user-attachments/assets/42e148fe-9f6b-47c6-ad11-2b483705f2e3" />

### Improved Version 
1. Menu 
<img width="1432" height="467" alt="uiux-menu" src="https://github.com/user-attachments/assets/543b0154-89e7-4c6a-b468-3bfcaf419ad7" />

2. Viewing Entries 
<img width="1438" height="421" alt="uiux-entries" src="https://github.com/user-attachments/assets/db5cef01-f2d3-4e51-9852-f010788f284b" />

3. Generating Passwords
<img width="1430" height="413" alt="uiux-pw-gen" src="https://github.com/user-attachments/assets/b3fbc40d-2abc-4d15-a879-bc0174393fc3" />

Please Note: These are only gist of the program not the whole program. 

## Contributing 
Contributions are welcome.

If you’d like to contribute:
- Fork the repository
- Create a feature or fix branch
- Keep changes focused and well-documented
- Submit a pull request

Suggestions, bug reports, and improvements to UI, security, or documentation are appreciated.
