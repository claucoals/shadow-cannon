# Shadow Cannon

**Shadow Cannon** is a strategic game based on physics and precision, developed in Python using the Kivy framework. The game was created by **Claudia Maria Carboni** and **Susanna Mazzocchi** as a project for the Programming course, BSc in Artificial Intelligence.

## Game Description

As the last Master of the Shadow Cannon, the player must navigate through four thematic levels, each with unique gameplay mechanics and obstacles. The goal is to hit the target using different types of projectiles, overcoming obstacles, and leveraging the laws of physics to complete the levels as quickly as possible.

### Levels:
1. **Hell**: Introduction to basic mechanics with parabolic projectiles and destructible obstacles.
2. **Abyss**: Introduction of the shotgun and bats, requiring different strategies.
3. **Cursed Lands**: Introduction of the laser and mirrors, which reflect the projectile.
4. **Space**: Final level with two types of lasers and asteroids to destroy.

## Key Features

- **Four levels** with progressive difficulty.
- **Three types of projectiles**: Bomb, Shotgun, and Laser.
- **Collision system** based on bounding boxes.
- **Hall of Fame** to store the best completion times.
- **Intuitive user interface** with visual and audio feedback.
- **Thematic background music** for each section of the game.

## System Requirements

- **Python 3.12.0**
- **Kivy 2.3.1**
- **Operating System**: Windows, macOS, Linux

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/shadow-cannon.git
   ```
2. Navigate to the project directory:
   ```bash
   cd shadow-cannon
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the game:
   ```bash
   python main.py
   ```

## Code Structure

- **`main.py`**: Contains the main game logic and screen management.
- **`menu.kv`**, **`Level1Game.kv`**, etc.: KV files for defining the graphical interface.
- **`images/`**: Directory containing the images used in the game.
- **`sounds/`**: Directory containing the background music and sound effects.

## Potential Improvements

- Implementation of more realistic physics (air resistance, friction, etc.).
- Multiplayer mode for two players.
- Adaptation for mobile devices and different operating systems.
- Addition of new worlds and themes to increase game variety.

## Acknowledgements

- **ChatGPT 4**: For suggestions and improvements during development.
- **DALL-E**: For creating backgrounds and objects.
- **Sumo AI**: For creating the soundtracks.

## License

This project is released under the MIT License. For more details, see the LICENSE file.

## Copyright and Copying

All content in this repository, including code, images, and sounds, is protected by copyright laws. Unauthorized copying, distribution, or modification of any part of this project is strictly prohibited. If you wish to use any part of this project, please contact the authors for permission.

---

**Enjoy playing Shadow Cannon!** 🎮
