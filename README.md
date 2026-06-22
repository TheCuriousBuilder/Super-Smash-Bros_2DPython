# Python Smash

Python Smash is a 2D platform fighting game I made in Python using Pygame. It's inspired by platform fighters like Super Smash Bros., with percentage-based knockback, multiple stages, unique characters, AI opponents, and local multiplayer.

I started this project to see how much of a fighting game I could build from scratch in Python while learning more about physics, game loops, AI, and combat systems.

## Features

### Game Modes

* VS AI
* Local 2-Player (same keyboard)

### Difficulty Levels

* Easy
* Medium
* Hard

The AI gets faster, more aggressive, and better at defending itself as the difficulty increases.

## Fighters

Every character has an ability and a drawback.

### Blaze

* +30% movement speed
* Takes extra knockback

### Titan

* Harder to launch
* Slower movement and lower jumps

### Volt

* Special attacks recharge twice as fast
* Weaker basic attacks

### Ace

* One extra air jump
* Lower shield health

### Hook

* Longer grab range
* Slower shield regeneration

### Nova

* Rage builds faster, increasing knockback at high percentages
* Longer special cooldowns

## Stages

### Battlefield

Three-platform stage inspired by classic platform fighters.

### Final Stage

A simple flat stage.

### Sky Arena

Features a moving platform that changes positioning during the match.

## Combat Mechanics

* Percentage-based damage and knockback
* Basic attacks
* Projectile specials
* Grabs
* Shields
* Spot dodges
* Air jumps
* Fast falling
* Ledge grabbing
* Rage mechanic
* Hit pause
* Screen shake
* Combo tracking and end-of-game statistics

## Controls

### Player 1

* A/D – Move
* W – Jump
* S – Fast Fall
* J – Attack
* K – Special
* L – Shield
* I – Grab

### Player 2

* ←/→ – Move
* ↑ – Jump
* ↓ – Fast Fall
* . – Attack
* / – Special
* Right Shift – Shield
* Right Ctrl – Grab

## Installation

Install the required libraries:

```bash
pip install pygame numpy
```

NumPy is optional. The game still runs without it, but sound effects will be disabled.

## Running the Game

```bash
python PythonSmash.py
```

## What I Learned

This project taught me a lot about:

* Object-oriented programming
* Physics and collision detection
* AI behavior
* Particle effects and screen shake
* Game balancing
* Building larger projects in Pygame

The hardest parts were getting knockback to feel right, handling platform collisions, and making the AI recover consistently.

## Future Ideas

* More fighters with unique movesets
* Stage hazards
* More attacks and combo options
* Better AI
* Additional stages
* Music and more sound effects
* Online multiplayer

## Built With

* Python
* Pygame
* NumPy (optional)

Made by **TheCuriousBuilder** as a personal project and a way to learn game development by building a platform fighter completely from scratch.
