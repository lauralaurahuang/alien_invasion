import pygame

class Settings():
    """A class to store all the settings for Alien Invasion."""
    
    def __init__(self):
        """Initializing the game's static settings."""
        # Screen settings
        
        self.full_screen = False
 
        self.screen =  pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            
 
        self.bg_color = (230, 230, 230)
        # Ship settings
        
        self.bullet_width = 3
        self.bullet_height = 15
        self.bullet_color = (60, 60, 60)
        self.bullets_allowed = 3
        
        self.fleet_drop_speed = 10
        
        self.ship_limit = 3
        
        # How quickly the game speeds up.
        self.speedup_scale = 1.1
        self.score_scale = 1.5
        self.initialize_dynamic_setting()
        
    # def resize(self):    
    #     if self.full_screen:
    #         self.screen =  pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            
    #     else:
    #         self.screen_width = 1200
    #         self.screen_height = 800
    #         self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        
    def initialize_dynamic_setting(self):
        """Initialize settings that change throught the game."""
        self.ship_speed = 1.5
        self.bullet_speed = 1.5
        self.alien_speed = 1.0
        
        # Fleet_direction of 1 represent right, -1 represent left.
        self.fleet_direction = 1
        # Scoring.
        self.alien_points = 50
        
    def increase_speed(self):
        """increase speed setttings"""
        self.ship_speed *= self.speedup_scale
        self.bullet_speed *= self.speedup_scale
        self.alien_speed *= self.speedup_scale
        self.alien_points = int(self.alien_points * self.score_scale)